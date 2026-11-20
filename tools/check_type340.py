"""Execute actual assembled PDP-1 native display-list builders, then decode them."""
import json,os,random,re,subprocess,sys
from pathlib import Path
from rim import tape_memory,write_mem,read_mem
from type340_model import read_lists,decode,label
root=Path(__file__).resolve().parents[1];build=root/'build'
sys.path.insert(0,str(root/'reference'))
from gcircle import circle_points
from gline import line_points
includes='''#include "../src/gplot.am1"
#include "../src/gline.am1"
#include "../src/gcircle.am1"
#include "../src/gtext.am1"
#include "../src/gframe.am1"
constants
before_guard, 0654321
buffer, 0
buffer + 0d512/
guard, 0123456
assert . < 07751, "test exceeds one bank"
start go
'''
results=[]
def run(name,body='',data='',fault=0,source=None,defines=()):
    source=source or 'P1GL Type 340 CPU test\n100/\ngo, lem\nlsm\ncbs\n'+body+'hlt\n'+data+includes
    (build/'native-check.am1').write_text(source)
    subprocess.run([os.environ.get('AM1','am1'),'-d',*['-D'+d for d in defines],'native-check.am1'],cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'native-check.rim');write_mem(build/'native.mem',mem)
    (build/'empty.mem').write_text('')
    cpu=subprocess.run([str(build/'type340_runner'),'native.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    assert 'overflow=0' in cpu.stdout,(name,cpu.stdout)
    ls=read_lists(build/'lists.trace');decoded=[decode(w) for w in ls]
    out=read_mem(build/'output.mem');sy={}
    for line in (build/'native-check.sym').read_text().splitlines():
        f=line.split()
        if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
    assert out[sy['gf_fault']]==fault,(name,out[sy['gf_fault']],fault)
    for guard,value in (('guard',0o123456),('buffer_guard',0o123456),('before_guard',0o654321)):
        if guard in sy:assert out[sy[guard]]==value,(name,guard)
    results.append(dict(name=name,lists=len(ls),words=sum(map(len,ls)),fault=fault))
    return decoded,out,sy

def flattened(items,key):return [v for d in items for v in d[key]]
def begin(n=512):return f'jda gframe_begin\nbuffer\n0d{n}\n'
finish='jsp gframe_end\njsp gframe_refresh\n'
p='jda gplot\n0d512\n0d512\n'
t='jda gtext\n0d100\n0d200\n2\nmessage\n'
message='message, ascii "A"\n'
d,_,_=run('empty',begin()+finish);assert len(d)==1 and d[0]['words']==3
assert not run('silent-build',begin()+p+t,data=message)[0]
d,_,_=run('exact-fit-point-char',begin(10)+t+p+finish,data=message)
assert flattened(d,'points')==[(512,512)] and flattened(d,'chars')==label(100,200,2,'A')
for name,body,err in [('point-overflow',begin(4)+p+finish,2),('char-overflow',begin(7)+t+finish,2),('partial-scene',begin(9)+p+t+finish,2),('refresh-unfinished',begin()+p+'jsp gframe_refresh\n',3),('zero-capacity',begin(0)+finish,1),('cross-bank','jda gframe_begin\n07776\n3\n'+finish,1)]:
    assert not run(name,body,data=message,fault=err)[0]
for name,body in [('end-without-begin','jsp gframe_end\n'),('refresh-without-scene','jsp gframe_refresh\n')]:
    assert not run(name,body,fault=3)[0]
d,_,_=run('repeat-and-immediate',begin()+p+finish+'jda gplot\n0\n0\njsp gframe_refresh\n')
assert flattened(d,'points')==[(512,512),(0,0),(512,512)]
d,_,_=run('recovery',begin(3)+p+'jsp gframe_end\n'+begin()+t+finish,data=message)
assert flattened(d,'chars')==label(100,200,2,'A')
# All true device coordinates including zero, in chunks small enough for code+buffer.
for off in range(0,1024,128):
    body=''.join(f'jda gplot\n0d{x}\n0d{1023-x}\n' for x in range(off,off+128))
    d,_,_=run(f'coordinate-{off}',body)
    assert flattened(d,'points')==[(x,1023-x) for x in range(off,off+128)]
# Hardware vectors: bounded components, connected segment endpoints on reference line.
rng=random.Random(0x340)
lines=[(512,512,512+dx,512+dy) for dx in range(-8,9) for dy in range(-8,9)]
lines += [(0,0,1023,1023),(1023,0,0,1023),(0,512,1023,512),(512,0,512,1023)]
for _ in range(128):
    a=tuple(rng.randrange(1024) for _ in range(4));lines.extend((a,(a[2],a[3],a[0],a[1])))
for off in range(0,len(lines),8):
    batch=lines[off:off+8]
    body=''.join('jda gline\n'+''.join(f'0d{n}\n' for n in a) for a in batch)
    d,_,_=run(f'lines-{off}',body);assert len(d)==len(batch)
    for decoded,a in zip(d,batch):
        assert decoded['points']==[a[:2]]
        pts=line_points(*a);ends=pts[127::127]
        if len(pts)>1 and (not ends or ends[-1]!=pts[-1]):ends.append(pts[-1])
        start=a[:2]
        assert decoded['vectors']==list(zip([start]+ends[:-1],ends)),(a,decoded['vectors'],ends)
# Exact midpoint circles including clipped bounds, streamed immediate lists.
cases=[(512,512,r) for r in range(129)]
for cx,cy in ((0,0),(0,512),(512,0),(1023,0),(1023,512),(512,1023),(0,1023),(1023,1023)):
    cases += [(cx,cy,r) for r in (0,1,2,3,16,31,127,511,512,1023)]
cases += [tuple(rng.randrange(1024) for _ in range(3)) for _ in range(64)]
cases += [(512,512,r) for r in (511,512,724,1023)]
for i,a in enumerate(cases):
    d,_,_=run(f'circle-{i}','jda gcircle\n'+''.join(f'0d{v}\n' for v in a))
    assert flattened(d,'points')==circle_points(*a),(a,len(flattened(d,'points')))
# Printable ASCII and unsupported/control replacements, scales and bounds.
for size in range(4):
    chars=''.join(chr(c) for c in range(32,127));body='';data='';expected=[]
    for i,c in enumerate(chars):
        body+=f'jda gtext\n0d100\n0d200\n{size}\nstr{i}\n'
        data+=f'str{i}, ascii '+json.dumps(c)+'\n';expected+=label(100,200,size,c)
    d,_,_=run(f'ascii-scale-{size}',body,data=data)
    assert flattened(d,'chars')==expected
for name,x,y,size,text in [('descender-clip',100,0,2,'AgjpqyB'),('right-clip',1000,500,2,'AB'),('top-clip',100,1020,3,'A'),('zero-origin',0,0,0,'A'),('empty',100,200,2,'')]:
    d,_,_=run(name,f'jda gtext\n0d{x}\n0d{y}\n{size}\nmessage\n',data='message, ascii '+json.dumps(text)+'\n')
    assert flattened(d,'chars')==label(x,y,size,text)
run('bad-text-size',begin()+t.replace('\n2\n','\n4\n')+finish,data=message,fault=1)
run('unterminated-text',begin()+t+finish,data='message, ascii "'+('A'*257)+'"\n',fault=1)
# The exact combined demo must use native vectors/characters, no Type 30/33 IOTs.
d,out,sy=run('actual-demo',source=(root/'examples/frame_demo.am1').read_text(),defines=('DEMO_CPU_TEST',))
assert len(d)==3 and out[sy['frames']]==3 and out[sy['fault']]==0
for i,(item,r) in enumerate(zip(d,(96,128,160)),1):
    assert item['points']==circle_points(512,512,r)+[(512,512),(512,512)]
    assert item['vectors'][-1][1]==(512+r,512)
    assert item['chars']==label(330,840,2,'P1GL TYPE 340')+label(414,140,2,f'FRAME {i}')
# Standalone native line and full-resolution circle screens.
ld,lo,ls=run('line-demo',source=(root/'examples/line_demo.am1').read_text(),defines=('DEMO_CPU_TEST',))
assert len(ld)==32 and lo[ls['frames']]==32 and lo[ls['fault']]==0
for item in ld: assert item['vectors'] and item['chars']==label(288,840,2,'TYPE 340 LINES')
cd,co,cs=run('circle-demo',source=(root/'examples/circle_demo.am1').read_text(),defines=('DEMO_CPU_TEST',))
circle_demo=[(512,512,r) for r in (64,96,128,160)]+[(0,512,96),(1023,512,96),(512,0,96),(512,1023,96),(0,0,128),(1023,1023,128),(512,512,0)]
assert len(cd)==11 and co[cs['frames']]==11 and co[cs['fault']]==0
for item,a in zip(cd,circle_demo):
    assert item['points']==circle_points(*a)
    assert item['chars']==label(288,840,2,'TYPE 340 CIRCLES')
report=dict(executions=len(results),line_cases=len(lines),circle_cases=len(cases),coordinate_cases=1024,display_lists=sum(r['lists'] for r in results),native_words=sum(r['words'] for r in results),demo_words=[a['words'] for a in d],scope='CPU plus structural native decoder; hardware vector pixels, glyph rendering and real timing require live tests',results=results)
(build/'type340-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
