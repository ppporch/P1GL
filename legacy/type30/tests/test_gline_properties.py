"""Extended regression tests for P1GL's host-side Bresenham reference."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reference'))
from gline import line_points


def test_all_octants_and_reversal():
    center = (512, 512)
    offsets = [(23, 5), (5, 23), (-5, 23), (-23, 5),
               (-23, -5), (-5, -23), (5, -23), (23, -5)]
    for dx, dy in offsets:
        end = (center[0] + dx, center[1] + dy)
        forward = line_points(*center, *end)
        backward = line_points(*end, *center)
        assert forward == list(reversed(backward)), (dx, dy)
        assert len(forward) == max(abs(dx), abs(dy)) + 1
        assert all(max(abs(x2-x1), abs(y2-y1)) == 1
                   for (x1, y1), (x2, y2) in zip(forward, forward[1:]))


def test_display_boundaries_and_long_diagonals():
    cases = [(0, 0, 1023, 1023), (1023, 0, 0, 1023),
             (0, 512, 1023, 512), (512, 0, 512, 1023)]
    for x0, y0, x1, y1 in cases:
        pts = line_points(x0, y0, x1, y1)
        assert pts[0] == (x0, y0)
        assert pts[-1] == (x1, y1)
        assert len(pts) == 1024
        assert all(0 <= x <= 1023 and 0 <= y <= 1023 for x, y in pts)


def test_error_against_ideal_line():
    for x0, y0, x1, y1 in [(20, 40, 100, 71), (300, 40, 320, 200),
                            (900, 800, 100, 400), (100, 900, 800, 100)]:
        points = line_points(x0, y0, x1, y1)
        dx, dy = x1-x0, y1-y0
        # Perpendicular distance in pixels from each plotted pixel to ideal line
        for x, y in points:
            numerator = abs(dy*(x-x0) - dx*(y-y0))
            denominator = (dx*dx + dy*dy)**0.5
            assert numerator / denominator <= 0.71
