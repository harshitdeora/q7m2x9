"""Pure, auditable as-of selection and hourly verification."""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

@lru_cache(maxsize=1)
def load_data():
    with gzip.open(ROOT / 'data/elexon.json.gz', 'rt') as stream:
        source = json.load(stream)
    forecasts = {}
    actuals = {}
    for row in source['WINDFOR']:
        forecasts.setdefault(timestamp(row['startTime']), []).append(row)
    for row in source['FUELHH']:
        start = timestamp(row['startTime'])
        if start not in actuals or row['publishTime'] > actuals[start]['publishTime']:
            actuals[start] = row
    return forecasts, actuals

def metrics(rows):
    pairs = [r for r in rows if r['forecast'] is not None and r['actual'] is not None]
    errors = [r['forecast'] - r['actual'] for r in pairs]
    if not errors:
        return {'count': 0, 'mae': None, 'rmse': None, 'bias': None, 'p90_absolute_error': None}
    absolute = sorted(abs(e) for e in errors)
    return {'count': len(errors), 'mae': sum(absolute) / len(errors),
            'rmse': math.sqrt(sum(e * e for e in errors) / len(errors)),
            'bias': sum(errors) / len(errors),
            'p90_absolute_error': absolute[max(0, math.ceil(.9 * len(absolute)) - 1)]}

def decision(day, cutoff, forecasts=None, actuals=None):
    if forecasts is None or actuals is None:
        forecasts, actuals = load_data()
    as_of = datetime.fromisoformat(f'{day}T{cutoff}:00+00:00')
    delivery = (as_of + timedelta(days=1)).replace(hour=0, minute=0, second=0)
    rows = []
    for hour in range(24):
        target = delivery + timedelta(hours=hour)
        eligible = [r for r in forecasts.get(target, []) if timestamp(r['publishTime']) <= as_of]
        selected = max(eligible, key=lambda r: timestamp(r['publishTime'])) if eligible else None
        halves = [actuals.get(target + timedelta(minutes=offset)) for offset in (0, 30)]
        actual = sum(r['generation'] for r in halves) / 2 if all(r is not None for r in halves) else None
        forecast = selected['generation'] if selected else None
        rows.append({'startTime': target.isoformat(), 'hour': hour,
                     'forecast': forecast, 'actual': actual,
                     'error': forecast - actual if forecast is not None and actual is not None else None,
                     'publishTime': selected['publishTime'] if selected else None,
                     'ageHours': (as_of - timestamp(selected['publishTime'])).total_seconds() / 3600 if selected else None,
                     'actualHalfHours': sum(r is not None for r in halves)})
    available = [r for r in rows if r['forecast'] is not None]
    matched = [r for r in rows if r['error'] is not None]
    return {'decisionDate': day, 'cutoff': cutoff, 'asOf': as_of.isoformat(),
            'deliveryDate': delivery.date().isoformat(), 'rows': rows, 'metrics': metrics(rows),
            'coverage': len(available), 'expected': 24,
            'forecastEnergyMWh': sum(r['forecast'] for r in available) if available else None,
            'meanForecastMW': sum(r['forecast'] for r in available) / len(available) if available else None,
            'latestPublication': max((r['publishTime'] for r in available), default=None),
            'oldestAgeHours': max((r['ageHours'] for r in available), default=None),
            'peak': max(available, key=lambda r: r['forecast']) if available else None,
            'largestError': max(matched, key=lambda r: abs(r['error'])) if matched else None}

@lru_cache(maxsize=48)
def month(cutoff):
    days = [decision(f'2026-01-{i:02d}', cutoff) for i in range(1, 32)]
    rows = [row for d in days for row in d['rows']]
    hourly = [{'hour': h, **metrics([r for r in rows if r['hour'] == h])} for h in range(24)]
    return {'metrics': metrics(rows), 'days': [{'decisionDate': d['decisionDate'],
            'deliveryDate': d['deliveryDate'], 'coverage': d['coverage'], **d['metrics']} for d in days],
            'hourly': hourly, 'expected': 744,
            'forecastCoverage': sum(r['forecast'] is not None for r in rows)}
