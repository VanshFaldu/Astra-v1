import csv
import io
import unittest
from ml import fit_csv, evaluate
from analyzer import FEATURES

class TrainingTests(unittest.TestCase):
    def dataset(self):
        output=io.StringIO(); writer=csv.DictWriter(output,fieldnames=FEATURES+['repository','label','review_rationale'])
        writer.writeheader()
        for group in range(5):
            for i in range(8):
                writer.writerow({**dict.fromkeys(FEATURES,1),'loc':5+i*10,'repository':f'fixture-{group}','label':int(i>=4),'review_rationale':'Synthetic test fixture, not research data'})
        return output.getvalue()
    def test_group_split_and_variants(self):
        model=fit_csv(self.dataset()); evaluation=model['evaluation']
        self.assertEqual(evaluation['train_samples'],32)
        self.assertEqual(evaluation['test_samples'],8)
        self.assertEqual(len(evaluation['held_out_repositories']),1)
        self.assertEqual(set(evaluation['variants']),{'rules','ml','hybrid'})
    def test_missing_columns(self):
        with self.assertRaisesRegex(ValueError,'Missing columns'): fit_csv('label\n1\n')
    def test_invalid_metric(self):
        with self.assertRaisesRegex(ValueError,'Invalid row'): fit_csv(self.dataset().replace('5,','nan,',1))
    def test_metrics(self):
        result=evaluate([0,0,1,1],[False,True,False,True])
        self.assertEqual(result['confusion_matrix'],[[1,1],[1,1]])
        self.assertEqual(result['f1'],.5)
