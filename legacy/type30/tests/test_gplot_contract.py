"""Static linkage smoke checks; executed coordinate tests are in tools/check_cpu.py."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TestGPlotContract(unittest.TestCase):
    def test_inline_argument_pointer_advanced_twice(self):
        source = (ROOT / 'src/gplot.am1').read_text().lower()
        self.assertEqual(source.count('idx gp_ret'), 2)
        self.assertIn('jmp i gp_ret', source)
        self.assertIn('lio gp_y', source)
        self.assertIn('lac gp_x', source)

    def test_demo_uses_five_calls(self):
        source = (ROOT / 'examples/gplot_demo.am1').read_text().lower()
        self.assertEqual(source.count('jda gplot'), 5)

if __name__ == '__main__':
    unittest.main()
