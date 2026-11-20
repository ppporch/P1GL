"""Session-specific guarded migration of Phillip's known v0.8 combined demo.
Not a general-purpose installer. Saves core/registers before loading v0.9.
"""
from pathlib import Path
import datetime,json,re,subprocess,sys,time
from rim import tape_memory
sys.path.insert(0,'/opt/pidp1-mods/FunStuff/SignalAnalysis')
from live import Link
home=Path(__file__).resolve().parents[1];build=home/'build'
old=build/'frame_demo-coarse.rim'
image,_=tape_memory(old)
with Link() as l:
    state=l.state()
    assert state[12] and not any(state[i] for i in (13,18,19)), 'Power/debug state changed'
    assert l.memory(0o100,16)==[image[0o100+i] for i in range(16)], "Not our known coarse Type 340 demo"
    l.request(0x31)
    halted=l.state();assert not halted[10]
    core=l.memory(0,65536)
    snap=build/'snapshots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ-type340')
    snap.mkdir(parents=True,exist_ok=False)
    (snap/'core.mem').write_text(''.join(f'{a:06o}: {w:06o}\n' for a,w in enumerate(core)))
    (snap/'registers.json').write_text(json.dumps(dict(before_stop=state,after_stop=halted))+'\n')
subprocess.run(['/opt/pidp1-mods/bin/fastload','-y',str(build/'frame_demo.rim')],check=True)
sy={}
for line in (build/'frame_demo.sym').read_text().splitlines():
    f=line.split()
    if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
with Link() as l:
    t0=time.monotonic();first=l.memory(sy['frames'],1)[0]
    time.sleep(10)
    elapsed=time.monotonic()-t0;last=l.memory(sy['frames'],1)[0]
    state=l.state()
    values={k:l.memory(sy[k],1)[0] for k in ('fault','gf_fault','buffer_guard','max_draw_ms','gf_used','gf_points','gf_vectors','gf_chars','page')}
assert state[10] and values['fault']==0 and values['gf_fault']==0 and values['buffer_guard']==0o123456,values
count=(last-first)&0o777777;assert count>0
report=dict(snapshot=str(snap),frames=count,elapsed_seconds=elapsed,mean_frame_ms=elapsed*1000/count,run=bool(state[10]),values=values,backend='native Type 340 display list, vectors and Type 342 characters',limit='Mean includes scene changes; max_draw_ms is sampled BBN display-completion duration, not worst-case latency or client frame rate')
(build/'type340-live-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
