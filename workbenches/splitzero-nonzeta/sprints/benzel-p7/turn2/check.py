#!/usr/bin/env python3
"""Exact replay of the turn-2 construction. Standard library; no tiling solver.
The all-parameter proofs are in PROOF.md. This script records its finite range.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'check.py'
PARENT_BLOB='7a330a951ffcd1ab1dcb1c965142b8ae76041f75'

def require(test: bool, message: str) -> None:
    if not test: raise ValueError(message)

raw=PARENT.read_bytes()
require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==PARENT_BLOB,
        'The original turn-1 constructor has changed; review before replay.')
spec=importlib.util.spec_from_file_location('p7_verified_turn1',PARENT)
t=importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def third_collar(d: int) -> tuple:
    require(d>=3,'Third-collar construction requires integer d>=3')
    out=[t.bone('D',(-d-5+r,d+3-2*r)) for r in range(d+3)]
    out.extend(t.bone('D',p) for p in
               [(-d-4,d+3),(-d-4,d+4),(-d-3,d+4),(-d-2,d+4)])
    out.extend(t.bone('D',(-d+2*r,d+3-r)) for r in range(d))
    out.extend(t.bone('H',(-d-3+2*r,d+5-r)) for r in range(d+2))
    out.append(t.bone('H',(d,3)))
    out.extend(t.bone('V',p) for p in
               [(d+1,0),(d+2,0),(d+3,1),(d+4,-1),(d+5,-3)])
    return tuple(out)


def positive_move(x: int,y: int) -> tuple[tuple,tuple]:
    old=(t.stone((x,y)),t.bone('H',(x+2,y)),t.bone('H',(x+1,y+1)))
    new=(t.bone('H',(x,y)),t.bone('H',(x,y+1)),t.stone((x+3,y)))
    return old,new


def prepare_third(d: int) -> tuple:
    old=t.translate(t.second_tiling(d),(1,-2))
    removed,added=positive_move(d-2,0)
    require(all(old.count(tile)==1 for tile in removed),'Required original source tiles absent')
    return tuple(tile for tile in old if tile not in removed)+added


def third_tiling(d: int) -> tuple:
    prepared=prepare_third(d);S=t.stone((d+1,0))
    require(prepared.count(S)==1,'Moved stone not present exactly once')
    return tuple(tile for tile in prepared if tile!=S)+third_collar(d)


def reflect(tiles: tuple) -> tuple:
    kinds={'R':'R','D':'H','H':'D','V':'V'}
    return tuple((kinds[k],tuple(sorted((i,1-i-j) for i,j in cells))) for k,cells in tiles)


def clean(counter: Counter) -> dict:
    return {p:n for p,n in counter.items() if n}


# E = Z[omega] direct-sum F_3 sigma. The first two entries are integers.
# No mod-3 reduction is applied to the Eisenstein component.
def eadd(a: tuple,b: tuple) -> tuple:
    return a[0]+b[0],a[1]+b[1],(a[2]+b[2])%3


def emul(a: tuple,b: tuple) -> tuple:
    x,y,c=a;u,v,f=b
    return x*u-y*v,x*v+y*u-y*v,((x+y)*f+(u+v)*c)%3


def epow(a: tuple,n: int) -> tuple:
    require(n>=0,'Nonnegative exponent needed; Laurent inverse is supplied separately')
    out=(1,0,0)
    while n:
        if n&1:out=emul(out,a)
        a=emul(a,a);n//=2
    return out


def cell_class(i: int,j: int) -> tuple:
    a,b=((1,0),(0,1),(-1,-1))[(i+2*j)%3]
    return a,b,j%3


def full_class(polynomial: dict) -> tuple:
    out=(0,0,0)
    for (i,j),n in polynomial.items():
        a,b,c=cell_class(i,j)
        out=eadd(out,(n*a,n*b,(n*c)%3))
    return out


def jet_from_full(value: tuple) -> tuple:
    a,b,c=value
    return (a+b)%3,(b+c)%3,c%3


def signed_incidence(chain: list[tuple[int,tuple]]) -> Counter:
    out=Counter()
    for n,(_,cells) in chain:
        for p in cells:out[p]+=n
    return out


def ring_checks() -> dict:
    one=(1,0,0);X=(0,1,0);Y=(-1,-1,1);S=(0,0,1);zero=(0,0,0)
    require(emul(X,(-1,-1,0))==one,'X inverse')
    require(emul(Y,(0,1,2))==one,'Y inverse')
    require(epow(X,3)==one and epow(Y,3)==one,'Laurent unit orders')
    require(S!=zero and eadd(eadd(S,S),S)==zero,'Retained nonzero 3-torsion')
    require(emul(S,S)==zero and emul(X,S)==S,'Square-zero and module relations')
    cell_tests=0;bone_tests=0
    for i in range(-12,13):
        for j in range(-12,13):
            value=emul(epow(X,i%3),epow(Y,j%3))
            require(value==cell_class(i,j),'Original Laurent cell formula')
            require(jet_from_full(value)==(1,i%3,j%3),'Cell/quotient/jet square')
            require(full_class(t.incidence((t.stone((i,j)),)))==S,'Translated stone class')
            for k in t.DIRECTIONS:
                require(full_class(t.incidence((t.bone(k,(i,j)),)))==zero,'Translated bone class')
                bone_tests+=1
            cell_tests+=1
    element_tests=0
    for a in range(-6,7):
        for b in range(-6,7):
            for c in range(3):
                is_zero=jet_from_full((a,b,c))==zero
                require(is_zero==(a%3==0 and b%3==0 and c==0),'Kernel is precisely 3C')
                element_tests+=1
    H=lambda i=0,j=0:t.bone('H',(i,j))
    V=lambda i=0,j=0:t.bone('V',(i,j))
    D=lambda i=0,j=0:t.bone('D',(i,j+2))
    chain=[(1,H()),(1,H(1,0)),(1,H(0,1)),(-1,D(1,0)),(-2,D()),(1,V(1,0)),(2,V())]
    require(clean(signed_incidence(chain))=={p:3 for p in t.stone((0,0))[1]},'Explicit 3s bone identity')
    for m in (12,24):
        for i in range(m):chain.extend(((1,D(i,0)),(-1,V(i,0))))
    source=tuple(t.stone((i,0)) for i in (0,12,24))
    z=t.incidence(source);support=set(z)
    require(clean(signed_incidence(chain))==dict(z),'Global signed preimage of local kernel class')
    local_bones=[]
    for p in support:
        for k,(di,dj) in t.DIRECTIONS.items():
            for u in range(3):
                tile=t.bone(k,(p[0]-u*di,p[1]-u*dj))
                if set(tile[1])<=support:local_bones.append(tile)
    require(not local_bones,'The local kernel example must have no contained bones')
    point_example=Counter({(0,0):1,(3,0):1,(6,0):1})
    require(t.jet(point_example)==zero and full_class(point_example)==(3,0,0),'Nonzero 3C example')
    return {'laurent_cell_square_checks':cell_tests,'translated_bone_classes':bone_tests,
            'integral_quotient_kernel_checks':element_tests,'signed_global_bone_preimage':[
                {'coefficient':n,'kind':tile[0],'cells':tile[1]} for n,tile in chain],
            'local_kernel_example_cells':sorted(support),'local_contained_bones':0}


def verify_third(d: int) -> dict:
    a,b=d+9,2*d+9
    O=t.region_rows(a,b)
    require(O==t.region(a,b),'Independent original outer cell definitions disagree')
    I={t.add(p,(1,-2)) for p in t.region_rows(d+6,2*d+6)}
    require(I<=O,'Translated source not inside original target')
    def in_I(p):
        d0,d1,d2=t.differences(p)
        return -d-8<=d0<=2*d+2 and -d-2<=d1<=2*d+8 and -d-5<=d2<=2*d+5
    require(I=={p for p in O if in_I(p)},'Exact translated source bounds')
    old,new=positive_move(d-2,0)
    require(t.incidence(old)==t.incidence(new),'Nine-cell kernel vector')
    require(all(n==1 for n in t.incidence(old).values()),'Local move overlaps')
    prepared=prepare_third(d);t.verify_tiles(prepared,I)
    S=t.stone((d+1,0));C=third_collar(d)
    require(set(S[1])<=I,'Moved source stone not in source')
    t.verify_tiles(C,(O-I)|set(S[1]))
    residual=Counter({p:1 for p in O});residual.subtract({p:1 for p in I});residual.update(S[1])
    require(dict(t.incidence(C))==clean(residual),'Exact collar cochain identity')
    T=third_tiling(d);t.verify_tiles(T,O)
    reflected=reflect(T);t.verify_tiles(reflected,t.region_rows(b,a))
    require(reflect(reflected)==T,'Reflection inverse fails')
    stones=sum(k=='R' for k,_ in T)
    require(stones==d*(d-1)//2-3,'Stone count')
    require(len(T)-stones==9*d+27,'Bone count')
    require(len(C)==3*d+15 and len(O)==t.area(d,3),'Original cardinalities')
    require(full_class(Counter({p:1 for p in O}))==(0,0,stones%3),'Full original region class')
    raw=Counter({p:1 for p in O});raw.subtract({p:1 for p in I})
    require(full_class(raw)==(0,0,2),'Raw collar class is minus sigma in full quotient')
    require(full_class(residual)==(0,0,0),'Full class cancellation')
    return {'d':d,'h':3,'a':a,'b':b,'cells':len(O),'right_stones':stones,'bones':len(T)-stones,
            'third_collar_bones':len(C),'old_bones_moved':2,
            'tiling_sha256':hashlib.sha256(json.dumps(T,separators=(',',':')).encode()).hexdigest()}


def decode(records: list) -> tuple:
    return tuple(t.bone(k,(i,j)) for k,i,j in records)


def fourth_checks() -> list:
    data=json.loads((ROOT/'fourth-seeds.json').read_text());out=[]
    require([r['d'] for r in data['cases']]==[4,5,6,7,8],'Changed fourth-collar scope')
    for r in data['cases']:
        d=r['d'];shift=tuple(r['source_shift']);old=t.translate(third_tiling(d),shift)
        S=t.stone(tuple(r['source_stone']));removed=(S,)+decode(r['removed_bones']);added=decode(r['added_bones'])
        require(len(removed)==9 and len(set(removed))==9,'Need one source stone and eight original bones')
        require(all(old.count(tile)==1 for tile in removed),'Fourth-collar removed tile absent')
        O=t.region_rows(d+12,2*d+12);I={p for _,cells in old for p in cells}
        require(I<=O,'Fourth-collar source inclusion')
        patch=(O-I)|{p for _,cells in removed for p in cells}
        t.verify_tiles(added,patch)
        new=tuple(tile for tile in old if tile not in removed)+added;t.verify_tiles(new,O)
        require(sum(k=='R' for k,_ in new)==d*(d-1)//2-4,'Fourth-collar invariant')
        out.append({'d':d,'h':4,'cells':len(O),'tiles':len(new),'released_old_bones':8,
                    'added_bones':len(added),'tiling_sha256':hashlib.sha256(json.dumps(new,separators=(',',':')).encode()).hexdigest()})
    return out


def exploration_checks() -> dict:
    data=json.loads((ROOT/'exploration.json').read_text());positive=0;unchecked=0;placements=0
    for r in data['cases']:
        if 'bones' not in r:
            unchecked+=1;continue
        d,h=r['d'],r['h'];D,H=r['outer_d'],r['outer_h']
        I=t.region_rows(d+3*h,2*d+3*h);O=t.region_rows(D+3*H,2*D+3*H)
        require(I<=O,'Exploratory annulus inclusion')
        bones=decode(r['bones']);t.verify_tiles(bones,O-I)
        positive+=1;placements+=len(bones)
    require((positive,unchecked)==(8,12),'Exploratory scope drift')
    return {'positive_annuli_replayed':positive,'tile_placements':placements,
            'uncertified_solver_infeasibility_returns':unchecked,'infeasibility_claimed_proved':False}


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument('--max-d',type=int,default=40)
    parser.add_argument('--output',type=Path,default=ROOT/'evidence'/'checks.json');args=parser.parse_args()
    require(args.max_d>=3,'Need d>=3');start=time.monotonic()
    rows=[verify_third(d) for d in range(3,args.max_d+1)]
    rings=ring_checks();fourth=fourth_checks();exploration=exploration_checks()
    args.output.parent.mkdir(exist_ok=True,parents=True)
    (args.output.parent/'local-kernel-witness.json').write_text(json.dumps(rings,indent=2)+'\n')
    sample={str(d):third_tiling(d) for d in (3,4,7) if d<=args.max_d}
    (args.output.parent/'third-collar-examples.json').write_text(json.dumps(sample,separators=(',',':'))+'\n')
    receipts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
              [PARENT,Path(__file__),ROOT/'PROOF.md',ROOT/'fourth-seeds.json',ROOT/'exploration.json']}
    # Name collision for the two check.py files is avoided by the explicit parent key.
    receipts['parent/check.py']=hashlib.sha256(PARENT.read_bytes()).hexdigest()
    receipt={'status':'PASS','python_optimized':not __debug__,'d_min':3,'d_max':args.max_d,
             'third_collar_parameter_values':len(rows),'third_collar_cochain_identities':len(rows),
             'full_h3_tilings_with_reflections':2*len(rows),
             'h3_tile_placements_with_reflections':2*sum(r['cells']//3 for r in rows),
             'nine_cell_moves':len(rows),'old_bones_moved_each_time':2,
             'full_h4_tilings':len(fourth),'h4_tile_placements':sum(r['tiles'] for r in fourth),
             'ring_checks':{k:v for k,v in rings.items() if k not in ['signed_global_bone_preimage','local_kernel_example_cells']},
             'exploration':exploration,'rows':rows,'fourth_rows':fourth,'input_sha256':receipts,
             'seconds':round(time.monotonic()-start,3),
             'scope':'Exact finite replay accompanying written all-parameter h=3 proof. h=4 only d=4..8. No full P7 resolution or Lean build.'}
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['rows','fourth_rows']},indent=2))

if __name__=='__main__':main()
