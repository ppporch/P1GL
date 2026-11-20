"""Session-specific guarded vector-font preview; not a general installer."""
from pathlib import Path
import datetime,json,re,subprocess,sys,time
from rim import tape_memory
sys.path.insert(0,'/opt/pidp1-mods/FunStuff/SignalAnalysis')
from live import Link
home=Path(__file__).resolve().parents[1];build=home/'build'
old,_=tape_memory(Path('/tmp/p1gl-type340-20261119/P1GL/build/frame_demo.rim'))
new,_=tape_memory(build/'vector_text_demo.rim')
with Link() as l:
    state=l.state()
    assert state[12] and not any(state[i] for i in (13,18,19))
    assert l.memory(0o100,16)==[old[0o100+i] for i in range(16)], 'Not our known Type 340 geometry demo'
    l.request(0x31);halted=l.state();assert not halted[10]
    core=l.memory(0,65536)
    snap=build/'snapshots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ-vector-text')
    snap.mkdir(parents=True,exist_ok=False)
    (snap/'core.mem').write_text(''.join(f'{a:06o}: {w:06o}\n' for a,w in enumerate(core)))
    (snap/'registers.json').write_text(json.dumps(dict(before_stop=state,after_stop=halted))+'\n')
subprocess.run(['/opt/pidp1-mods/bin/fastload','-y',str(build/'vector_text_demo.rim')],check=True)
sy={}
for line in (build/'vector_text_demo.sym').read_text().splitlines():
    f=line.split()
    if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
with Link() as l:
    first=l.memory(sy['frames'],1)[0];t0=time.monotonic()
    time.sleep(14)
    elapsed=time.monotonic()-t0;last=l.memory(sy['frames'],1)[0];state=l.state()
    values={k:l.memory(sy[k],1)[0] for k in ('fault','gf_fault','buffer_guard','gf_used','gf_points','gf_vectors','gf_chars','page')}
    font=l.memory(4096,4096)
assert state[10] and values['fault']==0 and values['gf_fault']==0 and values['buffer_guard']==0o123456,values
assert all(font[a-4096]==w for a,w in new.items() if 4096<=a<8192),'Font bank modified'
count=(last-first)&0o777777;assert count>0
report=dict(snapshot=str(snap),frames=count,elapsed_seconds=elapsed,mean_frame_ms=elapsed*1000/count,run=bool(state[10]),values=values,font_bank_unchanged=True,backend='optional Hershey stroke vectors plus native Type 342 comparison',limit='Frame-counter mean includes scene construction; no worst-case latency or client rendering claim')
(build/'vector-text-live-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
