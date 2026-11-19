"""Replace only our known line demo with the verified circle demo.
Saves halted core/register state first; leaves drum/tape untouched.
"""
import datetime,json,re,subprocess,sys,time
from pathlib import Path
from rim import tape_memory
sys.path.insert(0,'/opt/pidp1-mods/FunStuff/SignalAnalysis')
from live import Link
home=Path(__file__).resolve().parents[1];build=home/'build'
old,_=tape_memory(build/'line_demo.rim')
with Link() as l:
    before=l.state()
    assert before[12] and not any(before[i] for i in (13,18,19)), 'Power/debug state changed'
    signature=l.memory(0o100,16)
    assert signature==[old[0o100+i] for i in range(16)], 'Current program is not our line demo; leave it alone'
    l.request(0x31)
    state=l.state();assert not state[10]
    mem=l.memory(0,65536)
    snap=build/'snapshots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ-circles')
    snap.mkdir(parents=True,exist_ok=False)
    (snap/'core.mem').write_text(''.join(f'{a:06o}: {w:06o}\n' for a,w in enumerate(mem)))
    (snap/'registers.json').write_text(json.dumps(dict(before_stop=before,after_stop=state))+'\n')
subprocess.run(['/opt/pidp1-mods/bin/fastload','-y',str(build/'circle_demo.rim')],check=True)
sy={}
for line in (build/'circle_demo.sym').read_text().splitlines():
    f=line.split()
    if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
with Link() as l:
    first=l.memory(sy['frames'],1)[0];t0=time.monotonic()
    time.sleep(16)
    elapsed=time.monotonic()-t0;last=l.memory(sy['frames'],1)[0]
    state=l.state();page=l.memory(sy['page'],1)[0]
    fault=l.memory(sy['fault'],1)[0];guard=l.memory(sy['buffer_guard'],1)[0]
assert state[10] and fault==0 and guard==0o123456
count=(last-first)&0o777777
assert count>0
report=dict(snapshot=str(snap),frames=count,elapsed_seconds=elapsed,mean_frame_ms=elapsed*1000/count,page=page,run=bool(state[10]),fault=fault,buffer_guard=f'{guard:06o}',demo='11 pages: four radii, four clipped edges, two clipped corners, radius zero; retained raw points; 22 ms clock pacing',limit='Mean frame-counter rate, not maximum frame latency or client rendering rate')
(build/'circle-live-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
