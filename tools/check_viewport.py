"""Compare actual executed PDP-1 clipping against an exact rational oracle."""
from fractions import Fraction
import math
import os
from pathlib import Path
import random
import re
import subprocess

from rim import read_mem, tape_memory, write_mem
from type340_model import decode, read_lists

root = Path(__file__).resolve().parents[1]
build = root / 'build'


def clipping(rect, line):
    x0, y0, x1, y1 = line
    xmin, ymin, xmax, ymax = rect
    lo, hi = Fraction(0), Fraction(1)
    for origin, direction, lower, upper in (
        (x0, x1 - x0, xmin, xmax),
        (y0, y1 - y0, ymin, ymax),
    ):
        if direction == 0:
            if not lower <= origin <= upper:
                return None
            continue
        a, b = sorted((Fraction(lower - origin, direction),
                       Fraction(upper - origin, direction)))
        lo, hi = max(lo, a), min(hi, b)
    if lo > hi:
        return None
    return [tuple(math.floor(coord + t * delta + Fraction(1, 2))
                  for coord, delta in ((x0, x1 - x0), (y0, y1 - y0)))
            for t in (lo, hi)]


def call(entry, values):
    args = '; '.join(f'{"-" if n < 0 else ""}0d{abs(n)}' for n in values)
    return f'jda {entry}\n{args}\n'


def run(cases):
    source = ['Viewport CPU test\n100/\ngo, lem\nlsm\ncbs\n']
    for rect, line in cases:
        if rect is not None:
            source.append(call('gview_set', rect))
        source += ['jda gframe_begin\nscene; 0d64\n', call('gline_clip', line),
                   'jsp gframe_end\njsp gframe_refresh\n']
    source += ['jda gframe_begin\nscene; 0d64\n',
               call('gline_clip', (-131071, 0, 100, 100)),
               'dac invalid_line\njsp gframe_end\njsp gframe_refresh\nhlt\ninvalid_line,0\n']
    for module in ('gplot', 'gline', 'gframe', 'gview'):
        source.append(f'#include "../src/{module}.ac"\n')
    source.append('constants\nscene,\ntable 0d64,0\nguard,0123456\nstart go\n')
    (build / 'viewport-check.am1').write_text(''.join(source))
    subprocess.run([os.environ.get('AM1', 'am1'), '-d', '-S', 'viewport-check.am1'],
                   cwd=build, check=True, capture_output=True)
    memory, entry = tape_memory(build / 'viewport-check.rim')
    write_mem(build / 'viewport.mem', memory)
    (build / 'empty.mem').write_text('')
    proc = subprocess.run(['./type340_runner', 'viewport.mem', 'empty.mem',
                           'out.mem', f'{entry:o}'], cwd=build, check=True,
                          capture_output=True, text=True)
    assert 'overflow=0' in proc.stdout, proc.stdout
    symbols = {f[2]: int(f[0], 8) for row in (build / 'viewport-check.sym').read_text().splitlines()
               if len(f := row.split()) == 4 and re.fullmatch('[0-7]{6}', f[0])}
    out = read_mem(build / 'out.mem')
    assert out[symbols['guard']] == 0o123456
    assert out[symbols['invalid_line']] == out[symbols['gf_fault']] == 1
    lists = read_lists(build / 'lists.trace')
    assert len(lists) == len(cases), (len(lists), len(cases))
    active_rect = (0, 0, 1023, 1023)
    for words, (rect, line) in zip(lists, cases):
        if rect is not None:
            x0, y0, x1, y1 = rect
            if 0 <= x0 <= x1 <= 1023 and 0 <= y0 <= y1 <= 1023:
                active_rect = rect
        rect = active_rect
        d = decode(words)
        result = clipping(rect, line)
        vector = d['vectors']
        if result is None:
            assert not (d['points'] or vector), (rect, line, d)
            continue
        a, b = result
        assert d['points'] == [a], (rect, line, result, d)
        if a == b:
            assert not vector, (line, d)
        else:
            assert vector and vector[0][0] == a and vector[-1][1] == b, (rect, line, result, d)
            assert all(p[1] == q[0] for p, q in zip(vector, vector[1:]))
        x0, y0, x1, y1 = rect
        assert all(x0 <= x <= x1 and y0 <= y <= y1
                   for segment in vector for x, y in segment), (rect, line, d)


