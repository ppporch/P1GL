"""Executed frame/text checks: IOT transactions, geometry, lifecycle, bounds.
Type 33 events are captured, not rendered or timed by the CPU-only runner.
"""
import json,os,re,subprocess,sys
from pathlib import Path
from rim import tape_memory,write_mem,read_mem
root=Path(__file__).resolve().parents[1];build=root/'build'
sys.path.insert(0,str(root/'reference'))
from gcircle import circle_points
from gline import line_points
pdp=Path(os.environ.get('PDP1_ROOT','/opt/pidp1-mods'))
font_source=pdp/'Am1Includes/SYMGEN/ascchars.ac'
font=[tuple(int(v,8) for v in m) for m in re.findall(r'^\s*([0-7]{6});\s*([0-7]{6})',font_source.read_text(),re.M)]
assert len(font)==96

def raw(v):
    n=max(1,v)-512
    return n*256 if n>=0 else (~(-n*256))&0o777777

def point(x,y): return [(0o7,raw(x),raw(y),0o730207)]

def label(x,y,size,text):
    events=[];pitch=size+2
    for c in text:
        if x+4*pitch<=1023 and y+6*pitch<=1023:
            n=ord(c);n=n if 32<=n<=126 else 63
            a,b=font[n-32]
            events.extend(((0o26,None,size,0o722026),(0o7,raw(x),raw(y),0o722207),
                           (0o27,None,a,0o732027),(0o27,None,b,0o730027)))
        x+=6*pitch+2
    return events

results=[]
def execute(name,source,expected,fault=0,points=None,chars=None,defines=()):
    path=build/'frame-check.am1';path.write_text(source)
    command=[os.environ.get('AM1','am1'),'-d','-I'+str(pdp/'Am1Includes')]+['-D'+d for d in defines]+[path.name]
    subprocess.run(command,cwd=build,check=True,capture_output=True,text=True)
    mem,start=tape_memory(build/'frame-check.rim');write_mem(build/'frame.mem',mem)
    (build/'empty.mem').write_text('')
    run=subprocess.run([str(build/'plot_runner'),'frame.mem','empty.mem','output.mem',f'{start:o}'],cwd=build,check=True,capture_output=True,text=True)
    assert 'overflow=0' in run.stdout,(name,run.stdout)
    events=[tuple(int(w,8) for w in l.split()) for l in (build/'events.trace').read_text().splitlines()]
    events=[a for a in events if a[0] in (0o7,0o26,0o27)]
    assert len(events)==len(expected),(name,len(events),len(expected))
    for i,(actual,want) in enumerate(zip(events,expected)):
        assert all(v is None or v==a for a,v in zip(actual,want)),(name,i,actual,want)
    out=read_mem(build/'output.mem');sy={}
    for line in (build/'frame-check.sym').read_text().splitlines():
        f=line.split()
        if len(f)==4 and re.fullmatch('[0-7]{6}',f[0]):sy[f[2]]=int(f[0],8)
    assert out[sy['gf_fault']]==fault,(name,out[sy['gf_fault']],fault)
    if 'guard' in sy: assert out[sy['guard']]==0o123456,(name,'guard overwritten')
    if 'buffer_guard' in sy: assert out[sy['buffer_guard']]==0o123456,(name,'guard overwritten')
    if 'before_guard' in sy: assert out[sy['before_guard']]==0o654321,(name,'underflow')
    if points is not None: assert out[sy['gf_points']]==points,(name,'point count')
    if chars is not None: assert out[sy['gf_chars']]==chars,(name,'character count')
    results.append(dict(name=name,iot_events=len(events),fault=fault))

includes='''#include "../src/gplot.am1"
#include "../src/gframe.am1"
#include "../src/gtext.am1"
constants
before_guard, 0654321
buffer, 0
buffer + 0d512/
guard, 0123456
assert . < 07751, "test exceeds one bank"
start go
'''
def program(body,data=''):
    return 'P1GL executed frame contract test\n#define P1GL_FRAME\n100/\ngo, lem\nlsm\ncbs\n'+body+'hlt\n'+data+includes

