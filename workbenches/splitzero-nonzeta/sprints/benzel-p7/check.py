#!/usr/bin/env python3
"""Replay explicit P7 collars and full tilings using only integer arithmetic.
No search is used by the constructors. Check scopes are explicit in the receipt.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import time

Cell = tuple[int, int]
Tile = tuple[str, tuple[Cell, ...]]
DIRECTIONS = {'D': (1, -1), 'H': (1, 0), 'V': (0, 1)}


def add(p: Cell, q: Cell) -> Cell:
    return (p[0]+q[0], p[1]+q[1])


def stone(base: Cell) -> Tile:
    i,j=base
    return ('R',tuple(sorted(((i,j),(i+1,j),(i,j+1)))))


def bone(kind: str, base: Cell) -> Tile:
    di,dj=DIRECTIONS[kind];i,j=base
    return (kind,tuple(sorted((i+t*di,j+t*dj) for t in range(3))))


def translate(tiles: tuple[Tile,...], shift: Cell) -> tuple[Tile,...]:
    return tuple((k,tuple(sorted(add(p,shift) for p in t))) for k,t in tiles)


def differences(p: Cell) -> tuple[int,int,int]:
    i,j=p
    return j-i,1-i-2*j,2*i+j-1


def in_region(a: int,b: int,p: Cell) -> bool:
    return all(1-a<=q<=b-1 for q in differences(p))


def region(a: int,b: int) -> set[Cell]:
    if min(a,b)<2 or a>2*b or b>2*a:
        raise ValueError('Outside original parameter domain')
    # From the three bounded differences and i+j+k=1, every coordinate
    # lies in [-M,M], M=max(a,b)+2. Thus this finite scan is exhaustive.
    M=max(a,b)+2
    return {(i,j) for i in range(-M,M+1) for j in range(-M,M+1)
            if in_region(a,b,(i,j))}


def region_rows(a: int,b: int) -> set[Cell]:
    """Independent row-interval implementation of the same original inequalities."""
    M=max(a,b)+2
    out=set()
    for i in range(-M,M+1):
        lower=max(i+1-a,-((b+i-2)//2),2-a-2*i)
        upper=min(i+b-1,(a-i)//2,b-2*i)
        out.update((i,j) for j in range(lower,upper+1))
    return out


def area(d: int,h: int) -> int:
    return 3*d*(d-1)//2+(9*d-3)*h+9*h*h


def base_tiling(d: int) -> tuple[Tile,...]:
    if d<3: raise ValueError('This construction uses d>=3')
    return tuple(stone((d-2-2*r-s,r-s))
                 for r in range(d-1) for s in range(d-1-r))


def first_bones(d: int) -> tuple[Tile,...]:
    out=[bone('D',(-2,3-d)),bone('D',(-2,4-d)),bone('D',(-1,1-d))]
    out.extend(bone('H',(-d-1+2*r,d+1-r)) for r in range(d))
    out.extend(bone('H',(r,3-d+r)) for r in range(d-1))
    out.append(bone('V',(1,-d)))
    out.extend(bone('V',(r+2,r-d)) for r in range(d))
    return tuple(out)


def second_bones(d: int) -> tuple[Tile,...]:
    out=[bone('D',(-d-2,d)),bone('D',(-d-2,d+1))]
    out.extend(bone('D',(-d-1+r,d-2-2*r)) for r in range(d))
    out.extend(bone('H',p) for p in ((-d-3,d+2),(-d-2,d+3),(-d-1,d+1),(-d,d)))
    out.extend(bone('V',(1-d+r,d-3-2*r)) for r in range(d))
    out.extend((bone('V',(1,-d-2)),bone('V',(2,-d-3))))
    out.extend(bone('V',(3+r,-d-2+r)) for r in range(d+1))
    return tuple(out)


def replace(tiling: tuple[Tile,...],shift: Cell,reserved: Tile,
            replacement: tuple[Tile,...]) -> tuple[Tile,...]:
    moved=translate(tiling,shift)
    if moved.count(reserved)!=1: raise ValueError('Reserved source tile missing or duplicated')
    return tuple(t for t in moved if t!=reserved)+replacement


def first_tiling(d: int) -> tuple[Tile,...]:
    return replace(base_tiling(d),(-2,1),stone((-2,3-d)),first_bones(d))


def second_tiling(d: int) -> tuple[Tile,...]:
    return replace(first_tiling(d),(1,1),stone((1-d,d)),second_bones(d))


def incidence(tiles: tuple[Tile,...]) -> Counter:
    return Counter(p for _,tile in tiles for p in tile)


def verify_tiles(tiles: tuple[Tile,...],V: set[Cell]) -> None:
    # A second tile-classifier uses pairwise differences / extreme coordinates,
    # rather than invoking the construction functions.
    for k,t in tiles:
        if len(t)!=3 or len(set(t))!=3: raise ValueError('Degenerate tile')
        pts=set(t)
        if k=='R':
            i=min(p[0] for p in t);j=min(p[1] for p in t)
            good=pts=={(i,j),(i+1,j),(i,j+1)}
        else:
            di,dj=DIRECTIONS[k]
            good=any({(p[0]+s*di,p[1]+s*dj) for s in (-1,0,1)}==pts for p in t)
        if not good: raise ValueError('Forbidden shape')
    if incidence(tiles)!=Counter({p:1 for p in V}):
        raise ValueError('Containment, overlap or coverage failure')


def verify_collar(d: int,stage: int,I: set[Cell],O: set[Cell]) -> None:
    shift,S,C=((-2,1),stone((-2,3-d)),first_bones(d)) if stage==1 else ((1,1),stone((1-d,d)),second_bones(d))
    J={add(p,shift) for p in I}
    if not J<=O or not set(S[1])<=J: raise ValueError('Source inclusion or reserved tile failure')
    target=(O-J)|set(S[1])
    verify_tiles(C,target)
    if len(C)!=(3*d+3 if stage==1 else 3*d+9): raise ValueError('Collar count mismatch')
    # Exact cochain equation: partial beta = 1_O - J 1_I + partial S.
    residual=Counter({p:1 for p in O})
    residual.subtract({p:1 for p in J})
    residual.update(S[1])
    residual=Counter({p:n for p,n in residual.items() if n})
    if incidence(C)!=residual: raise ValueError('Cochain residual identity failed')


def jet(cells_with_coefficients: Counter) -> tuple[int,int,int]:
    return tuple(sum(n*(1 if k==0 else p[k-1]) for p,n in cells_with_coefficients.items())%3
                 for k in range(3))


def fixed_source_obstruction() -> list[dict]:
    I=region(9,12);O=region(12,15);T=second_tiling(3)
    rows=[]
    # All inner extrema are attained. The outer bound permits only
    # difference increments in [-3,3]; the inverse gives |shift_i|<=3.
    for coord in range(3):
        if (min(differences(p)[coord] for p in I),max(differences(p)[coord] for p in I))!=(-8,11):
            raise ValueError('Required attained coordinate extrema absent')
    for si in range(-3,4):
        for sj in range(-3,4):
            shift=(si,sj);J={add(p,shift) for p in I}
            if not J<=O: continue
            S=next(t for k,t in translate(T,shift) if k=='R')
            patch=(O-J)|set(S)
            isolated=[]
            for p in sorted(patch):
                exists=False
                for di,dj in DIRECTIONS.values():
                    for u in range(3):
                        tile={(p[0]+(v-u)*di,p[1]+(v-u)*dj) for v in range(3)}
                        if tile<=patch: exists=True
                if not exists: isolated.append(p)
            if not isolated: raise ValueError('Fixed-source obstruction was not reproduced')
            rows.append({'shift':shift,'patch_cells':len(patch),'uncoverable_cells':isolated,
                         'reason':'No permitted bone through these cells lies entirely in the exact patch.'})
    if len(rows)!=13: raise ValueError('Containing-translation count changed')
    return rows


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument('--max-d',type=int,default=60)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'evidence'/'checks.json')
    args=parser.parse_args()
    if args.max_d<3: raise ValueError('Need at least d=3')
    started=time.monotonic();rows=[];examples=[]
    for d in range(3,args.max_d+1):
        Vs=[region(d+3*h,2*d+3*h) for h in range(3)]
        for h,V in enumerate(Vs):
            if V!=region_rows(d+3*h,2*d+3*h): raise ValueError('Independent carrier implementations disagree')
            if len(V)!=area(d,h): raise ValueError('Source area polynomial mismatch')
        Ts=[base_tiling(d),first_tiling(d),second_tiling(d)]
        for h,(V,T) in enumerate(zip(Vs,Ts)):
            verify_tiles(T,V)
            R=sum(k=='R' for k,_ in T)
            if R!=d*(d-1)//2-h: raise ValueError('Original invariant count mismatch')
            if jet(Counter({p:1 for p in V}))!=(0,R%3,R%3):
                raise ValueError('Original region jet observation failed')
            for kind,tile in T:
                expected=(0,1,1) if kind=='R' else (0,0,0)
                if jet(Counter(tile))!=expected: raise ValueError('Tile jet observation failed')
            if h: verify_collar(d,h,Vs[h-1],V)
            rows.append({'d':d,'h':h,'a':d+3*h,'b':2*d+3*h,'cells':len(V),'right_stones':R,
                         'bones':len(T)-R,'tiling_sha256':hashlib.sha256(json.dumps(T,separators=(',',':')).encode()).hexdigest()})
        if d in (3,4,5,10): examples.append({'d':d,'h':2,'tiles':Ts[2]})
    obstruction=fixed_source_obstruction()
    receipt={'status':'PASS','python_optimized':not __debug__,'d_min':3,'d_max':args.max_d,
             'parameter_values':args.max_d-2,'full_tilings_checked':len(rows),
             'collar_cochain_identities_checked':2*(args.max_d-2),
             'fixed_source_translations_with_uncoverable_cells':len(obstruction),
             'total_tile_placements_checked':sum((r['cells']//3) for r in rows),
             'rows':rows,'seconds':round(time.monotonic()-started,3),
             'scope':'Finite replay of explicit constructors; the all-parameter written proof is in PROOF.md.',
             'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    (args.output.parent/'fixed-source-obstruction.json').write_text(json.dumps(obstruction,indent=2)+'\n')
    (args.output.parent/'examples.json').write_text(json.dumps(examples,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2))

if __name__=='__main__': main()
