"""Exercise the real PENMENU library through P1GL's polled pen path."""
import os

from check_arcs import check_commands, reference
from check_transform import build, execute, root
from type340_model import decode


def main():
    script = build / 'pen-events.txt'
    script.write_text(
        '2 154 1004 59920\n'
        '3 154 1004 59960\n'
        '4 154 1004 0\n'
        '5 282 1004 40\n'
        '6 282 1004 80\n'
        '8 26 800 400\n'
        '10 26 1004 760\n'
    )
    env = dict(os.environ, P1GL_TEST_PEN=str(script))
    source = (root / 'examples/penmenu_demo.am1').read_text()
    out, sy, scans = execute(source, demo=True, env=env)
    assert len(scans) == 12
    assert out[sy['selected']] == 1
    assert [out[sy['test_history'] + i] for i in range(12)] == [0, 2, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0]
    curves = [
        (512, 536, 130, 130, 0, 256, 8),
        (512, 536, 180, 105, 0, 256, 8),
        (512, 536, 180, 128, 29, 197, 8),
    ]
    screen = (0, 0, 1023, 1023)
    for words, choice in zip(scans, [0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 0, 0]):
        scene = decode(words)
        assert any(y >= 1000 for _, y, _, _ in scene['chars'])
        check_commands(scene, reference(screen, curves[choice]))

    # The same adapter must follow a different frame buffer and the
    # immediate drawing buffer, rather than assuming a fixed application list.
    a = source.index('        law 1\n        dac selected')
    b = source.index('selected,0', a)
    driver = '''        jda gframe_begin
        scene; 0d20
        jda gplot
        0d100; 0d200
        jsp gframe_end
        jsp gframe_refresh
        jda gframe_begin
        other; 0d20
        jda gplot
        0d120; 0d240
        jsp gframe_end
        jsp gframe_refresh
        jda gplot
        0d180; 0d300
        hlt
other,
        table 0d20,0
'''
    _, _, scans = execute(source[:a] + driver + source[b:])
    assert [decode(words)['points'] for words in scans] == [[(100, 200)], [(120, 240)], [(180, 300)]]
    print('PENMENU passed action delivery, held hits across clock wrap, off-menu hits and scan routing.')


if __name__ == '__main__':
    main()