def begin(n):return f'jda gframe_begin\nbuffer\n0d{n}\n'
end_refresh='jsp gframe_end\njsp gframe_refresh\n'
p='jda gplot\n0d512\n0d512\n'
t='jda gtext\n0d100\n0d200\n2\nmessage\n'
message='message, ascii "A"\n'
execute('empty',program(begin(512)+end_refresh),[],points=0,chars=0)
execute('recording-is-silent',program(begin(512)+p+t,message),[],points=1,chars=1)
execute('exact-fit-mixed-reordered',program(begin(7)+t+p+end_refresh,message),point(512,512)+label(100,200,2,'A'),points=1,chars=1)
execute('two-refreshes',program(begin(7)+p+t+end_refresh+'jsp gframe_refresh\n',message),(point(512,512)+label(100,200,2,'A'))*2,points=1,chars=1)
execute('point-overflow',program(begin(1)+p+end_refresh),[],fault=2)
execute('text-overflow',program(begin(4)+t+end_refresh,message),[],fault=2)
execute('partial-frame-is-not-replayed',program(begin(6)+p+t+end_refresh,message),[],fault=2)
execute('refresh-during-build',program(begin(512)+p+'jsp gframe_refresh\n'),[],fault=3)
execute('capacity-zero',program(begin(0)+p+end_refresh),[],fault=1)
execute('capacity-negative',program('jda gframe_begin\nbuffer\n0777777\n'+p+end_refresh),[],fault=1)
execute('buffer-crosses-bank',program('jda gframe_begin\n07777\n2\n'+p+end_refresh),[],fault=1)
execute('begin-clears-error-and-old-scene',program(begin(1)+p+'jsp gframe_end\n'+begin(512)+t+end_refresh,message),label(100,200,2,'A'),points=0,chars=1)
execute('immediate-outside-frame',program(p+t,message),point(512,512)+label(100,200,2,'A'))
execute('empty-text',program(begin(512)+t+end_refresh,'message, ascii ""\n'),[],points=0,chars=0)
execute('odd-packed-text',program(begin(512)+t+end_refresh,'message, ascii "Ab3"\n'),label(100,200,2,'Ab3'),chars=3)
execute('even-packed-text',program(begin(512)+t+end_refresh,'message, ascii "9?"\n'),label(100,200,2,'9?'),chars=2)
execute('unsupported-code-question',program(begin(512)+t+end_refresh,'message, 0777000\n'),label(100,200,2,'?'),chars=1)
execute('text-right-clipping',program(begin(512)+t.replace('0d100','0d1020')+end_refresh,message),[],chars=0)
execute('text-top-clipping',program(begin(512)+t.replace('0d200','0d1020')+end_refresh,message),[],chars=0)
execute('text-exact-right-edge',program(begin(512)+t.replace('0d100','0d1007')+end_refresh,message),label(1007,200,2,'A'),chars=1)
execute('invalid-size',program(begin(512)+t.replace('\n2\n','\n4\n')+end_refresh,message),[],fault=1)
execute('unterminated-limit',program(begin(512)+t+end_refresh,'message, ascii "'+('A'*257)+'"\n'),[],fault=1)
# Every printable character, positioned on three visible rows.
body=begin(512);data='';expected=[]
allchars=''.join(chr(n) for n in range(32,127))
for i in range(3):
    text=allchars[i*32:(i+1)*32];y=500-i*50
    body+=f'jda gtext\n0d100\n0d{y}\n0\nrow{i}\n'
    data+=f'row{i}, ascii '+json.dumps(text)+'\n'
    expected+=label(100,y,0,text)
execute('all-printable-ascii',program(body+end_refresh,data),expected,chars=95)
# Actual combined demo: one replay per scene. Geometry is magnified in the app.
expected=[]
for i,r in enumerate((12,16,20),1):
    geom=circle_points(512,512,r)+line_points(512,512,512+r,512)
    for x,y in geom: expected+=point(512+(x-512)*8,512+(y-512)*8)
    expected+=point(512,512)
    expected+=label(304,840,3,'P1GL GRAPHICS')+label(420,140,2,f'FRAME {i}')
execute('combined-frame-demo', (root/'examples/frame_demo.am1').read_text(), expected,points=len(circle_points(512,512,20))+21+1,chars=20,defines=('DEMO_CPU_TEST',))
report=dict(cases=len(results),iot_events=sum(r['iot_events'] for r in results),results=results,font_source=str(font_source),timing='IOT transaction capture only; real character generation and pacing require live test')
(build/'frame-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
