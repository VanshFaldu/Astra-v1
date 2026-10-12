import unittest
import ast
from analyzer import analyze, metrics
from ml import train, predict

class AnalysisTests(unittest.TestCase):
    def test_strings_not_branches(self):
        r=analyze('def f():\n    return "if for while"\n')
        self.assertEqual(r['functions'][0]['complexity'],1)
    def test_scope_isolation(self):
        r=analyze('def outer():\n    def inner():\n        if True:\n            return 1\n    return inner()\n')
        self.assertEqual([f['complexity'] for f in r['functions']],[1,2])
    def test_unused_closure_read(self):
        r=analyze('def f():\n    x = 3\n    def g():\n        return x\n    return g\n')
        self.assertFalse(any(f['type']=='Unused local' for f in r['findings']))
    def test_parameters_and_nesting(self):
        r=analyze('async def f(a, /, b, *args, c=1, **kwargs):\n    if a:\n        for x in b:\n            while c:\n                if x:\n                    return x\n')
        self.assertEqual(r['functions'][0]['parameters'],5)
        self.assertEqual(r['functions'][0]['nesting'],4)
    def test_boolean_complexity(self):
        r=analyze('def f(a,b,c):\n    if a and b or c:\n        return 1\n')
        self.assertEqual(r['functions'][0]['complexity'],4)
    def test_duplicate_ignores_formatting(self):
        r=analyze('def a(x):\n    y=x+1\n    z=y+1\n    return z\ndef b(x):\n    y = x + 1\n    z = y + 1\n    return z\n')
        self.assertTrue(any(f['type']=='Duplicate implementation' for f in r['findings']))
    def test_invalid_syntax(self):
        with self.assertRaises(SyntaxError): analyze('def invalid(')
    def test_no_execution(self):
        self.assertEqual(analyze('raise RuntimeError("never run")')['summary']['findings'],0)
    def test_tree_learns_signal(self):
        rows=[dict(loc=i,statements=1,parameters=1,nesting=1,complexity=1,calls=1,loops=0,branches=0,label=int(i>=10)) for i in range(20)]
        t=train(rows)
        self.assertLess(predict(t,rows[0]),.5)
        self.assertGreaterEqual(predict(t,rows[-1]),.5)
if __name__=='__main__': unittest.main()
