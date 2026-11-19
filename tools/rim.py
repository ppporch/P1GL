"""AM1 RIM decoder, from SignalAnalysis/tests/test_core.py."""
import re
def tape_memory(path, parts=False):
    """Decode the actual RIM bootstrap followed by AM1 address/end/data blocks."""
    holes=[b & 63 for b in path.read_bytes() if b & 128]
    assert len(holes)%3 == 0
    words=[(holes[i]<<12)|(holes[i+1]<<6)|holes[i+2] for i in range(0,len(holes),3)]
    mem={}
    i=0
    while words[i] != 0o607751:
        assert words[i]&0o770000 == 0o320000, 'Unexpected RIM bootstrap'
        addr=words[i]&0o7777
        assert addr not in mem
        mem[addr]=words[i+1]
        i+=2
    i+=1
    bootstrap=dict(mem)
    stream=words[i:]
    while True:
        begin=words[i];i+=1
        if begin & 0o400000:
            assert not begin & 0o200000, 'Expected START, not STOP'
            assert i==len(words), 'Trailing binary words'
            if parts: return bootstrap,stream,begin & 0o177777
            return mem, begin & 0o177777
        end=words[i];i+=1
        assert 0<=begin<end<=65536
        for addr in range(begin,end):
            assert addr not in mem, f'Overlapping tape block at {addr:o}'
            mem[addr]=words[i];i+=1

def listing_memory(path):
    pat=re.compile(r'^\s*\d+:\s+([0-7]{6})\s+([0-7]{6})(?:\s|$)')
    return {int(m[1],8):int(m[2],8) for line in path.read_text().splitlines() if (m:=pat.match(line))}

def write_mem(path, values):
    path.write_text(''.join(f'{a:06o}: {w:06o}\n' for a,w in sorted(values.items())))

def read_mem(path):
    return {int(a,8):int(w,8) for a,w in (line.split(':') for line in path.read_text().splitlines())}
