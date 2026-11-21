"""Check the actual PDP-1 curve and clipping display lists."""
import math
import random

from check_transform import execute, rect
from check_viewport import call, clipping
from type340_model import decode


def vertex(cx, cy, rx, ry, angle):
    radians = math.tau * (angle % 256) / 256
    return (cx + (rx * round(1024 * math.cos(radians)) + 512) // 1024,
            cy + (ry * round(1024 * math.sin(radians)) + 512) // 1024)


def reference(viewport, curve):
    cx, cy, rx, ry, start, sweep, step = curve
    distances = list(range(0, abs(sweep), step)) + [abs(sweep)]
    direction = -1 if sweep < 0 else 1
    points = [vertex(cx, cy, rx, ry, start + direction * d) for d in distances]
    edges = [(a, b) for a, b in zip(points, points[1:]) if a != b]
    if not edges:
        edges = [(points[0], points[0])]
    return [edge for a, b in edges if (edge := clipping(viewport, (*a, *b))) is not None]


def check_commands(display, expected):
    assert display['points'] == [a for a, _ in expected]
    vectors = iter(display['vectors'])
    for start, end in expected:
        if start == end:
            continue
        cursor = start
        while cursor != end:
            a, b = next(vectors)
            assert a == cursor
            cursor = b
    assert next(vectors, None) is None


def run(cases):
    source = ['Curve CPU test\n100/\ngo, lem\nlsm\ncbs\n']
    for viewport, entry, args, curve in cases:
        source += [call('gview_set', viewport), 'jda gframe_begin\nscene; 0d1700\n',
                   call(entry, args), 'jsp gframe_end\njsp gframe_refresh\n']
    source += ['hlt\n']
    for module in ('gplot', 'gline', 'gframe', 'gview', 'gtransform', 'garc'):
        source.append(f'#include "../src/{module}.am1"\n')
    source.append('constants\nscene,\ntable 0d1700,0\nguard,0123456\nstart go\n')
    out, sy, lists = execute(''.join(source))
    assert len(lists) == len(cases)
    assert out[sy['guard']] == 0o123456
    for words, (viewport, entry, args, curve) in zip(lists, cases):
        try:
            check_commands(decode(words), reference(viewport, curve))
        except (AssertionError, StopIteration) as error:
            raise AssertionError((viewport, entry, args, decode(words))) from error


def main():
    screen = (0, 0, 1023, 1023)
    cases = [
        (screen, 'gcircle_vector', (512, 512, 220, 1), (512, 512, 220, 220, 0, 256, 1)),
        (screen, 'gellipse_vector', (512, 512, 300, 100, 7), (512, 512, 300, 100, 0, 256, 7)),
    ]
    arcs = [(512, 512, 100, 70, 252, 19, 8), (512, 512, 100, 70, 4, -19, 8),
            (512, 512, 300, 100, 33, -256, 7), (512, 512, 0, 0, 45, 256, 1),
            (-20, 400, 280, 70, 0, 224, 9), (-700, 400, 280, 70, 0, 256, 8),
            (512, 512, 0, 222, 0, 256, 16), (512, 512, 50, 75, 32, 0, 1),
            (512, 512, 1, 1, 97, 256, 1), (1023, -1023, 1023, 1023, 0, 256, 64)]
    cases += [(rect, 'garc', curve, curve) for curve in arcs]
    rng = random.Random(340)
    for _ in range(48):
        curve = (rng.randint(-200, 1023), rng.randint(-200, 1023),
                 rng.randrange(401), rng.randrange(401), rng.randrange(256),
                 rng.randint(-256, 256), rng.randint(5, 64))
        cases.append((rect, 'garc', curve, curve))
    for start in range(0, len(cases), 8):
        run(cases[start:start + 8])
    print(f'{len(cases)} curve cases matched the reference geometry.')
    from check_transform import root
    _, _, lists = execute((root / 'examples/arc_demo.am1').read_text(), demo=True)
    assert len(lists) == 1
    scene = decode(lists[0])
    viewport = (88, 230, 936, 750)
    curves = [(193, 500, 80, 80, 0, 256, 8), (513, 500, 141, 83, 0, 256, 8),
              (874, 500, 118, 170, 232, -208, 8), (874, 500, 79, 112, 232, -208, 16)]
    expected = [edge for curve in curves for edge in reference(viewport, curve)]
    # The border uses four points and 24 vector segments before the curves.
    check_commands(dict(points=scene['points'][4:], vectors=scene['vectors'][24:]), expected)
    print(f'Demo drew {len(expected)} visible chords with a retained border.')


if __name__ == '__main__':
    main()
