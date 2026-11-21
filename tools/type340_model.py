"""Independent structural decoder of the native commands P1GL emits.
Checks points, vector endpoints, characters and bounds; it is NOT the real
Type 340 rate-multiplier rasterizer, glyph renderer, HSC, or timing model.
"""
from pathlib import Path

def read_lists(path):
    lists=[];current=None
    for line in Path(path).read_text().splitlines():
        if line.startswith('BEGIN '):
            assert current is None;current=[]
        elif line=='END':
            assert current is not None;lists.append(current);current=None
        else:current.append(int(line,8))
    assert current is None
    return lists

def decode(words):
    mode=0;x=y=0;scale=1;shift=0;points=[];vectors=[];chars=[];stop=False
    for i,w in enumerate(words):
        if mode==0:
            if w&0o2000:
                assert i==len(words)-1,'trailing words after HALT';stop=True;break
            if w&0o100:scale=1<<((w>>4)&3)
            mode=(w>>13)&7
            if mode==3:shift=0
        elif mode==7 and w >> 16 == 2:
            # The runner has already followed this jump in scan order.
            mode=(w>>13)&7
        elif mode==1:
            if w&0o200000:y=w&1023
            else:x=w&1023
            if w&0o2000:points.append((x,y))
            mode=(w>>13)&7
            if mode==3:shift=0
        elif mode==4:
            dx=(w&127)*scale*(-1 if w&0o200 else 1)
            dy=((w>>8)&127)*scale*(-1 if w&0o100000 else 1)
            end=(x+dx,y+dy)
            assert all(0<=v<=1023 for v in end),('vector edge',x,y,dx,dy)
            if w&0o200000:vectors.append(((x,y),end))
            x,y=end
            if w&0o400000:mode=0
        elif mode==3:
            for s in (12,6,0):
                c=(w>>s)&63
                if c==0o37:mode=0;break
                if c==0o35:shift=0;continue
                if c==0o36:shift=64;continue
                assert 0<=x and x+7*scale<=1023,('character advance edge',x,scale)
                assert 0<=y and y+6*scale<=1023,('character top edge',y,scale)
                if shift and c in (7,10,16,17,25):assert y-2*scale>=0,'descender edge'
                chars.append((x,y,scale,c+shift))
                x+=7*scale
        else:raise AssertionError(('unexpected mode',mode,oct(w)))
    assert stop,'unterminated list'
    return dict(points=points,vectors=vectors,chars=chars,words=len(words))

def char_code(c):
    if c in '^`' or not 32<=ord(c)<=126:c='?'
    shift=64 if c.islower() or c in '~\\[]{}_|' else 0
    if c.isalpha():code=ord(c.upper())-64
    elif 32<=ord(c)<=63:code=ord(c)
    elif c=='@':code=0
    else:code={'~':0o43,'\\':0o52,'[':0o53,']':0o54,'{':0o55,'}':0o56,'_':0o60,'|':0o62}[c]
    return code+shift

def label(x,y,size,text):
    out=[];scale=1<<size
    for c in text:
        code=char_code(c)
        if x+7*scale<=1023 and y+6*scale<=1023 and (c not in 'gjpqy' or y>=2*scale):
            out.append((x,y,scale,code))
        x+=7*scale
    return out
