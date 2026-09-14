"""Replay exact constructions, affine certificates, bijections and finite seeds."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from fractions import Fraction
import argparse, hashlib, json, sys, time
import construction as C
import certify
import polygons as P
ROOT=Path(__file__).resolve().parent

def reflected_region(d,h):
    a,b=2*d+3*h,d+3*h; M=max(a,b)+2
    return {(x,y)for x in range(-M,M+1)for y in range(-M,M+1)
            if all(1-a<=v<=b-1 for v in C.differences(x,y))}

def fail_required(fn):
    try:fn()
    except (ValueError,KeyError,IndexError,TypeError):return
    raise ValueError('A mutation was incorrectly accepted')

def mutation_tests():
    fail_required(lambda:C.tiling(3,5))
    fail_required(lambda:C.tiling(4.0,5))
    fail_required(lambda:C.tiling(4,6))
    rows=[((1,0,0),0),((-1,0,0),-1)]
    certify.verify_weights(rows,{0:Fraction(1),1:Fraction(1)})
    fail_required(lambda:certify.verify_weights(rows,{0:Fraction(-1),1:Fraction(1)}))
    fail_required(lambda:certify.verify_weights(rows,{0:Fraction(1)}))
    fail_required(lambda:C.check_partition((C.tile('H',0,0),),{(0,0)}))
    old=C.TABLES['5']['removed'][0]
    # This base corner was already consumed by the second collar.
    C.TABLES['5']['removed'][0]=['R',[-1,1],[1,0]]
    try:fail_required(lambda:certify.source_membership(5,4))
    finally:C.TABLES['5']['removed'][0]=old
    return 7

def fifth_bijection(d):
    old=C.tiling(d,4); sh=C.TABLES['5']['shift']; moved=C.translate(old,sh)
    A=C.removed(d,5);B=C.replacements(d,5)
    forward=tuple(t for t in moved if t not in A)+B
    if set(forward)!=set(C.tiling(d,5)):raise ValueError('Positive forward map changed')
    backward=C.translate(tuple(t for t in forward if t not in B)+A,(-sh[0],-sh[1]))
    if set(backward)!=set(old):raise ValueError('Positive inverse map failed')

def finite_seeds():
    rows=json.loads((ROOT/'evidence/sixth-witnesses.json').read_text()); count=placements=0
    for a in rows:
        d=a['d'];old=C.translate(C.tiling(d,5),a['shift'])
        removed=C.decode([a['removed_stone']]+a['removed_bones']);new=C.decode(a['new_bones'])
        if any(old.count(t)!=1 for t in removed):raise ValueError('Sixth source tile missing')
        result=tuple(t for t in old if t not in removed)+new
        C.check_partition(result,C.region(d,6))
        residual=C.incidence(new);residual.subtract(C.incidence(removed));residual.update(C.incidence(old))
        if +residual!=Counter({p:1 for p in C.region(d,6)}) or any(n<0 for n in residual.values()):
            raise ValueError('Sixth cochain identity failed')
        count+=1;placements+=len(result)
    # Three exact annuli preserve the integer stone-count difference.
    annuli=json.loads((ROOT/'evidence/constant-charge-annuli.json').read_text())
    for a in annuli:
        d,h=a['d'],a['h'];I=C.region(d,h);O=C.region(d+1,h+d)
        sx,sy=a['shift'];J={(x+sx,y+sy)for x,y in I}
        if not J<=O:raise ValueError('Annulus source inclusion failed')
        ts=C.decode(a['tiles'])
        if any(k=='R'for k,_ in ts):raise ValueError('Annulus is not bone-only')
        C.check_partition(ts,O-J)
        if len(O-J)!=9*(2*d+1)*(d+h):raise ValueError('Annulus size identity failed')
    previous=json.loads((ROOT/'evidence/earlier-fifth-d4.json').read_text())
    old=C.decode(previous['tiling']);new=C.tiling(4,5)
    C.check_partition(old,C.region(4,5))
    delta=C.incidence(new);delta.subtract(C.incidence(old))
    if any(delta.values()):raise ValueError('Earlier/current positive kernel comparison failed')
    return {'sixth_tilings':count,'sixth_tile_placements':placements,'bone_only_annuli':len(annuli),
            'd4_fifth_original_and_new_bijection_kernel':True}

def polygon_checks():
    inverses=memberships=tiles=0
    for d in range(3,9):
        for x in range(-12,13):
            for y in range(-12,13):
                r,s,p=P.from_cell(d,x,y)
                if P.to_cell(d,r,s,p)!=(x,y):raise ValueError('Cell inverse failed')
                inverses+=1
        for h in range(7):
            R=C.region(d,h);counts=Counter()
            for x,y in R:
                r,s,p=P.from_cell(d,x,y)
                if not P.in_polygon(d,h,r,s,p):raise ValueError('Original cell left polygon domain')
                counts[p]+=1
            bound=d+3*h+2;back=set()
            for r in range(-h-1,bound):
                for s in range(-h-1,bound):
                    for p in range(3):
                        if P.in_polygon(d,h,r,s,p):back.add(P.to_cell(d,r,s,p))
                        memberships+=1
            if back!=R or any(counts[p]!=P.count_per_phase(d,h)for p in range(3)):
                raise ValueError('Polygon count or domain inverse failed')
    for k in 'RDHV':
        for p in range(3):
            for r in range(-4,5):
                for s in range(-4,5):
                    x,y=P.to_cell(9,r,s,p)
                    original=C.tile(k,x,y)
                    image={P.to_cell(9,r+a,s+b,q)for q,a,b in P.tile_image(k,p)}
                    if image!=set(original[1]):raise ValueError('Original tile incidence square failed')
                    tiles+=1
    return {'cell_inverse_checks':inverses,'polygon_membership_checks':memberships,
            'tile_incidence_squares':tiles,'complete_small_regions':42}

def run(maximum):
    start=time.monotonic();exact=certify.verify();count=placements=identities=0
    for d in range(4,maximum+1):
        parent=C.tiling(d,4);result=C.tiling(d,5)
        C.check_partition(parent,C.region(d,4));C.check_partition(result,C.region(d,5))
        C.check_partition(C.reflect(result),reflected_region(d,5))
        raw=C.incidence(result);raw.subtract(C.incidence(C.translate(parent,(1,1))))
        delta=C.incidence(C.replacements(d,5));delta.subtract(C.incidence(C.removed(d,5)))
        if dict(+raw)!=dict(+delta) or dict(-raw)!=dict(-delta):raise ValueError('Fifth cochain identity failed')
        if sum(k=='R'for k,_ in result)!=d*(d-1)//2-5 or sum(k!='R'for k,_ in result)!=15*d+75:
            raise ValueError('Original invariant or tile count failed')
        fifth_bijection(d);identities+=1;count+=2;placements+=2*len(result)
    ans={'record_date':'2026-09-15','sprint_turn':3,'status':'PASS','python_optimized':bool(sys.flags.optimize),
         'all_parameter_stages':[{'h':a['stage'],'d_min':a['d_min'],'collision_certificates':a['collision_certificates']}for a in exact],
         'fifth_d_min':4,'fifth_d_max':maximum,'fifth_tilings_with_reflections':count,
         'fifth_tile_placements_with_reflections':placements,'fifth_incidence_and_inverse_identities':identities,
         'bounded_seeds':finite_seeds(),'polygon_checks':polygon_checks(),'mutation_tests':mutation_tests(),
         'full_P7_resolution':False,'independent_specialist_review':False,'lean_build':False,
         'seconds':round(time.monotonic()-start,3)}
    ans['input_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
      for p in sorted(ROOT.rglob('*'))if p.is_file()and (p.suffix=='.py' or p.name in ('tables.json','PROOF.md','sixth-witnesses.json','constant-charge-annuli.json','earlier-fifth-d4.json'))}
    return ans

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--max-d',type=int,default=100)
    parser.add_argument('--output',type=Path,default=ROOT/'evidence/normal.json');args=parser.parse_args()
    if args.max_d<4:raise ValueError('Need max-d>=4')
    receipt=run(args.max_d);args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
