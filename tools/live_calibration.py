"""Load calibration on an idle Pi after a full core snapshot; capture device output.
Run on the Pi only. Leaves calibration running for visual inspection.
"""
from pathlib import Path
import collections,datetime,json,re,socket,struct,subprocess,sys,time
sys.path.insert(0,'/opt/pidp1-mods/FunStuff/SignalAnalysis')
from live import Link
home=Path(__file__).resolve().parents[1]
build=home/'build'
snap=build/'snapshots'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
with Link() as l:
    state=l.state()
    assert state[12] and not state[10], 'Power must be on and CPU halted'
    assert not any(state[i] for i in (13,18,19)), 'Existing debugger state must be resolved first'
    memory=l.memory(0,65536)
    assert not l.state()[10], 'CPU began running during snapshot'
    snap.mkdir(parents=True,exist_ok=False)
    (snap/'core.mem').write_text(''.join(f'{a:06o}: {w:06o}\n' for a,w in enumerate(memory)))
    (snap/'registers.json').write_text(json.dumps(state)+'\n')
# Preflight verifies no display client is connected before running this tool.
display=socket.create_connection(('127.0.0.1',3400),timeout=3)
display.settimeout(.2)
subprocess.run(['/opt/pidp1-mods/bin/fastload','-y',str(build/'calibrate.rim')],check=True)
sy={}
for line in (build/'calibrate.sym').read_text().splitlines():
    f=line.split()
    if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]): sy[f[2]]=int(f[0],8)
with Link() as l: first=l.memory(sy['frames'],1)[0]
t0=time.monotonic();data=bytearray()
while time.monotonic()-t0<4:
    try: data.extend(display.recv(65536))
    except socket.timeout: pass
elapsed=time.monotonic()-t0
with Link() as l:
    last=l.memory(sy['frames'],1)[0];state=l.state()
display.close()
assert len(data)%4==0
words=struct.unpack(f'<{len(data)//4}I',data)
points=[(w&1023,(w>>10)&1023) for w in words]
expected=[(x+dx,y+dy) for y in (112,512,912) for x in (112,512,912) for dx,dy in ((0,0),(-3,0),(3,0),(0,-3),(0,3))]
assert len(points)>len(expected)*3, len(points)
start=points.index(expected[0])
assert all(p==expected[i%45] for i,p in enumerate(points[start:])), 'Live device sequence mismatch'
frames=(last-first)&0o777777
assert state[10], 'CPU unexpectedly halted'
report=dict(snapshot=str(snap),points=len(points),complete_frames=len(points[start:])//45,frame_counter_delta=frames,elapsed_seconds=elapsed,mean_frame_ms=elapsed*1000/frames,run=bool(state[10]),pc=f'{state[2]:06o}',intensity_fields=dict(collections.Counter((w>>20)&7 for w in words)),limits='Mean from frame counter; no worst-case refresh or visual rendering claim.')
(build/'live-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
