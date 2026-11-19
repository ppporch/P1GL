"""Check assembled G_LINE point-for-point on the installed PDP-1 CPU object.
Device completion is immediate in this CPU-only test; timing is not physical.
"""
import json,os,random,subprocess,sys
from pathlib import Path
from rim import tape_memory,write_mem
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'reference'))
from gline import line_points
build=root/'build'
rng=random.Random(0x5031474c)
cases=[(512,512,512+dx,512+dy) for dx in range(-8,9) for dy in range(-8,9)]
cases += [(0,0,1023,1023),(1023,0,0,1023),(0,512,1023,512),(512,0,512,1023),(0,0,0,0),(1023,1023,1023,1023),(0,1,1,0),(1,0,0,1)]
for _ in range(128):
    a=tuple(rng.randrange(1024) for _ in range(4))
    cases.extend((a,(a[2],a[3],a[0],a[1])))
# Additional long, nearly axial cases exercise error signs and equality ties.
for dy in (0,1,2,511,512,1022,1023):
    cases.extend(((0,0,1023,dy),(1023,dy,0,0),(0,0,dy,1023),(dy,1023,0,0)))
points=0;batches=0
for offset in range(0,len(cases),8):
    batch=cases[offset:offset+8]
    source='P1GL executed G_LINE correctness batch\n100/\ngo, lem\nlsm\ncbs\n'
    for a in batch:
        source+='jda gline\n'+''.join(f'0d{v}\n' for v in a)
    source+='hlt\n#include "../src/gline.am1"\n#include "../src/gplot.am1"\nconstants\nstart go\n'
    (build/'line-check.am1').write_text(source)
    subprocess.run([os.environ.get('AM1','am1'),'-d','line-check.am1'],cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'line-check.rim');write_mem(build/'line.mem',mem)
    (build/'empty.mem').write_text('')
    run=subprocess.run([str(build/'plot_runner'),'line.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    assert 'overflow=0' in run.stdout,run.stdout
    trace=[tuple(int(w,8) for w in l.split()) for l in (build/'points.trace').read_text().splitlines()]
    expected=[p for a in batch for p in line_points(*a)]
    assert len(trace)==len(expected),(offset,len(trace),len(expected))
    def coord(w):
        c=w>>8
        return (c+bool(c&512)+512)&1023
    for i,((ac,io,mb),(x,y)) in enumerate(zip(trace,expected)):
        assert (coord(ac),coord(io),mb)==(max(1,x),max(1,y),0o730207),(offset,i,(x,y),oct(ac),oct(io),oct(mb))
    points+=len(expected);batches+=1
# Execute the actual paged demo, with one frame per page, through its view transform.
(build/'line-demo-once.am1').write_text((root/'examples/line_demo.am1').read_text())
subprocess.run([os.environ.get('AM1','am1'),'-d','-DDEMO_CPU_TEST','line-demo-once.am1'],cwd=build,check=True,capture_output=True,text=True)
mem,start=tape_memory(build/'line-demo-once.rim');write_mem(build/'line.mem',mem)
run=subprocess.run([str(build/'plot_runner'),'line.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
ends=[(32,12),(12,32),(-12,32),(-32,12),(-32,-12),(-12,-32),(12,-32),(32,-12),(32,0),(0,32),(-32,0),(0,-32),(32,32),(-32,32),(-32,-32),(32,-32)]
demo=[(512,512,512+x,512+y) for x,y in ends]
demo += [(c,d,a,b) for a,b,c,d in demo]
expected=[(512+(x-512)*8,512+(y-512)*8) for a in demo for x,y in line_points(*a)]
trace=[tuple(int(w,8) for w in l.split()) for l in (build/'points.trace').read_text().splitlines()]
assert len(trace)==len(expected),(len(trace),len(expected))
for (ac,io,mb),(x,y) in zip(trace,expected):
    assert (coord(ac),coord(io),mb)==(x,y,0o730207),(x,y,oct(ac),oct(io))
assert 'overflow=0' in run.stdout,run.stdout
report=dict(demo_pages=32,demo_points=len(expected),demo_cpu=run.stdout.strip(),cases=len(cases),points=points,batches=batches,seed='0x5031474c',isa='original PDP-1; PDP-1D extensions disabled',comparison='every emitted point equals host Bresenham reference after documented coordinate-zero clamp',timing='immediate IOT completion; no real display timing claim')
(build/'line-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
