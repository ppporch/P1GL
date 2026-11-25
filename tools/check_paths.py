"""Exercise the path API on the PDP-1 CPU and decode its Type 340 lists."""
import os
import subprocess

from check_viewport import build, call, clipping, root
from rim import read_mem, tape_memory, write_mem
from type340_model import decode, read_lists


def execute(name, source):
    asm = build / f'{name}.am1'
    asm.write_text(source)
    result = subprocess.run([os.environ.get('AM1', 'am1'), '-d', '-S',
                             '-DDEMO_CPU_TEST', asm.name], cwd=build,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout
    memory, entry = tape_memory(asm.with_suffix('.rim'))
    write_mem(build / 'paths.mem', memory)
    (build / 'paths-empty.mem').write_text('')
    run = subprocess.run(['./type340_runner', 'paths.mem', 'paths-empty.mem',
                          'paths-out.mem', f'{entry:o}'], cwd=build,
                         check=True, capture_output=True, text=True)
    assert 'overflow=0' in run.stdout, run.stdout
    return read_lists(build / 'lists.trace')


def frame(commands, capacity=256):
    return (f'jda gframe_begin\nscene; 0d{capacity}\n' + commands
            + 'jsp gframe_end\njsp gframe_refresh\n')


def table(name, values):
    return name + ',\n' + '; '.join(
        f'{"-" if value < 0 else ""}0d{abs(value)}' for value in values
    ) + '\n'


def nominal_redraw_us(words):
    """Type 340 timing for these point/vector lists, excluding host delays."""
    mode = 0
    duration = 0.0
    for word in words:
        duration += 5
        if mode == 1 and (not word & 0o200000 or word & 0o2000):
            duration += 35
        if mode == 4:
            longest = max(word & 127, (word >> 8) & 127)
            pulses = (1 << max(3, longest.bit_length())) - 1
            duration += 0.5 + 1.5 * pulses
            if word & 0o400000:
                mode = 0
        else:
            mode = (word >> 13) & 7
    return duration


def main():
    points = [(100 + i * 20, 400 + (i % 4) * 20) for i in range(20)]
    short_edges = list(zip(points, points[1:]))
    baseline = ''.join(call('gline', (*a, *b)) for a, b in short_edges)
    route = [(200, 210), (900, 250), (900, 750), (200, 790)]
    rect = (100, 100, 800, 800)
    source = 'Path CPU test\n#define P1GL_RETAINED\n100/\ngo,lem\nlsm\ncbs\n'
    source += frame(baseline)
    source += frame('jda gpolyline\npoints; 0d20; 0\n')
    source += frame(call('gview_set', rect) + 'jda gpolyline\nroute; 4; 0\n')
    source += frame('jda gtrace\nsamples; 0d20; 0d480; -0d20\n')
    source += frame(''.join(call('gmarker', (300, 300, 20, shape))
                            for shape in range(3)))
    source += frame('jda gpolyline\npoints; 0; 0\n'
                    'jda gpolyline\npoints; 1; 1\n'
                    'jda gtrace\nsamples; 1; 0d550; 0\n'
                    'jda gmarker\n0d600; 0d400; 0; 1\n')
    source += ('jda gframe_begin\nscene; 0d64\n'
               'jda ggroup_define\nmarker_group; 0d10\n'
               'jda gmarker\n0d200; 0d300; 0d20; 0\n'
               'jsp ggroup_end\njsp gframe_end\njsp gframe_refresh\n'
               'jda ggroup_replace\nmarker_group; marker_scratch\n'
               'jda gmarker\n0d300; 0d300; 0d20; 2\n'
               'jsp ggroup_end\njsp gframe_refresh\n')
    source += 'jda gpolyline\nlong_trace; 0d100; 0\n'
    for commands, capacity in (
        ('jda gpolyline\npoints; 0d20; 0\n', 8),
        ('jda gpolyline\n07777; 1; 0\n', 256),
        ('jda gpolyline\npoints; -1; 0\n', 256),
        ('jda gpolyline\npoints; 010001; 0\n', 256),
        ('jda gtrace\nsamples; 2; 0d8190; 2\n', 256),
        ('jda gmarker\n0d600; 0d400; 1; 3\n', 256),
    ):
        source += frame(commands, capacity)
        source += f'sad [{2 if capacity == 8 else 1}]\njmp .+2\njmp failed\n'
    source += 'law 1\ndac success\nfailed,hlt\nsuccess,0\n'
    source += table('points', [coord for point in points for coord in point])
    source += table('route', [coord for point in route for coord in point])
    source += table('samples', [y for _, y in points])
    long_points = [(200 + 5*i, 600 + 10*(i % 2)) for i in range(100)]
    source += table('long_trace', [coord for point in long_points for coord in point])
    for module in ('gplot', 'gline', 'gframe', 'gview', 'gpath', 'gtext', 'gretained'):
        source += f'#include "../src/{module}.ac"\n'
    source += ('constants\nmarker_group,0; 0; 0\nmarker_scratch,\ntable 0d10,0\n'
               'scene,\ntable 0d256,0\nguard,0123456\nstart go\n')
    lists = execute('paths-check', source)
    symbols = {fields[2]: int(fields[0], 8)
               for row in (build / 'paths-check.sym').read_text().splitlines()
               if len(fields := row.split()) == 4 and fields[0].isdigit()}
    output = read_mem(build / 'paths-out.mem')
    assert output[symbols['success']] == 1
    assert output[symbols['guard']] == 0o123456

    assert decode(lists[0])['vectors'] == short_edges
    assert decode(lists[1])['vectors'] == short_edges
    assert len(lists[0]) == 117 and len(lists[1]) == 25
    baseline_us, path_us = map(nominal_redraw_us, lists[:2])
    assert path_us < baseline_us
    clipped = decode(lists[2])['vectors']
    expected = [clipping(rect, (*a, *b)) for a, b in zip(route, route[1:])]
    expected = [segment for segment in expected if segment]
    assert len([1 for a, b in zip(clipped, clipped[1:]) if a[1] != b[0]]) == 1
    assert clipped[0][0] == expected[0][0]
    assert clipped[-1][1] == expected[-1][1]
    assert all(rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]
               for segment in clipped for x, y in segment)
    reverse_trace = [(480 - i*20, y) for i, (_, y) in enumerate(points)]
    assert decode(lists[3])['vectors'] == list(zip(reverse_trace, reverse_trace[1:]))
    assert decode(lists[4])['vectors'] == [
        ((280, 300), (320, 300)), ((300, 280), (300, 320)),
        ((280, 280), (320, 320)), ((280, 320), (320, 280)),
        ((280, 300), (300, 320)), ((300, 320), (320, 300)),
        ((320, 300), (300, 280)), ((300, 280), (280, 300)),
    ]
    assert decode(lists[5])['points'] == [points[0], (550, points[0][1]), (600, 400)]
    assert decode(lists[6])['vectors'] == [((180, 300), (220, 300)), ((200, 280), (200, 320))]
    assert decode(lists[7])['vectors'] == decode(lists[4])['vectors'][-4:]
    assert len(lists[8:]) > 1
    assert [v for words in lists[8:] for v in decode(words)['vectors']] == list(
        zip(long_points, long_points[1:]))
    print(f'19-segment trace: {len(lists[0])} words with gline, '
          f'{len(lists[1])} words with gpolyline.')
    print(f'Nominal redraw: {baseline_us/1000:.3f} ms vs {path_us/1000:.3f} ms.')

    demo = execute('path-demo-check', (root / 'examples/path_demo.ac').read_text())
    assert len(demo) == 1 and decode(demo[0])['vectors']
    print('Clipping, disconnected runs, markers, immediate chunks, faults and demo passed.')


if __name__ == '__main__':
    main()
