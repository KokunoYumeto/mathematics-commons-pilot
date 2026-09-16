"""Exact finite and stable band constructions, with original source labels."""
from __future__ import annotations
from collections import Counter
import geometry as G


def band(d: int, h: int, shift: int, y: int) -> tuple[int, int]:
    G.parameters(d, h)
    G.require(type(shift) is int and 0 <= shift <= G.triangular(d)-h, 'Shift outside proved range')
    G.require(type(y) is int and 1 <= y <= 2*h+d, 'Band index out of range')
    if y <= h:
        return 1-2*y-G.block(y+shift), y
    return y-3*h-d+1, min(h, 2*h+d-y)


def packing(d: int, h: int, shift: int | None = None) -> tuple:
    G.parameters(d, h)
    if shift is None:
        shift = G.triangular(d)-h
    out = []
    for y in range(1, 2*h+d+1):
        x, q = band(d, h, shift, y)
        for j in range(q):
            t = G.tile('H', x+3*j, y)
            out.extend(G.reflect_tile(G.rotate_tile(t, p)) for p in range(3))
    return tuple(sorted(out))


def stable_owner(delta: int, cell: tuple) -> tuple | None:
    """Return (sector, original band y, bone index j, original placed tile)."""
    G.require(type(delta) is int and delta >= 0, 'Nonnegative integer invariant required')
    z = G.reflect(cell)
    for p in range(3):
        x, y = z
        if y >= 1:
            left = 1-2*y-G.block(y+delta)
            if left <= x <= y-G.block(y+delta):
                j = (x-left)//3
                t = G.tile('H', left+3*j, y)
                out = G.reflect_tile(G.rotate_tile(t, p))
                G.require(cell in out[1], 'Stable owner did not return original cell')
                return p, y, j, out
        z = G.rho(G.rho(z))
    return None


def base_stones(k: int) -> tuple:
    G.require(type(k) is int and k >= 1, 'Positive original core parameter required')
    return tuple(G.tile('R', k-2-2*r-s, r-s) for r in range(k-1) for s in range(k-1-r))


def triangular_family(d: int, k: int) -> tuple:
    G.require(type(d) is int and type(k) is int and d >= 3 and 1 <= k <= d, 'Use 1<=k<=d,d>=3')
    h = G.triangular(d)-G.triangular(k)
    return packing(d,h) + base_stones(k)


def first_collar(m: int) -> tuple:
    """The complete original turn-1 table, not a new claim of that result."""
    G.require(type(m) is int and m >= 3, 'Original first-collar domain m>=3')
    inner = tuple((k, tuple(sorted((x-2,y+1) for x,y in cs))) for k,cs in base_stones(m))
    remove = G.tile('R',-2,3-m)
    G.require(inner.count(remove)==1,'Reserved original stone missing')
    bones = [G.tile('D',-2,3-m),G.tile('D',-2,4-m),G.tile('D',-1,1-m),G.tile('V',1,-m)]
    bones += [G.tile('H',-m-1+2*r,m+1-r)for r in range(m)]
    bones += [G.tile('H',r,3-m+r)for r in range(m-1)]
    bones += [G.tile('V',r+2,r-m)for r in range(m)]
    return tuple(t for t in inner if t!=remove)+tuple(bones)


def minus_one_family(d: int, m: int) -> tuple:
    G.require(type(d) is int and type(m) is int and 3 <= m <= d, 'Use 3<=m<=d')
    delta=G.triangular(m)-1
    h=G.triangular(d)-delta
    if d==m:
        return first_collar(m)
    core=G.region(m,1)
    out=[]
    for t in packing(d,h):
        overlap=set(t[1]) & core
        G.require(not overlap or len(overlap)==3, 'A band crossed the proved core interface')
        if not overlap:
            out.append(t)
    return tuple(out)+first_collar(m)


def one_stone_bands(d: int):
    G.require(type(d) is int and d>=3,'Use d>=3')
    for r in range(d-2,0,-1):
        y=r*(r+1)//2
        old=tuple(G.tile('H',1-r*r+3*j,y)for j in range(y))
        new=tuple(G.tile('H',2-r*r+3*j,y)for j in range(y))
        for p in range(3):
            yield r,p,tuple(G.rotate_tile(t,p)for t in old),tuple(G.rotate_tile(t,p)for t in new)


def one_stone_transport(d: int) -> tuple:
    h=G.triangular(d)-1
    current=set(packing(d,h,0))
    for r,p,old,new in one_stone_bands(d):
        G.require(len(old)==len(new) and set(old)<=current,'An original transport band is missing')
        current.difference_update(old)
        G.require(not(current & set(new)),'Repeated target bone')
        current.update(new)
    return tuple(sorted(current))+(G.tile('R',0,0),)


def certificate_threshold(delta: int, released: tuple) -> tuple[int, int]:
    rows=[]
    for t in released:
        owner=stable_owner(delta,t[1][0])
        G.require(owner is not None and owner[3]==t,'Release is not an original stable-source bone')
        rows.append(owner[1])
    Y=max(rows,default=0)
    d=3
    while G.triangular(d)-delta < Y:
        d+=1
    return d,Y


def apply_certificate(d: int, record: dict) -> tuple:
    delta=record['delta'];h=G.triangular(d)-delta
    A=G.decode_anchors(record['released']);B=G.decode_anchors(record['replacement'])
    D,Y=certificate_threshold(delta,A)
    G.require(d>=D,'Below the exact stable-source threshold')
    source=packing(d,h)
    G.require(len(set(A))==len(A) and set(A)<=set(source),'Original release subset not present')
    return tuple(t for t in source if t not in set(A))+B
