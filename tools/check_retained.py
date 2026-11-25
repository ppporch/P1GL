"""Run the retained-group and label API on the PiDP-1 CPU object."""
import os
import re
import subprocess
from pathlib import Path

from rim import read_mem, tape_memory, write_mem
from type340_model import decode, label, read_lists

root = Path(__file__).resolve().parents[1]
build = root / 'build'
setup = '''jda gframe_begin
scene; 0d120
jda ggroup_define
group_handle; 0d12
jda gline
0d10; 0d20; 0d30; 0d40
jsp ggroup_end
jda glabel_define
label_handle; 0d10; 0d40; 0d50; 1
jsp gframe_end
'''
refresh = 'jsp gframe_refresh\n'
replace = 'jda ggroup_replace\ngroup_handle; scratch\n'
line = 'jda gline\n0d20; 0d25; 0d40; 0d45\n'
text = 'jda glabel_text\nlabel_handle; message\n'
number = 'jda glabel_number\nlabel_handle; -0d125; 2\n'
record = 'dac result\n'
source = f'''Retained API checks
#define P1GL_RETAINED
100/
go, lem
lsm
cbs
{setup}
{text}
{refresh}
{replace}
{line}
jsp ggroup_end
{number}
{refresh}
{replace}
{line * 3}
jsp ggroup_end
{record}
{refresh}
jda glabel_text
label_handle; too_long
dac text_error
{refresh}
jda ggroup_replace
group_handle; scene
dac overlap_error
{refresh}
jda ggroup_replace
group_handle; scratch
jsp ggroup_end
jda glabel_number
label_handle; -0d131071; 5
{refresh}
jda glabel_number
label_handle; 0777777; 3
{refresh}
jda gframe_begin
scene; 0d120
jsp gframe_end
{text}
dac stale_error
{refresh}
hlt
result,0
text_error,0
overlap_error,0
stale_error,0
message,ascii "TEST"
too_long,ascii "THIS IS TOO LONG"
group_handle,0; 0; 0
label_handle,0; 0; 0
#include "../src/gplot.ac"
#include "../src/gline.ac"
#include "../src/gtext.ac"
#include "../src/gframe.ac"
#include "../src/gretained.ac"
constants
scratch,
table 0d12,0
scratch_guard,0123456
scene,
table 0d120,0
scene_guard,0654321
start go
'''
(build / 'retained-check.am1').write_text(source)
subprocess.run([os.environ.get('AM1', 'am1'), '-d', '-S', 'retained-check.am1'], cwd=build, check=True)
memory, entry = tape_memory(build / 'retained-check.rim')
write_mem(build / 'retained.mem', memory)
(build / 'retained-empty.mem').write_text('')
subprocess.run([str(build / 'type340_runner'), 'retained.mem', 'retained-empty.mem',
                'retained-out.mem', f'{entry:o}'], cwd=build, check=True)
out = read_mem(build / 'retained-out.mem')
symbols = {}
for line in (build / 'retained-check.sym').read_text().splitlines():
    fields = line.split()
    if len(fields) == 4 and re.fullmatch('[0-7]{6}', fields[0]):
        symbols[fields[2]] = int(fields[0], 8)
for name, value in [('result', 2), ('text_error', 1), ('overlap_error', 1),
                    ('stale_error', 1), ('scratch_guard', 0o123456),
                    ('scene_guard', 0o654321), ('gf_fault', 0)]:
    assert out[symbols[name]] == value, (name, out[symbols[name]], value)
lists = read_lists(build / 'lists.trace')
assert len(lists) == 8
first, second = map(decode, lists[:2])
assert first['vectors'] == [((10, 20), (30, 40))]
assert second['vectors'] == [((20, 25), (40, 45))]
assert first['chars'] == label(40, 50, 1, 'TEST      '), first['chars']
assert second['chars'] == label(40, 50, 1, '     -1.25'), second['chars']
assert lists[1] == lists[2] == lists[3] == lists[4]
assert decode(lists[5])['vectors'] == []
assert decode(lists[5])['chars'] == label(40, 50, 1, '  -1.31071')
assert decode(lists[6])['chars'] == label(40, 50, 1, '     0.000')
assert decode(lists[7])['chars'] == []
print('Retained groups and text passed, including atomic rejection and stale handles.')
