"""Execute banked Hershey text; compare native geometry with source-font strokes."""
import json,os,re,subprocess,sys
from pathlib import Path
from rim import tape_memory,write_mem,read_mem
from type340_model import read_lists,decode,label
from generate_vfont import load_font
root=Path(__file__).resolve().parents[1];build=root/'build'
sys.path.insert(0,str(root/'reference'))
from gline import line_points
font={chr(g['ascii']):g for g in load_font()}

def geometry(x,y,size,text):
    points=[];vectors=[];scale=1<<size
    for c in text:
        if c not in font:c='?'
        g=font[c];a,b,d,e=g['bounds']
        if 0<=x+a*scale and x+b*scale<=1023 and 0<=y+d*scale and y+e*scale<=1023:
            for stroke in g['strokes']:
                pts=[(x+px*scale,y+py*scale) for px,py in stroke]
                if len(pts)==1:points.append(pts[0])
                for p,q in zip(pts,pts[1:]):
                    points.append(p)
                    path=line_points(*p,*q);ends=path[127::127]
                    if len(path)>1 and (not ends or ends[-1]!=path[-1]):ends.append(path[-1])
                    vectors+=list(zip([p]+ends[:-1],ends))
        x+=g['advance']*scale
    return points,vectors

includes='''#include "../src/gplot.ac"
#include "../src/gline.ac"
#include "../src/gtext.ac"
#include "../src/gframe.ac"
#include "../src/gvtext.ac"
constants
before_guard, 0654321
buffer, 0
buffer + 0d512/
guard, 0123456
assert . < 07751, "test code bank overflow"
start go:0
'''
results=[]
def run(name,body='',data='',fault=0,source=None,defines=()):
    (build/'vtext-check.am1').write_text(source or 'P1GL executed stroke text test\n100/\ngo, lem\nlsm\ncbs\n'+body+'hlt\n'+data+includes)
    subprocess.run([os.environ.get('AM1','am1'),'-d',*['-D'+d for d in defines],'vtext-check.am1'],cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'vtext-check.rim');write_mem(build/'vtext.mem',mem)
    (build/'empty.mem').write_text('')
    cpu=subprocess.run([str(build/'type340_runner'),'vtext.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    assert 'overflow=0' in cpu.stdout and 'extend=0' in cpu.stdout,(name,cpu.stdout)
    ds=[decode(w) for w in read_lists(build/'lists.trace')]
    out=read_mem(build/'output.mem');sy={}
    for line in (build/'vtext-check.sym').read_text().splitlines():
        f=line.split()
        if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
    assert out[sy['gf_fault']]==fault,(name,out[sy['gf_fault']],fault)
    for guard,v in (('guard',0o123456),('buffer_guard',0o123456),('before_guard',0o654321)):
        if guard in sy:assert out[sy[guard]]==v,(name,guard)
    # Font data is read only: no metadata or vertex word may change.
    assert all(out[a]==w for a,w in mem.items() if a>=4096),(name,'font bank changed')
    results.append(dict(name=name,lists=len(ds),vectors=sum(len(d['vectors']) for d in ds),fault=fault))
    return ds,out,sy

def flat(ds,k):return [v for d in ds for v in d[k]]
def call(x,y,size,string='message'):return f'jda gvtext\n0d{x}; 0d{y}; {size}; {string}\n'
def check(name,x,y,size,text,defines=()):
    d,_,_=run(name,call(x,y,size),data='message, ascii '+json.dumps(text)+'\n',defines=defines)
    p,v=geometry(x,y,size,text)
    assert flat(d,'points')==p,(name,'points',flat(d,'points')[:4],p[:4])
    assert flat(d,'vectors')==v,(name,'vectors',flat(d,'vectors')[:3],v[:3])
    assert not flat(d,'chars'),name

check('first-A',100,200,1,'A')
# Every printable glyph at all scales, positioned independently so none is clipped.
for size in range(4):
    body='';data='';points=[];vectors=[]
    for i in range(95):
        c=chr(32+i);body+=call(128,400,size,f'm{i}');data+=f'm{i}, ascii '+json.dumps(c)+'\n'
        p,v=geometry(128,400,size,c);points+=p;vectors+=v
    d,_,_=run(f'all-ascii-scale-{size}',body,data=data)
    assert flat(d,'points')==points and flat(d,'vectors')==vectors
    assert not flat(d,'chars')
for name,x,y,size,text in [('mixed-case',100,200,1,'PiDP-1'),('true-zero',0,0,0,'A'),('descenders',100,0,0,'AgjpqyB'),('top-clipping',100,1020,1,'ABC'),('right-clipping',1000,200,1,'ABC'),('caret-and-grave',100,200,1,'^`'),('empty',100,200,1,''),('odd-string',100,200,1,'ABC'),('even-string',100,200,1,'AB'),('punctuation',100,200,0,'!?@#[]{}~|')]:
    check(name,x,y,size,text)
check('alternate-font-bank',100,200,1,'P1GL',defines=('P1GL_FONT_BANK=3',))
check('highest-font-bank',100,200,1,'P1GL',defines=('P1GL_FONT_BANK=0xf',))
# Retained frame and recovery are verified without new drawing during build.
begin='jda gframe_begin\nbuffer; 0d512\n';finish='jsp gframe_end\njsp gframe_refresh\n'
d,_,_=run('silent-build',begin+call(100,200,1),data='message, ascii "A"\n');assert not d
d,_,_=run('retained-twice',begin+call(100,200,1)+finish+'jsp gframe_refresh\n',data='message, ascii "A"\n')
p,v=geometry(100,200,1,'A');assert flat(d,'points')==p*2 and flat(d,'vectors')==v*2
assert not run('capacity-failure','jda gframe_begin\nbuffer; 0d8\n'+call(100,200,1)+finish,data='message, ascii "A"\n',fault=2)[0]
run('invalid-size',call(100,200,4),data='message, ascii "A"\n',fault=1)
run('invalid-position',call(1024,200,1),data='message, ascii "A"\n',fault=1)
run('string-limit',begin+call(100,200,0)+finish,data='message, ascii "'+(' '*257)+'"\n',fault=1)
# Actual four-page demo, one replay per page, including native-text coexistence.
d,o,s=run('actual-demo',source=(root/'examples/vector_text_demo.ac').read_text(),defines=('DEMO_CPU_TEST',))
assert len(d)==4 and o[s['frames']]==4 and o[s['fault']]==0
bodies=[(335,590,1,'Vector Text'),(255,590,0,'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),(291,590,0,'abcdefghijklmnopqrstuvwxyz'),(304,590,0,'0123456789  !?+-=/()[]')]
for i,(item,b) in enumerate(zip(d,bodies)):
    p,v=geometry(354,800,2,'P1GL');p2,v2=geometry(*b);p+=p2;v+=v2
    if i==0:
        p2,v2=geometry(361,440,0,'Continuous strokes');p+=p2;v+=v2
    assert item['points']==p and item['vectors']==v,(i,'demo geometry')
    assert item['chars']==label(302,180,2,'NATIVE TYPE 342')
report=dict(executions=len(results),glyphs=95,scales=4,vectors=sum(r['vectors'] for r in results),demo_words=[a['words'] for a in d],font_bank=1,read_only_font_verified=True,ordinary_mode_restored=True,scope='real CPU, source-font geometry and native-list decoder; live rendering is separate',results=results)
(build/'vector-text-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
