import importlib.util
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('circuit',ROOT/'scripts/render_circuit.py')
circuit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(circuit)


class CircuitTests(unittest.TestCase):
    def test_every_real_day_is_mapped_once_with_unchanged_counts(self):
        data=json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8'))
        _, mapping=circuit.draw_board(data)
        self.assertEqual(len(mapping),len(data['days']))
        self.assertEqual(sum(day['count'] for day in mapping),data['total'])
        self.assertEqual([{k:d[k] for k in ('date','count','level')} for d in mapping],data['days'])
        self.assertEqual(len({(d['column'],d['lane']) for d in mapping}),len(mapping))

    def test_lap_is_continuous_and_tiles_stay_in_frame(self):
        start=circuit.pose(0)
        end=circuit.pose(circuit.LENGTH-.01)
        self.assertLess(math.dist(start[:2],end[:2]),.02)
        self.assertLess(abs(start[2]-end[2]),.03)
        for distance in range(math.ceil(circuit.LENGTH)):
            for offset in (-36,36):
                x,y,_=circuit.pose(distance,offset)
                self.assertTrue(0<x<circuit.W and 75<y<520)

    def test_missing_or_duplicate_dates_cannot_become_fake_activity(self):
        data=json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8'))
        data['days'][5]['date']=data['days'][4]['date']
        with self.assertRaises(ValueError):
            circuit.validate(data)
        with self.assertRaises(ValueError):
            circuit.parse_calendar('<html>Unavailable</html>')


if __name__=='__main__':
    unittest.main()
