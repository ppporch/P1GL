"""Midpoint circle geometry reference; integer logical viewport 0..1023."""
def circle_points(cx,cy,radius):
    if any(type(v) is not int or not 0<=v<=1023 for v in (cx,cy,radius)):
        raise ValueError('center and radius must be integers 0..1023')
    x,y,d=radius,0,1-radius
    points=[]
    while y<=x:
        candidates=[(cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                    (cx+y,cy+x),(cx+y,cy-x),(cx-y,cy+x),(cx-y,cy-x)]
        seen=set()
        for p in candidates:
            if p not in seen and all(0<=v<=1023 for v in p): points.append(p)
            seen.add(p)
        y+=1
        if d<0: d+=2*y+1
        else:
            x-=1
            d+=2*(y-x)+1
    return points
