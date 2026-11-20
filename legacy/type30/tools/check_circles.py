"""Execute midpoint circles on the installed CPU; verify every display word."""
import json,os,random,subprocess,sys
from pathlib import Path
from rim import tape_memory,write_mem
root=Path(__file__).resolve().parents[1];build=root/'build'
sys.path.insert(0,str(root/'reference'))
from gcircle import circle_points
rng=random.Random(0x43315243)
cases=[(512,512,r) for r in range(129)]
for cx,cy in ((0,0),(0,512),(512,0),(1023,0),(1023,512),(512,1023),(0,1023),(1023,1023)):
    cases += [(cx,cy,r) for r in (0,1,2,3,16,31,127,511,512,1023)]
cases += [tuple(rng.randrange(1024) for _ in range(3)) for _ in range(64)]
cases += [(512,512,511),(512,512,512),(512,512,724),(512,512,1023)]
total=0;clipped=0
for a in cases:
    source='P1GL executed circle check\n100/\ngo, lem\nlsm\ncbs\njda gcircle\n'
    source+=''.join(f'0d{v}\n' for v in a)
    source+='hlt\n#include "../src/gcircle.am1"\n#include "../src/gplot.am1"\nconstants\nstart go\n'
    (build/'circle-check.am1').write_text(source)
    subprocess.run([os.environ.get('AM1','am1'),'-d','circle-check.am1'],cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'circle-check.rim');write_mem(build/'circle.mem',mem)
    (build/'empty.mem').write_text('')
    run=subprocess.run([str(build/'plot_runner'),'circle.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    assert 'overflow=0' in run.stdout,(a,run.stdout)
    trace=[tuple(int(w,8) for w in l.split()) for l in (build/'points.trace').read_text().splitlines()]
    expected=circle_points(*a)
    assert len(trace)==len(expected),(a,len(trace),len(expected))
    def coord(w):
        c=w>>8;return (c+bool(c&512)+512)&1023
    for i,((ac,io,mb),(x,y)) in enumerate(zip(trace,expected)):
        assert (coord(ac),coord(io),mb)==(max(1,x),max(1,y),0o730207),(a,i,(x,y),oct(ac),oct(io))
    total+=len(expected)
    if a[0]-a[2]<0 or a[1]-a[2]<0 or a[0]+a[2]>1023 or a[1]+a[2]>1023:clipped+=1
# Test every actual demo page, including cache generation and raw replay.
(build/'circle-demo-once.am1').write_text((root/'examples/circle_demo.am1').read_text())
subprocess.run([os.environ.get('AM1','am1'),'-d','-DDEMO_CPU_TEST','circle-demo-once.am1'],cwd=build,check=True,capture_output=True,text=True)
mem,start=tape_memory(build/'circle-demo-once.rim');write_mem(build/'circle.mem',mem)
run=subprocess.run([str(build/'plot_runner'),'circle.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
assert 'overflow=0' in run.stdout,run.stdout
pages=[(512,512,r) for r in (8,16,24,32)]+[(0,512,24),(1023,512,24),(512,0,24),(512,1023,24),(0,0,32),(1023,1023,32),(512,512,0)]
expected=[(max(1,cx+(x-cx)*8),max(1,cy+(y-cy)*8)) for cx,cy,r in pages for x,y in circle_points(cx,cy,r)]
trace=[tuple(int(w,8) for w in l.split()) for l in (build/'points.trace').read_text().splitlines()]
assert len(trace)==len(expected),(len(trace),len(expected))
for i,((ac,io,mb),(x,y)) in enumerate(zip(trace,expected)):
    assert (coord(ac),coord(io),mb)==(x,y,0o730207),(i,x,y,oct(ac),oct(io))
from rim import read_mem
out=read_mem(build/'output.mem')
sy={}
import re
for line in (build/'circle-demo-once.sym').read_text().splitlines():
    f=line.split()
    if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
assert out[sy['fault']]==0
assert out[sy['buffer_guard']]==0o123456
assert out[sy['frames']]==len(pages)
report=dict(demo_pages=len(pages),demo_points=len(expected),demo_cpu=run.stdout.strip(),cases=len(cases),points=total,clipped_cases=clipped,seed='0x43315243',comparison='every point and IOT word; unique symmetry points; viewport clipping; device zero clamp',isa='original PDP-1; extensions disabled',timing='immediate device completion, not live timing')
(build/'circle-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
