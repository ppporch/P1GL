"""Run both pytest-style functions and unittest cases in the original archive."""
import runpy,unittest
from pathlib import Path
n=0
for p in sorted((Path(__file__).resolve().parents[1]/'tests').glob('test_*.py')):
    ns=runpy.run_path(str(p))
    for name,fn in ns.items():
        if name.startswith('test_') and callable(fn): fn();n+=1
suite=unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parents[1]/'tests'))
result=unittest.TextTestRunner(verbosity=1).run(suite)
assert result.wasSuccessful()
print(f'PASS: {n} function tests and {result.testsRun} unittest cases')
