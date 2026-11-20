"""Execute assembled calibration and every valid coordinate on the installed CPU."""
import json, subprocess
from pathlib import Path
from rim import tape_memory,write_mem
root=Path(__file__).resolve().parents[1]
build=root/'build'
results=[]
for name,expected in [('calibrate-once',[(x+dx,y+dy) for y in (112,512,912) for x in (112,512,912) for dx,dy in ((0,0),(-3,0),(3,0),(0,-3),(0,3))]),('coordinate_sweep',[(x,1023-x) for x in range(1024)])]:
    mem,start=tape_memory(build/(name+'.rim'))
    write_mem(build/'program.mem',mem)
    (build/'empty.mem').write_text('')
    run=subprocess.run([str(build/'plot_runner'),'program.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    trace=[tuple(int(w,8) for w in line.split()) for line in (build/'points.trace').read_text().splitlines()]
    assert len(trace)==len(expected),(name,len(trace))
    def coordinate(w):
        c=w>>8
        return (c+(1 if c&512 else 0)+512)&1023
    for (ac,io,mb),(x,y) in zip(trace,expected):
        assert (coordinate(ac),coordinate(io))==(max(1,x),max(1,y)),(x,y,oct(ac),oct(io))
        assert mb==0o730207,oct(mb)
    results.append(dict(program=name,points=len(trace),cpu=run.stdout.strip()))
(build/'cpu-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
