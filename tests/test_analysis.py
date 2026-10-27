import gzip
import hashlib
import json
import math
import unittest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.analysis import ROOT, decision, metrics, month, load_data, timestamp
from backend.app import app

class AnalysisTests(unittest.TestCase):
    def test_only_latest_forecast_known_at_cutoff_is_used(self):
        start = datetime(2026, 1, 16, tzinfo=timezone.utc)
        forecasts = {start: [
            {'publishTime': '2026-01-15T09:00:00Z', 'generation': 100},
            {'publishTime': '2026-01-15T10:00:00Z', 'generation': 150},
            {'publishTime': '2026-01-15T10:00:01Z', 'generation': 999},
        ]}
        result = decision('2026-01-15', '10:00', forecasts, {})
        self.assertEqual(result['rows'][0]['forecast'], 150)
        self.assertIsNone(result['rows'][1]['forecast'])
        self.assertEqual(result['coverage'], 1)

    def test_actuals_require_both_halves_and_preserve_zero(self):
        start = datetime(2026, 1, 16, tzinfo=timezone.utc)
        forecasts = {start: [{'publishTime': '2026-01-15T09:00:00Z', 'generation': 100}]}
        actuals = {start: {'generation': 0}, start + timedelta(minutes=30): {'generation': 200}}
        result = decision('2026-01-15', '10:00', forecasts, actuals)
        self.assertEqual(result['rows'][0]['actual'], 100)
        self.assertEqual(result['metrics']['mae'], 0)
        del actuals[start]
        self.assertIsNone(decision('2026-01-15', '10:00', forecasts, actuals)['rows'][0]['actual'])

    def test_metric_definitions_and_missing_pairs(self):
        result = metrics([{'forecast': 100, 'actual': 80}, {'forecast': 60, 'actual': 100}, {'forecast': None, 'actual': 90}])
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['mae'], 30)
        self.assertEqual(result['bias'], -10)
        self.assertAlmostEqual(result['rmse'], math.sqrt(1000))
        self.assertEqual(result['p90_absolute_error'], 40)
        self.assertIsNone(metrics([])['mae'])

    def test_january_31_decision_covers_february_1(self):
        result = decision('2026-01-31', '10:00')
        self.assertEqual(result['deliveryDate'], '2026-02-01')
        self.assertEqual(result['metrics']['count'], 24)

    def test_snapshot_checksum_and_dataset_contract(self):
        manifest = json.loads((ROOT / 'data/manifest.json').read_text())
        raw = gzip.decompress((ROOT / 'data/elexon.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest['sha256_uncompressed'])
        forecasts, actuals = load_data()
        self.assertTrue(all(k.minute == 0 for k in forecasts))
        self.assertEqual(len(actuals), 31 * 48)

    def test_entire_snapshot_has_no_future_leakage(self):
        for cutoff in ['00:00', '10:00', '23:30']:
            for i in range(1, 32):
                result = decision(f'2026-01-{i:02d}', cutoff)
                for r in result['rows']:
                    if r['publishTime']:
                        self.assertLessEqual(timestamp(r['publishTime']), timestamp(result['asOf']))

    def test_month_metrics_are_weighted_by_observation(self):
        result = month('10:00')
        self.assertEqual(result['expected'], 744)
        self.assertEqual(result['metrics']['count'], 744)
        self.assertAlmostEqual(result['metrics']['mae'], sum(d['mae'] * d['count'] for d in result['days']) / 744)

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_decision_and_csv(self):
        result = self.client.get('/api/decision?day=2026-01-15&cutoff=10:00')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()['rows']), 24)
        csv = self.client.get('/api/export?day=2026-01-15&cutoff=10:00')
        self.assertEqual(len(csv.text.splitlines()), 25)
        self.assertIn('publishTime', csv.text)
        self.assertIn('attachment;', csv.headers['content-disposition'])

    def test_invalid_inputs(self):
        for query in ['day=2026-02-01', 'day=garbage', 'cutoff=25:00', 'cutoff=10:00:30', 'cutoff=10:00Z']:
            self.assertEqual(self.client.get('/api/decision?' + query).status_code, 422, query)

    def test_provenance_and_health(self):
        self.assertEqual(self.client.get('/api/health').json()['status'], 'ok')
        self.assertEqual(len(self.client.get('/api/provenance').json()['sources']), 64)

if __name__ == '__main__':
    unittest.main()
