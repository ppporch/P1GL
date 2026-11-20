"""Execute the non-owning vector emitter with an AC-clobbering output sink."""
import json,math,os,random,re,subprocess
from pathlib import Path
from rim import tape_memory,write_mem,read_mem
from type340_model import read_lists,decode
root=Path(__file__).resolve().parents[1];build=root/'build'
rng=random.Random(340127)
cases=[(0,0)]
for n in range(0,1024):
    cases += [(0,n),(0,-n),(n,0),(-n,0)]
for dx in (-1023,-382,-128,-127,-3,-1,0,1,3,127,128,382,1023):
    for dy in (-1023,-382,-128,-127,-1,0,1,127,128,382,1023):cases.append((dx,dy))
cases += [(rng.randrange(-1023,1024),rng.randrange(-1023,1024)) for _ in range(256)]
max_words=0;max_deviation=0;tested=0
for offset in range(0,len(cases),32):
    batch=cases[offset:offset+32]
    s='P1GL streaming vector tests\n#include "../src/type340.ah"\n100/\ngo, lem\nlsm\ncbs\n'
    for dx,dy in batch:
        x0=max(0,-dx);y0=max(0,-dy)
        s+=f'''law output + 3
dac sink_pointer
lac [0d{y0} | T_Y | T_POINT]
dac output + 1
lac [0d{x0} | T_VECTOR]
dac output + 2
lac [{('-' if dx<0 else '')}0d{abs(dx)}]
dac p1gl_vdx
lac [{('-' if dy<0 else '')}0d{abs(dy)}]
dac p1gl_vdy
lac [T_END]
dac p1gl_vtail
jsp p1gl_vector
lac p1gl_vfault
sza
jmp bad
lac [T_HALT]
dac i sink_pointer
lio [output]
iot 015
'''
    s+='''hlt
bad, hlt
sink_pointer, 0
#define P1GL_VECTOR_EMIT dac i sink_pointer; idx sink_pointer
#include "../src/vector_sink.ac"
constants
output, T_SETUP
0
0
output + 0d24/
guard, 0123456
start go
'''
    (build/'sink-check.am1').write_text(s)
    subprocess.run([os.environ.get('AM1','am1'),'-d','sink-check.am1'],cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'sink-check.rim');write_mem(build/'sink.mem',mem)
    (build/'empty.mem').write_text('')
    cpu=subprocess.run([str(build/'type340_runner'),'sink.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    assert 'overflow=0' in cpu.stdout,cpu.stdout
    lists=read_lists(build/'lists.trace');assert len(lists)==len(batch),(offset,len(lists))
    for words,(dx,dy) in zip(lists,batch):
        ds=decode(words);vs=ds['vectors'];assert 1<=len(vs)<=16
        assert vs[-1][1]==(max(0,-dx)+dx,max(0,-dy)+dy)
        raw=words[3:-1];assert len(raw)==len(vs)
        assert all(w&0o200000 for w in raw)
        assert all(not w&0o400000 for w in raw[:-1]) and raw[-1]&0o400000
        for i,(a,b) in enumerate(vs):
            assert max(abs(b[0]-a[0]),abs(b[1]-a[1]))<=127
            if i:assert a==vs[i-1][1]
            if dx:assert (b[0]-a[0])*dx>=0
            if dy:assert (b[1]-a[1])*dy>=0
            if dx or dy:
                ex=b[0]-max(0,-dx);ey=b[1]-max(0,-dy)
                dev=abs(dy*ex-dx*ey)/math.hypot(dx,dy)
                max_deviation=max(max_deviation,dev);assert dev<=2.0+1e-12
        if dx==0 or dy==0:assert len(vs)==max(1,math.ceil(max(abs(dx),abs(dy))/127))
        max_words=max(max_words,len(vs));tested+=1
# Invalid input must not call the output sink or leave partial commands.
invalid=[(1024,0,0),(0,1024,0),(-1024,0,0),(0,-1024,0),(0,0,1)]
for dx,dy,tail in invalid:
    s='P1GL rejected vector arguments\n100/\ngo, lem\nlsm\ncbs\nlaw output + 3\ndac sink_pointer\n'
    for name,value in [('p1gl_vdx',dx),('p1gl_vdy',dy),('p1gl_vtail',tail)]:
        s+=f'lac [{"-" if value<0 else ""}0d{abs(value)}]\ndac {name}\n'
    s+='jsp p1gl_vector\nhlt\nsink_pointer, 0\n#define P1GL_VECTOR_EMIT dac i sink_pointer; idx sink_pointer\n#include "../src/vector_sink.ac"\nconstants\noutput, 0\noutput + 0d24/\nguard, 0123456\nstart go\n'
    (build/'sink-check.am1').write_text(s)
    subprocess.run([os.environ.get('AM1','am1'),'-d','sink-check.am1'],cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'sink-check.rim');write_mem(build/'sink.mem',mem)
    subprocess.run([str(build/'type340_runner'),'sink.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    out=read_mem(build/'output.mem');sy={}
    for line in (build/'sink-check.sym').read_text().splitlines():
        f=line.split()
        if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
    assert out[sy['p1gl_vfault']]==1 and out[sy['p1gl_vcount']]==0
    assert out[sy['sink_pointer']]==sy['output']+3
    assert out[sy['guard']]==0o123456 and not read_lists(build/'lists.trace')
report=dict(cases=tested,rejected_cases=len(invalid),max_vector_words=max_words,max_split_endpoint_deviation_pixels=max_deviation,axis_chunk_limit=127,unit_spacing=True,tail_end_only_on_final_word=True,sink_clobbers_ac=True)
(build/'vector-sink-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
