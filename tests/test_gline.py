import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reference'))
from gline import line_points


def test_all_octants():
    origin = (512, 512)
    deltas = [(9, 3), (3, 9), (-3, 9), (-9, 3),
              (-9, -3), (-3, -9), (3, -9), (9, -3)]
    for dx, dy in deltas:
        dest = (origin[0] + dx, origin[1] + dy)
        pts = line_points(*origin, *dest)
        assert pts[0] == origin and pts[-1] == dest
        assert len(pts) == max(abs(dx), abs(dy)) + 1
        assert all(abs(b[0]-a[0]) <= 1 and abs(b[1]-a[1]) <= 1
                   for a,b in zip(pts, pts[1:]))
        assert pts == list(reversed(line_points(*dest, *origin)))


def test_axes_and_diagonal():
    assert line_points(0, 0, 3, 0) == [(0,0),(1,0),(2,0),(3,0)]
    assert line_points(0, 0, 0, 3) == [(0,0),(0,1),(0,2),(0,3)]
    assert line_points(0, 0, 3, 3) == [(0,0),(1,1),(2,2),(3,3)]


def test_point_and_bounds():
    assert line_points(1023,1023,1023,1023) == [(1023,1023)]
    for args in [(-1,0,2,2),(0,0,1024,0),(1.5,0,2,2),(True,0,2,2)]:
        try:
            line_points(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Expected invalid coordinates: {args}')


def test_every_point_inside_and_no_duplicates():
    for a in [(0,1023,1023,0),(0,0,1023,1023),(15,991,1001,12),
              (300,700,301,700),(100,100,100,100)]:
        pts = line_points(*a)
        assert len(pts) == len(set(pts))
        assert all(0 <= x <= 1023 and 0 <= y <= 1023 for x,y in pts)
