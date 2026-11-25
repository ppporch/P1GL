"""Verify transformations and clipped display commands on the PiDP-1 CPU."""
import math
import os
from pathlib import Path
import random
import re
import subprocess

from check_viewport import build, call, clipping
from rim import read_mem, tape_memory, write_mem
from type340_model import decode, read_lists

root = Path(__file__).resolve().parents[1]
am1 = os.environ.get('AM1', 'am1')
rect = (256, 256, 768, 768)


def transform(pose, x, y):
    tx, ty, angle, sx, sy = pose
    sine = round(1024 * math.sin(math.tau * angle / 256))
    cosine = round(1024 * math.cos(math.tau * angle / 256))
    xx = (cosine * sx + 512) // 1024
    xy = (-sine * sy + 512) // 1024
    yx = (sine * sx + 512) // 1024
    yy = (cosine * sy + 512) // 1024
    return tx + (xx * x + xy * y + 512) // 1024, ty + (yx * x + yy * y + 512) // 1024


def execute(source, demo=False, env=None):
    test = build / 'transform-check.am1'
    test.write_text(source)
    flags = ['-DDEMO_CPU_TEST'] if demo else []
    result = subprocess.run([am1, '-d', '-S', *flags, test.name], cwd=build,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout
    memory, entry = tape_memory(test.with_suffix('.rim'))
    write_mem(build / 'transform.mem', memory)
    (build / 'transform-empty.mem').write_text('')
    proc = subprocess.run(['./type340_runner', 'transform.mem', 'transform-empty.mem',
                           'transform-out.mem', f'{entry:o}'], cwd=build,
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 0 and 'overflow=0' in proc.stdout, proc.stderr + proc.stdout
    out = read_mem(build / 'transform-out.mem')
    sy = {f[2]: int(f[0], 8) for row in test.with_suffix('.sym').read_text().splitlines()
          if len(f := row.split()) == 4 and re.fullmatch('[0-7]{6}', f[0])}
    assert out[sy['gf_fault']] == 0
    return out, sy, read_lists(build / 'lists.trace')


def signed(word):
    return word if word < 0o400000 else -(0o777777 ^ word)


def check_points(cases):
    source = ['Transform CPU test\n100/\ngo, lem\nlsm\ncbs\n']
    for n, (pose, point) in enumerate(cases):
        if pose is not None:
            source += [call('gtransform_set', pose), f'dac set{n}\n']
        source += [call('gtransform_point', point),
                   f'dac status{n}\nlac gtransform_x\ndac x{n}\n'
                   f'lac gtransform_y\ndac y{n}\n']
    source.append('hlt\n')
    for n in range(len(cases)):
        source.append(f'set{n},0\nstatus{n},0\nx{n},0\ny{n},0\n')
    for module in ('gplot', 'gline', 'gframe', 'gview', 'gtransform'):
        source.append(f'#include "../src/{module}.ac"\n')
    source.append('constants\nstart go\n')
    out, sy, lists = execute(''.join(source))
    assert not lists
    current = (0, 0, 0, 1024, 1024)
    previous = (0, 0)
    for n, (pose, point) in enumerate(cases):
        if pose is not None:
            tx, ty, angle, sx, sy_scale = pose
            valid = (abs(tx) <= 1023 and abs(ty) <= 1023 and 0 <= angle <= 255
                     and abs(sx) <= 4096 and abs(sy_scale) <= 4096)
            assert out[sy[f'set{n}']] == int(not valid)
            if valid:
                current = pose
        valid = all(abs(p) <= 1023 for p in point)
        expected = transform(current, *point) if valid else previous
        actual = tuple(signed(out[sy[f'{v}{n}']]) for v in ('x', 'y'))
        assert out[sy[f'status{n}']] == int(not valid)
        assert actual == expected, (n, current, point, actual, expected)
        previous = actual


def check_line_entry():
    pose = (256, 512, 64, 2048, 512)
    lines = [(-30, 20, 30, -20), (-30, 20, 30, 20),
             (10, -60, -30, -60), (0, 0, 0, 0)]
    source = ['Transform line CPU test\n100/\ngo, lem\nlsm\ncbs\n',
              call('gview_set', rect), call('gtransform_set', pose)]
    for line in lines:
        source += ['jda gframe_begin\nscene; 0d64\n', call('gline_transform', line),
                   'jsp gframe_end\njsp gframe_refresh\n']
    source.append('hlt\n')
    for module in ('gplot', 'gline', 'gframe', 'gview', 'gtransform'):
        source.append(f'#include "../src/{module}.ac"\n')
    source.append('constants\nscene,\ntable 0d64,0\nstart go\n')
    _, _, lists = execute(''.join(source))
    assert len(lists) == len(lines)
    for words, (x0, y0, x1, y1) in zip(lists, lines):
        expected = clipping(rect, (*transform(pose, x0, y0), *transform(pose, x1, y1)))
        d = decode(words)
        if expected is None:
            assert not d['points'] and not d['vectors']
        else:
            a, b = expected
            assert d['points'] == [a]
            assert d['vectors'] == ([(a, b)] if a != b else [])
    print('Transformed-line entry passed clipped, hidden, visible and point cases.')


def check_demo():
    _, _, lists = execute((root / 'examples/transform_demo.ac').read_text(), demo=True)
    assert len(lists) == 256, len(lists)
    border_count = 20
    border = decode(lists[0])['vectors'][:border_count]
    edges = [(-60, 22, 60, 0), (60, 0, -60, -22),
             (-60, -22, -27, 0), (-27, 0, -60, 22), (-27, 0, 60, 0)]
    clipped_edges = 0
    for angle, words in enumerate(lists):
        phase = min(angle, 256 - angle)
        pose = (320 + 3 * phase + phase // 2, 512, angle, 512 + 4 * phase, 512 + 4 * phase)
        actual = decode(words)['vectors']
        assert actual[:border_count] == border
        drawn = iter(actual[border_count:])
        for x0, y0, x1, y1 in edges:
            a, b = transform(pose, x0, y0), transform(pose, x1, y1)
            expected = clipping(rect, (*a, *b))
            if expected != [a, b]:
                clipped_edges += 1
            if not expected or expected[0] == expected[1]:
                continue
            point, end = expected
            for _ in range(10):
                start, finish = next(drawn)
                assert start == point, (angle, start, point)
                assert all(256 <= v <= 768 for v in (*start, *finish))
                if finish == end:
                    break
                point = finish
            else:
                raise AssertionError((angle, expected))
        assert next(drawn, None) is None
    assert clipped_edges
    print(f'All 256 demo frames matched the transformed arrow; {clipped_edges} edges were clipped or hidden.')


def main():
    special = [(None, (-1023, 1023)), ((3, -4, 64, 1024, 512), (5, -6)),
               ((0, 0, 0, 512, -512), (-3, -3)), (None, (3, 3)),
               ((1024, 0, 0, 1024, 1024), (1, 2)),
               ((0, 0, -1, 1024, 1024), (1, 2)),
               ((0, 0, 256, 1024, 1024), (1, 2)),
               ((0, 0, 0, 4097, 1024), (1, 2)),
               (None, (-131071, 0)), ((1023, -1023, 32, 4096, 4096), (1023, -1023)),
               ((23, 44, 192, 0, 0), (1023, -1023))]
    check_points(special)
    rng = random.Random(2048)
    angles = [((rng.randint(-1023, 1023), rng.randint(-1023, 1023), angle,
                rng.randint(-4096, 4096), rng.randint(-4096, 4096)),
               (rng.randint(-1023, 1023), rng.randint(-1023, 1023)))
              for angle in range(256)]
    for start in range(0, len(angles), 32):
        check_points(angles[start:start + 32])
    print(f'{len(special) + len(angles)} point cases matched the fixed-point reference.')
    check_line_entry()
    check_demo()


if __name__ == '__main__':
    main()
