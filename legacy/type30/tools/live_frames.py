"""Replace only our known circle demo with the verified retained-frame demo.
Saves halted core/register state first; leaves drum/tape untouched.
"""
import datetime,json,re,subprocess,sys,time
from pathlib import Path
from rim import tape_memory
sys.path.insert(0,'/opt/pidp1-mods/FunStuff/SignalAnalysis')
from live import Link
home=Path(__file__).resolve().parents[1];build=home/'build'
old,_=tape_memory(build/'circle_demo.rim')
with Link() as l:
    before=l.state()
    assert before[12] and not any(before[i] for i in (13,18,19)), 'Power/debug state changed'
    signature=l.memory(0o100,16)
    assert signature==[old[0o100+i] for i in range(16)], 'Current program is not our circle demo; leave it alone'
    l.request(0x31)
    state=l.state();assert not state[10]
    mem=l.memory(0,65536)
    snap=build/'snapshots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ-frames')
    snap.mkdir(parents=True,exist_ok=False)
    (snap/'core.mem').write_text(''.join(f'{a:06o}: {w:06o}\n' for a,w in enumerate(mem)))
    (snap/'registers.json').write_text(json.dumps(dict(before_stop=before,after_stop=state))+'\n')
subprocess.run(['/opt/pidp1-mods/bin/fastload','-y',str(build/'frame_demo.rim')],check=True)
sy={}
for line in (build/'frame_demo.sym').read_text().splitlines():
    f=line.split()
    if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
with Link() as l:
    first=l.memory(sy['frames'],1)[0];t0=time.monotonic()
    time.sleep(10)
    elapsed=time.monotonic()-t0;last=l.memory(sy['frames'],1)[0]
    state=l.state();page=l.memory(sy['page'],1)[0]
    fault=l.memory(sy['fault'],1)[0];guard=l.memory(sy['buffer_guard'],1)[0]
    frame_fault=l.memory(sy['gf_fault'],1)[0]
    max_draw=l.memory(sy['max_draw_ms'],1)[0]
    point_count=l.memory(sy['gf_points'],1)[0]
    char_count=l.memory(sy['gf_chars'],1)[0]
assert state[10] and fault==0 and frame_fault==0 and guard==0o123456
count=(last-first)&0o777777
assert count>0
report=dict(snapshot=str(snap),frames=count,elapsed_seconds=elapsed,mean_frame_ms=elapsed*1000/count,page=page,run=bool(state[10]),fault=fault,buffer_guard=f'{guard:06o}',frame_fault=frame_fault,max_draw_ms=max_draw,points=point_count,characters=char_count,demo='three retained scenes: Type 33 labels, circle, radius line, center point; 22 ms clock pacing',limit='Mean frame-counter rate, not maximum frame latency or client rendering rate')
(build/'frame-live-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
