"""Geometric properties independent of the circle recurrence and device code."""
import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'))
from gcircle import circle_points

def test_circle_symmetry_and_radial_error():
    for r in range(0,129):
        points=circle_points(512,512,r);s=set(points)
        assert len(s)==len(points),(r,'duplicate')
        assert s
        for x,y in s:
            dx,dy=x-512,y-512
            assert abs(math.hypot(dx,dy)-r)<=0.5+1e-12,(r,dx,dy)
            for a,b in ((dx,dy),(-dx,dy),(dx,-dy),(-dx,-dy),(dy,dx),(-dy,dx),(dy,-dx),(-dy,-dx)):
                assert (512+a,512+b) in s

def test_circle_axes_and_zero():
    assert circle_points(512,512,0)==[(512,512)]
    assert set(circle_points(512,512,1))=={(511,512),(513,512),(512,511),(512,513)}
    for r in (2,3,16,100,511):
        s=set(circle_points(512,512,r))
        assert {(512-r,512),(512+r,512),(512,512-r),(512,512+r)}<=s

def test_circle_clipping():
    for cx,cy in ((0,0),(0,512),(1023,512),(512,0),(512,1023),(1023,1023)):
        for r in (0,1,2,16,511,1023):
            p=circle_points(cx,cy,r)
            assert len(p)==len(set(p))
            assert all(0<=x<=1023 and 0<=y<=1023 for x,y in p)
            assert all(abs(math.hypot(x-cx,y-cy)-r)<=0.5+1e-12 for x,y in p)

def test_circle_invalid_inputs():
    for a in ((-1,0,1),(512,512,-1),(1024,0,1),(512,512,1024),(512,512,1.0),(True,512,1)):
        try: circle_points(*a)
        except ValueError: pass
        else: raise AssertionError(a)
