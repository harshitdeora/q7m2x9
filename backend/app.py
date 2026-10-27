from datetime import date, time
import csv
import io
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from .analysis import decision, month, ROOT

app = FastAPI(title='Aeris Wind Intelligence', version='1.0.0', docs_url='/api/docs', openapi_url='/api/openapi.json')

def validate(day, cutoff):
    if day < date(2026, 1, 1) or day > date(2026, 1, 31):
        raise HTTPException(422, 'Decision date must be in January 2026.')
    if cutoff.second or cutoff.microsecond or cutoff.tzinfo:
        raise HTTPException(422, 'Use an unzoned HH:MM decision time in Europe/London (GMT in January).')
    return day.isoformat(), cutoff.strftime('%H:%M')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'source': 'Elexon historical snapshot'}

@app.get('/api/decision')
def get_decision(day: date = date(2026, 1, 15), cutoff: time = time(10)):
    day_text, cutoff_text = validate(day, cutoff)
    return decision(day_text, cutoff_text)

@app.get('/api/accuracy')
def accuracy(cutoff: time = time(10)):
    _, cutoff_text = validate(date(2026, 1, 1), cutoff)
    return month(cutoff_text)

@app.get('/api/provenance')
def provenance():
    return json.loads((ROOT / 'data/manifest.json').read_text())

@app.get('/api/export')
def export(day: date = date(2026, 1, 15), cutoff: time = time(10)):
    day_text, cutoff_text = validate(day, cutoff)
    rows = decision(day_text, cutoff_text)['rows']
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['startTime', 'forecast', 'actual', 'error', 'publishTime', 'ageHours', 'actualHalfHours'])
    writer.writeheader()
    writer.writerows({k: r[k] for k in writer.fieldnames} for r in rows)
    return Response(output.getvalue(), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename="aeris-{day_text}-{cutoff_text.replace(":", "")}.csv"'})

# Docker serves the same built React application through Python.
if (ROOT / 'dist').exists():
    app.mount('/', StaticFiles(directory=ROOT / 'dist', html=True), name='frontend')
