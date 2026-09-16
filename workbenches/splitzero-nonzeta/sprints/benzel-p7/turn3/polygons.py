"""Exact original-cell / three-polygon maps, including every allowed tile phase."""
OFFSETS = ((0,0),(1,0),(0,1))
TILE_OFFSETS = {'R': OFFSETS, 'D': ((0,0),(1,-1),(2,-2)),
                'H': ((0,0),(1,0),(2,0)), 'V': ((0,0),(0,1),(0,2))}

def to_cell(d, r, s, phase):
    a,b = OFFSETS[phase]
    return d-2-2*r-s+a, r-s+b

def from_cell(d, x, y):
    phase = (x+2*y-(d-2)) % 3
    a,b = OFFSETS[phase]
    rnum = y-x+d-2-b+a
    snum = 1-x-2*y+d-3+a+2*b
    if rnum % 3 or snum % 3: raise ValueError('Nonintegral coordinate inverse')
    return rnum//3, snum//3, phase

def in_polygon(d,h,r,s,phase):
    R,S = r+h,s+h
    upper_R = d+2*h-(2 if phase==2 else 1)
    upper_S = d+2*h-(2 if phase==0 else 1)
    lower_sum = h if phase==1 else h-1
    return (0<=R<=upper_R and 0<=S<=upper_S
            and lower_sum<=R+S<=d+3*h-2)

def tile_image(kind, phase):
    """Return (output_phase, delta_r, delta_s) for each original tile cell."""
    a,b = OFFSETS[phase]; result=[]
    for u,v in TILE_OFFSETS[kind]:
        q=(phase+u+2*v)%3; c,e=OFFSETS[q]
        x,y=a+u-c,b+v-e
        if (y-x)%3 or (-x-2*y)%3:raise ValueError('Tile transport not integral')
        result.append((q,(y-x)//3,(-x-2*y)//3))
    return tuple(result)

def count_per_phase(d,h):
    def choose2(n):return n*(n-1)//2
    return choose2(d+3*h)-2*choose2(h)-choose2(h+1)
