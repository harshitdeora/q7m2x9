"""Download the reproducible Elexon pilot snapshot. No fabricated data."""
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://data.elexon.co.uk/bmrs/api/v1/datasets/'

def fetch(task):
    dataset, day = task
    if dataset == 'WINDFOR':
        end = day + dt.timedelta(days=1)
        query = f'publishDateTimeFrom={day}T00:00:00Z&publishDateTimeTo={end}T00:00:00Z'
    else:
        query = f'settlementDateFrom={day}&settlementDateTo={day}&fuelType=WIND'
    url = BASE + dataset + '/stream?' + query
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                records = json.load(response)
            if not isinstance(records, list):
                raise ValueError('Expected a list of records')
            print(dataset, day, len(records), flush=True)
            return dataset, records, url
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def main():
    tasks = [('WINDFOR', dt.date(2025, 12, 30) + dt.timedelta(days=i)) for i in range(33)]
    tasks += [('FUELHH', dt.date(2026, 1, 2) + dt.timedelta(days=i)) for i in range(31)]
    data = {'WINDFOR': {}, 'FUELHH': {}}
    sources = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for dataset, records, url in pool.map(fetch, tasks):
            sources.append(url)
            for record in records:
                if dataset == 'FUELHH' and record.get('fuelType') != 'WIND':
                    continue
                key = (record['startTime'], record['publishTime'])
                data[dataset][key] = {k: record[k] for k in ['startTime', 'publishTime', 'generation']}
    snapshot = {k: sorted(v.values(), key=lambda r: (r['startTime'], r['publishTime'])) for k, v in data.items()}
    output = ROOT / 'data'
    output.mkdir(exist_ok=True)
    raw = json.dumps(snapshot, separators=(',', ':')).encode()
    (output / 'elexon.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    manifest = {'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'sha256_uncompressed': hashlib.sha256(raw).hexdigest(),
                'records': {k: len(v) for k,v in snapshot.items()}, 'sources': sources,
                'decision_dates': ['2026-01-01', '2026-01-31'],
                'delivery_dates': ['2026-01-02', '2026-02-01']}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: v for k,v in manifest.items() if k != 'sources'}), flush=True)

if __name__ == '__main__':
    main()
