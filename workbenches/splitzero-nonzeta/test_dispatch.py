"""Queue regression checks, including fail-closed mutations in temporary copies."""
from pathlib import Path
from unittest import TestCase,main
from unittest.mock import patch
import json,shutil,tempfile
import dispatch

class DispatchTests(TestCase):
    def test_counts(self):
        rows,jobs,s=dispatch.build()
        self.assertEqual((len(rows),len(jobs),s['ready_intake_jobs']),(56,251,70))
    def test_resolution_routing(self):
        rows,jobs,_=dispatch.build()
        self.assertEqual(next(r for r in rows if r['id']=='P14')['status'],'RESOLVED_PUBLISHED')
        for p in ['P14','AIM-C14','AIM-E36','AIM-ZC2N']:
            self.assertEqual([j['role'] for j in jobs if j['problem_id']==p],['CS','CE'])
    def test_claims_remain_review(self):
        _,jobs,_=dispatch.build()
        for p in ['P04','P06']:
            self.assertEqual([j['role'] for j in jobs if j['problem_id']==p],['AS','AP','AR'])
            self.assertTrue(all(j['source_status']=='CLAIMED_UNVERIFIED' for j in jobs if j['problem_id']==p))
    def test_prior_work_attached(self):
        _,jobs,_=dispatch.build()
        for p in ['P07','P15','P16','P17','P18','P19','G92-DECK','AIM-S21']:
            for j in jobs:
                if j['problem_id']==p:
                    self.assertIsNotNone(j['prior_work'])
                    self.assertEqual(j['mathematical_entry'],j['prior_work']['next'])
    def test_no_automatic_dispatch(self):
        _,jobs,_=dispatch.build()
        self.assertTrue(all(not j['dispatch_authorized'] for j in jobs))
    def test_baseline_drift_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp)
            for f in ['intake.json','seeds.psv']:
                shutil.copyfile(dispatch.ROOT/f,r/f)
            shutil.copytree(dispatch.ROOT/'review/catalog',r/'review/catalog')
            with (r/'seeds.psv').open('a') as stream:stream.write('\n')
            with patch.object(dispatch,'ROOT',r):
                with self.assertRaisesRegex(ValueError,'Baseline seed drift'):dispatch.build()
    def test_orphan_delta_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp)
            for f in ['intake.json','seeds.psv']:shutil.copyfile(dispatch.ROOT/f,r/f)
            shutil.copytree(dispatch.ROOT/'review/catalog',r/'review/catalog')
            p=r/'review/catalog/progress.json';d=json.loads(p.read_text());d['missing']={};p.write_text(json.dumps(d))
            with patch.object(dispatch,'ROOT',r):
                with self.assertRaisesRegex(ValueError,'Orphan prior-work'):dispatch.build()
if __name__=='__main__':main(verbosity=2)
