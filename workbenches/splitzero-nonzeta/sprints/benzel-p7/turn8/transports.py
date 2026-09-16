"""Explicit original bone-band chain homotopies and finite jet observations.

These are exact cell identities. Their use as positive replacements requires
an original source support and current holes; no global positive completion
of the two remaining residue classes is claimed by this module.
"""
from __future__ import annotations
from collections import Counter
import geometry as G


def jet(vector):
    # Original quotient observation X->1+e, Y->1+f,
    # e^2=ef=f^2=0, characteristic 3. Negative exponents are retained.
    return (sum(vector.values())%3,
            sum(x*n for (x,y),n in vector.items())%3,
            sum(y*n for (x,y),n in vector.items())%3)

def difference(new,old):
    out=Counter(G.incidence(new));out.subtract(G.incidence(old))
    return {p:n for p,n in out.items() if n}

def band(kind,x:int,y:int,n:int):
    G.require(all(type(a)is int for a in (x,y,n))and n>=0,'Original integer band required')
    old=[];new=[];end=Counter()
    if kind=='V_to_H':
        for i in range(n):
            old.append(G.tile('V',x+i,y+i));new.append(G.tile('H',x+i-1,y+i+1))
        for dx,dy,c in [(n,n,1),(n-1,n+1,-1),(0,0,-1),(-1,1,1)]:end[(x+dx,y+dy)]+=c
    elif kind=='H_to_D':
        for i in range(n):
            old.append(G.tile('H',x+2*i,y-i));new.append(G.tile('D',x+2*i,y-i+1))
        for dx,dy,c in [(0,1,1),(0,0,-1),(2*n,-n+1,-1),(2*n,-n,1)]:end[(x+dx,y+dy)]+=c
    elif kind=='VV_to_DD':
        for i in range(n):
            old.extend((G.tile('V',x+i,y+i),G.tile('V',x+i,y+i+3)))
            new.extend((G.tile('D',x+i-2,y+i+2),G.tile('D',x+i-2,y+i+3)))
        for dx,dy in [(-1,4),(-1,3),(-1,2),(-1,1),(-2,3),(-2,2)]:
            end[(x+dx,y+dy)]+=1;end[(x+dx+n,y+dy+n)]-=1
    else:raise ValueError('Unknown original band homotopy')
    endpoint={p:c for p,c in end.items() if c}
    return tuple(old),tuple(new),endpoint