def check_demo():
    test_source = build / 'viewport-demo-check.am1'
    test_source.write_text((root / 'examples/viewport_demo.ac').read_text())
    subprocess.run([os.environ.get('AM1', 'am1'), '-d', '-DDEMO_CPU_TEST',
                    test_source.name], cwd=build, check=True)
    memory, entry = tape_memory(test_source.with_suffix('.rim'))
    write_mem(build / 'viewport.mem', memory)
    subprocess.run(['./type340_runner', 'viewport.mem', 'empty.mem',
                    'out.mem', f'{entry:o}'], cwd=build, check=True)
    lists = read_lists(build / 'lists.trace')
    assert len(lists) == 280, len(lists)
    border_count = 20  # four 512-unit lines, five native segments each
    rect = (256, 256, 768, 768)
    route = ((232, 512, 4, 4), (512, 792, 4, -4),
             (792, 512, -4, -4), (512, 232, -4, 4))
    border = decode(lists[0])['vectors'][:border_count]
    for index, words in enumerate(lists):
        leg, step = divmod(index, 70)
        x, y, dx, dy = route[leg]
        x, y = x + step * dx, y + step * dy
        corners = [(x, y + 90), (x + 90, y), (x, y - 90), (x - 90, y)]
        expected = [clipping(rect, (*a, *b))
                    for a, b in zip(corners, corners[1:] + corners[:1])]
        expected = [tuple(edge) for edge in expected if edge and edge[0] != edge[1]]
        actual = decode(words)['vectors']
        assert actual[:border_count] == border
        assert actual[border_count:] == expected, (index, actual, expected)
    print('All 280 demo frames kept the retained border and drew the expected diamond.')


def main():
    rect = (100, 200, 800, 900)
    fixed = [(-8191, 500, 8191, 500), (300, -8191, 300, 8191),
             (50, 150, 100, 200), (50, 250, 150, 150),
             (-30, 190, 950, 190), (100, 200, 100, 200),
             (101, 199, 101, 199), (99, 200, 101, 201),
             (-8191, -8191, 8191, 8191), (8191, -8191, -8191, 8191),
             (99, 899, 102, 901), (99, 901, 101, 899)]
    cases = [(None, (-10, 512, 1100, 512)), (rect, fixed[0]),
             ((100, -1, 900, 900), fixed[0]), ((900, 200, 800, 900), fixed[0]),
             ((100, 200, 1024, 900), fixed[0])]
    cases += [(rect, line) for line in fixed]
    cases += [((256, 256, 256, 768), (-8191, 512, 8191, 512)),
              ((256, 256, 256, 256), (0, 0, 1023, 1023)),
              ((0, 0, 1023, 1023), (-8191, -8191, 8191, 8190))]
    rng = random.Random(340)
    for _ in range(320):
        xa, xb = sorted(rng.sample(range(1024), 2))
        ya, yb = sorted(rng.sample(range(1024), 2))
        scale = rng.choice((64, 1024, 8191))
        line = tuple(rng.randint(-scale, 1023 if scale == 64 else scale) for _ in range(4))
        cases.append(((xa, ya, xb, yb), line))
    cases += [(rect, (c, d, a, b)) for rect, (a, b, c, d) in cases[5:]]
    for start in range(0, len(cases), 40):
        run(cases[start:start + 40])
    print(f'{len(cases)} viewport cases matched exact rational clipping.')
    check_demo()


if __name__ == '__main__':
    main()
