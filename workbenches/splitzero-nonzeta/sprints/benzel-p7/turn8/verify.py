#!/usr/bin/env python3
"""Replay original cells, shared symbolic families, and integer support maps.

Standard library only. Validation remains active under python -O. No solver
is invoked. Symbolic proof and finite computational scopes are recorded
separately; no finite parameter replay is labelled a universal proof.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time
from pathlib import Path
from collections import Counter
import construction as C
import geometry as G
import packing as P
import families as F
import bivariate_certificate as B
import cohomology as H
import transports as TR

ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def independent_region(a,b):
    """Inverse to u=y-x, v=1-x-2y, w=-u-v; original integer congruence."""
    cells=set();L=1-a;U=b-1
    for u in range(L,U+1):
        low=max(L,-U-u);high=min(U,-L-u)
        for v in range(low,high+1):
            n=1-2*u-v
            if n%3==0:
                x=n//3;y=x+u
                G.require(G.differences((x,y))==(u,v,-u-v),'Original difference inverse failed')
                cells.add((x,y))
    return frozenset(cells)

def verify_core(m,k,count):
    A=C.source(m,k);BB=C.new_bones(m,k);R=C.retained_stones(m,k)
    delta=G.triangular(m)-3*k;O=G.omega(delta)
    G.check_partition(A,set(G.incidence(A)))
    G.require(not(set(G.incidence(A))&O),'Source intersects the original residual')
    G.check_partition(BB+R,set(G.incidence(A))|O)
    wanted=3*k*m+6*k*k-3
    G.require(len(A)==len(BB)==wanted and len(R)==delta,'Original tile count mismatch')
    z=H.add(H.unit(O),H.scale(-1,G.chain_boundary(H.unit(R))))
    signed=H.add(H.unit(BB),H.scale(-1,H.unit(A)))
    G.require(z==G.chain_boundary(signed),'Original signed comparison preimage failed')
    p=(m-2,0)
    G.require(z.get(p)==1 and all(p not in t[1]for t in A),'Distinguished class lost its integral left inverse')
    for d in (m,m+1,m+3):
        for p,y,ell,t in C.source_labels(m,k):
            role,j,actual=C.receiving_generator(d,m,k,p,y,ell)
            G.require(actual==t,'Source-to-tail generator map changed cells')
            if role=='tail':G.require(j+y-3*k==y-1-ell,'Tail inverse failed')
            count['original_receiving_generator_checks']+=1
    if k>=2:
        symbolic_A=tuple(G.reflect_tile(G.rotate_tile(t,p))for t in F.expand('source',m,k)for p in range(3))
        G.require(Counter(symbolic_A)==Counter(A),'Shared source families differ from original band labels')
        numeric_long=F.expand('long',m,k)
        direct_long=tuple(G.tile('H',y+m+3*ell,y)for ell in range(k)for y in range(1-m+k-ell,1-2*k))
        G.require(Counter(numeric_long)==Counter(direct_long),'Original long-strip index map failed')
        G.require(Counter(F.expand('deleted',m,k))==Counter(G.tile('R',m-2-i,-i)for i in range(k)),'Corner deletion index map failed')
        count['shared_family_comparisons']+=3
    count['positive_core_partitions']+=1
    count['core_new_bone_placements']+=len(BB)
    count['signed_class_left_inverses']+=1

def verify_kernel(m,k,count):
    A=C.source(m,k);BB=C.new_bones(m,k);K=H.MatchingKernel(A,BB)
    K.check_relations()
    for j in K.basis:
        count['dual_cell_coefficients']+=K.check_dual(j)
        count['exact_kernel_duals']+=1
    coeff=tuple((j%7)-3 for j in range(len(BB)))
    coords=K.coordinates(coeff);restored=K.inverse_coordinates(coords)
    G.require(K.coordinates(restored)==coords,'Kernel coordinate inverse failed')
    diff=H.add({t:a-b for t,a,b in zip(K.B,coeff,restored)})
    old=Counter()
    for ais,bs in K.closed:
        for i in ais:old[K.A[i]]+=coeff[bs[0]]
    G.require(G.chain_boundary(diff)==G.chain_boundary(old),'Coordinate comparison lost the original intersection preimage')
    count['kernel_comparisons']+=1
    return {'m':m,'k':k,'old_bones':len(A),'new_bones':len(BB),'closed_components':len(K.closed),'kernel_rank':len(K.basis)}

def verify_split(m,k,count):
    S=H.Supports(m,k);full=frozenset(range(len(S.old)))
    a=frozenset(range(0,len(S.old),3));b=a|frozenset(range(1,len(S.old),3))
    eta=S.eta(a,b);eta2=S.eta(b,full)
    G.require(H.add(eta,eta2)==S.eta(a,full),'Original release cocycle failed')
    for charge in (-2,0,1,3):
        n={S.old[i]:(i%3)-1 for i in a}
        r,nn=S.augmented_transition(a,b,charge,n)
        G.require(S.augmented_d(b,r,nn)==S.augmented_d(a,charge,n),'Augmented cochain square failed')
        r,nnn=S.augmented_transition(b,full,r,nn)
        G.require((r,nnn)==S.augmented_transition(a,full,charge,n),'Augmented composition failed')
        count['augmented_transition_checks']+=2
    cycle=H.unit(C.patch(m,k));G.require(S.positive_cycle(full,1,cycle),'Original positive charge-one fibre failed')
    X=H.Total(m,k,0,a,{S.old[i]:1 for i in a})
    G.require(X.d().d()==H.Total(m,k,2,a,{}),'Supported differential square failed')
    G.require(X.smul(H.E).label==a and X.smul(H.TAU).label is None,'Support-labelled zero collapsed to absence')
    G.require(X.smul(H.E)!=X.smul(H.TAU),'Distinct support labels erased')
    Y=H.Total(m,k,0,b,{S.old[i]:-1 for i in b})
    for s in (H.TAU,H.E,H.ONE,H.Scalar(True,-2)):
        G.require((X+Y).smul(s)==X.smul(s)+Y.smul(s),'Reconstructed scalar distributivity failed')
        G.require(X.smul(s).d()==X.d().smul(s),'Differential lost scalar/support compatibility')
        count['split_scalar_cochain_checks']+=2
    G.require(S.cells(frozenset())==S.omega and S.cells(None)==frozenset(),'Bottom or empty-release support changed')
    count['positive_augmented_cycles']+=1


def verify_transports(count):
    for kind in ('V_to_H','H_to_D','VV_to_DD'):
        for n in range(31):
            for x,y in ((0,0),(-5,7),(8,-11)):
                old,new,endpoint=TR.band(kind,x,y,n)
                G.require(TR.difference(new,old)==endpoint,'Original band endpoint identity failed')
                G.require(TR.jet(endpoint)==(0,0,0),'Bone homotopy changed global jet')
                G.require(G.incidence(old)==Counter({p:1 for p in G.incidence(old)}) and
                          G.incidence(new)==Counter({p:1 for p in G.incidence(new)}),'Band matching has overlaps')
                count['original_band_homotopies']+=1
    for m,k in ((5,1),(8,2),(14,4)):
        d=m;h=3*k;T=C.complete(d,m,k)
        G.require(set(G.rotate_tile(t)for t in T)==set(T),'Constructed original rotational symmetry failed')
        fixed=[t for t in T if t[0]=='R'and G.rotate_tile(t)==t]
        G.require(all(t==G.tile('R',0,0)for t in fixed),'Unexpected fixed original right stone')
        G.require((G.triangular(m)-3*k-len(fixed))%3==0,'Right-stone orbit count failed')
        count['rotation_fixed_tile_checks']+=1
    # A test of the original chain-map norm without division by three.
    v={(-2,3):2,(1,0):-4,(0,0):1}
    def rot(v):return {G.rho(p):c for p,c in v.items()}
    norm=lambda v:H.add(v,rot(v),rot(rot(v)))
    G.require(norm(norm(v))==H.scale(3,norm(v)),'Integral norm identity failed')
    count['integer_norm_checks']+=1


def rejection_tests():
    tests=[]
    def bad(name,fn):
        try:fn()
        except (ValueError,KeyError):tests.append(name);return
        raise ValueError('Mutation incorrectly accepted: '+name)
    bad('invalid k',lambda:C.complete(5,5,0))
    bad('original parameter too small',lambda:C.complete(10,7,2))
    bad('nonintegral original parameter',lambda:C.complete(10.0,8,2))
    bad('absent scalar with amplitude',lambda:H.Scalar(False,1))
    bad('duplicate matching generator',lambda:H.MatchingKernel([G.tile('H',0,0)]*2,[]))
    bad('missing replacement bone',lambda:G.check_partition(C.patch(8,2)[1:],set(G.incidence(C.source(8,2)))|G.omega(22)))
    bad('nonzero original cell in claimed identity',lambda:(B.identity()+B.point()).verify_zero())
    original=F.specifications
    def changed():
        data=original();data['corner'][7]['y'][-1]+=1;return data
    try:
        F.specifications=changed
        bad('changed parameter-family anchor',lambda:B.identity().verify_zero())
    finally:F.specifications=original
    S=H.Supports(8,2)
    bad('tile outside its support',lambda:S.validate_chain(frozenset(),{G.tile('H',1000,1000):1}))
    bad('charge at absence',lambda:S.augmented_d(None,1,{}))
    return tests


def run(max_k):
    G.require(type(max_k)is int and 1<=max_k<=40,'Use max-k 1..40')
    start=time.monotonic();count=Counter();kernels=[]
    pins=json.loads((ROOT/'SOURCES.json').read_text(encoding='utf-8'))
    for name,digest in pins['parent_code'].items():
        if name.endswith('.py'):G.require(sha(ROOT/name)==digest,'Changed mathematical parent code: '+name)
    pp=pins['parent_proof'];G.require(sha(ROOT/pp['path'])==pp['sha256'],'Changed original parent proof')
    symbolic=B.verify_all()
    # Original core and generator maps: four different m values, not just minimal m.
    for k in range(1,max_k+1):
        for m in sorted({3*k+2,3*k+3,4*k+7,8*k+11}):verify_core(m,k,count)
    # Full original regions; preserve a bounded, explicit cell window.
    regions=[]
    for k in range(1,min(max_k,10)+1):
        for m in (3*k+2,3*k+4):
            for d in (m,m+1,m+2):
                h=G.triangular(d)-G.triangular(m)+3*k;a,b=G.parameters(d,h)
                T=C.complete(d,m,k);cells=G.region_ab(a,b);G.check_partition(T,cells)
                G.require(sum(t[0]=='R'for t in T)==G.triangular(m)-3*k,'Full invariant count changed')
                G.check_partition(tuple(G.reflect_tile(t)for t in T),G.region_ab(b,a))
                if k<=4:
                    G.require(cells==independent_region(a,b),'Independent original region inverse disagrees')
                    count['independent_region_enumerations']+=1
                count['full_tilings_with_reflections']+=2
                count['full_tile_placements_with_reflections']+=2*len(T)
                regions.append({'k':k,'m':m,'d':d,'h':h,'cells':len(cells)})
    for k in range(1,min(max_k,5)+1):
        for m in (3*k+2,3*k+5):
            kernels.append(verify_kernel(m,k,count));verify_split(m,k,count)
    verify_transports(count)
    tests=rejection_tests();count['rejection_tests']=len(tests)
    inputs={p.name:sha(p)for p in ROOT.iterdir()if p.is_file() and p.suffix in ('.py','.json','.md') and p.name not in ('recorded-checks.json','MANIFEST.json')}
    return {'status':'PASS','date':'2026-09-16','turn':8,'python_optimized':not __debug__,
            'symbolic_certificate':symbolic,'finite_core_window':{'k_min':1,'k_max':max_k,'m_values':'distinct values 3k+2,3k+3,4k+7,8k+11'},
            'counts':dict(count),'kernel_comparisons':kernels,'original_regions':regions,
            'rejection_tests':tests,'input_sha256':inputs,'seconds':round(time.monotonic()-start,3),
            'scope':'Exact formal Laurent identity for unbounded integer k>=1,m>=3k+2, together with finite positive, original-region, integer-kernel and Split-Zero replays. Full P7, other two deletion residues, novelty and independent review are not claimed.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--max-k',type=int,default=15);ap.add_argument('--output',type=Path)
    args=ap.parse_args();result=run(args.max_k)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text,encoding='utf-8')
    print(json.dumps({'status':result['status'],'counts':result['counts'],'seconds':result['seconds']},indent=2))
