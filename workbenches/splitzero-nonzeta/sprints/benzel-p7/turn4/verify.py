"""Exact unbounded-d certificate replay, finite tests, and Split-Zero algebra.

Uses the standard library only. No linear-programming or tiling solver is
called. The finite-breakpoint proof partitions ALL integers d>=4 and retains
an unbounded final interval; it is not extrapolation from a finite sample.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse, hashlib, itertools, json, sys, time
import support as S
C=S.C; ROOT=Path(__file__).resolve().parent

def plus(a,b):return (a[0]+b[0],a[1]+b[1])
def minus(a,b):return (a[0]-b[0],a[1]-b[1])
def mul(k,a):return (k*a[0],k*a[1])
def at(f,d):return f[0]*d+f[1]

def region_forms(point,h,shift=(0,0)):
    x,y=point;x=minus(x,(0,shift[0]));y=minus(y,(0,shift[1]))
    qs=(minus(y,x),minus(minus((0,1),x),mul(2,y)),minus(plus(mul(2,x),y),(0,1)))
    lower=(-1,1-3*h);upper=(2,3*h-1)
    return tuple(f for q in qs for f in (minus(q,lower),minus(upper,q)))

def local_point(u,v):return ((-1,u),(1,v))

def release_points(A):
    selected=[C.TABLES['5']['removed'][0]]+[C.TABLES['5']['removed'][i+1] for i in sorted(A)]
    out=[]
    for k,x,y in selected:
        offsets=((0,0),(1,0),(0,1)) if k=='R' else tuple((q*C.DIR[k][0],q*C.DIR[k][1])for q in range(3))
        out.extend(((x[0],x[1]+u),(y[0],y[1]+v))for u,v in offsets)
    return tuple(out)

def membership_forms(point,A):
    fs=list(region_forms(point,5))+list(region_forms(point,4,(1,1)))
    for q in release_points(A):
        fs.extend((minus(point[0],q[0]),minus(point[1],q[1])))
    return fs

def member(point,A,d):
    outer=all(at(f,d)>=0 for f in region_forms(point,5))
    inner=all(at(f,d)>=0 for f in region_forms(point,4,(1,1)))
    released=any(all(at(minus(x,y),d)==0 for x,y in zip(point,q))for q in release_points(A))
    return (outer and not inner)or released

def intervals(forms):
    """Truth of every affine sign/equality is constant on each returned cell."""
    starts={4}
    for a,b in forms:
        if a:
            f=(-b)//a
            starts.update(n for n in (f,f+1) if n>=4)
    ss=sorted(starts)
    out=[(n,ss[i+1]-1 if i+1<len(ss) else None)for i,n in enumerate(ss)]
    for lo,hi in out:
        for a,b in forms:
            v=a*lo+b
            if hi is not None:
                w=a*hi+b
                if (v>=0)!=(w>=0) or (v==0)!=(w==0):raise ValueError('Missed affine root')
            elif (a>0 and v<=0)or(a<0 and v>=0):
                # A root at lo must have its successor as another interval.
                raise ValueError('Unbounded sign cell is not stable')
    return out

def local_tile(t):return C.tile(*t)

def all_parameter_checks():
    receipts=[]
    for row in S.DUALS:
        i=row['omitted']; A=S.ALL-{i}
        weights={tuple(p):n for p,n in row['weights_at_minus_d_plus_d']}
        if len(weights)!=len(row['weights_at_minus_d_plus_d'])or any(type(n)is not int for n in weights.values()):
            raise ValueError('Repeated site or changed integer coefficient')
        if sum(weights.values())!=row['mass']or row['mass']>=0:raise ValueError('No negative evaluation')
        candidates=set()
        for (u,v),n in weights.items():
            if n<0:
                for k,(dx,dy)in C.DIR.items():
                    for q in range(3):candidates.add((k,u-q*dx,v-q*dy))
        bad=[t for t in sorted(candidates)if sum(weights.get(c,0)for c in local_tile(t)[1])<0]
        points=set(weights)|{c for t in bad for c in local_tile(t)[1]}
        forms=[f for p in points for f in membership_forms(local_point(*p),A)]
        cells=intervals(forms)
        for lo,hi in cells:
            if not all(member(local_point(*p),A,lo)for p in weights):raise ValueError('Dual outside actual support')
            if any(all(member(local_point(*p),A,lo)for p in local_tile(t)[1])for t in bad):
                raise ValueError('Negative evaluation on an admissible bone')
        receipts.append({'omitted_bone':i+1,'dual_nonzero_sites':len(weights),'region_evaluation':row['mass'],
                         'candidate_bones_through_negative_sites':len(candidates),'negative_bones_excluded':len(bad),
                         'parameter_intervals':cells})
    if sorted(x['omitted']for x in S.DUALS)!=list(range(16)):raise ValueError('Incomplete maximal-omission cover')
    patch=S.PATCH
    if patch['denominator']!=1:raise ValueError('Signed lift is not integral')
    rho=Counter({local_tile(t):1 for t in patch['removed_new_bones']})
    mu=Counter({local_tile(t):n for t,n in patch['signed_new_bones']})
    old16=C.tile('V',1,-3)
    if S.boundary(mu)!=S.add_vectors(S.boundary(rho),S.scale(S.unit(old16[1]),-1)):
        raise ValueError('Original signed incidence identity failed')
    if not set(old16[1])<=set(S.boundary(rho)):raise ValueError('Missing omitted source cells')
    # All nine removed new bones are literal fixed rows of the proved fifth table.
    families=C.TABLES['5']['families'];matches=[]
    for k,u,v in patch['removed_new_bones']:
        ids=[name for name,kind,x,y,bound in families
             if (kind,x,y,bound)==(k,[-1,0,u],[1,0,v],[0,0])]
        if len(ids)!=1:raise ValueError('Unproved source-family substitution')
        matches.append(ids[0])
    if C.TABLES['5']['removed'][-1]!=['V',[-1,1],[1,-3]]:raise ValueError('Original last release changed')
    A=frozenset(range(15));pnts={p for t in mu for p in t[1]}
    cells=intervals([f for p in pnts for f in membership_forms(local_point(*p),A)])
    for lo,hi in cells:
        if not all(member(local_point(*p),A,lo)for p in pnts):raise ValueError('Signed lift left its support')
    # B15 is absent at every prefix through level 14. Its dual is evaluation at one cell.
    row=S.DUALS[14]
    if row['weights_at_minus_d_plus_d']!=[[[4,-1],-1]]:raise ValueError('Evaluation retraction changed')
    return {'domain':'every integer d>=4','maximal_omissions':receipts,
            'proper_release_subsets_excluded':2**16-1,
            'signed_patch_cells':24,'signed_patch_source_rows':matches,
            'signed_patch_parameter_intervals':cells,
            'integral_class_first_zero_level':15,'first_positive_level':16}

def reject(fn):
    try:fn()
    except (ValueError,TypeError,KeyError):return
    raise ValueError('Mutation unexpectedly accepted')

def split_checks():
    scalars=[S.TAU]+[S.Scalar(True,n)for n in range(-2,3)]
    checks=0
    for a,b,c in itertools.product(scalars,repeat=3):
        if (a+b)+c!=a+(b+c)or(a*b)*c!=a*(b*c)or a*(b+c)!=a*b+a*c:
            raise ValueError('Split scalar identity failed')
        checks+=3
    xs=[S.CyclicClass(None)]+[S.CyclicClass(j,n)for j in (0,1,14)for n in (-1,0,1)]+[S.CyclicClass(j)for j in (15,16)]
    for x,y,z in itertools.product(xs,repeat=3):
        if (x+y)+z!=x+(y+z):raise ValueError('Reconstructed addition failed')
        checks+=1
    for x,y,a,b in itertools.product(xs,xs,scalars,scalars):
        if (x+y).smul(a)!=x.smul(a)+y.smul(a)or x.smul(a+b)!=x.smul(a)+x.smul(b)or x.smul(a*b)!=x.smul(b).smul(a):
            raise ValueError('Actual split-module law failed')
        checks+=3
    source=S.Total(4,0,frozenset(range(15)),S.fixed_vector_preimage(4))
    image=source.differential()
    if image.amplitude!=S.unit(S.support_cells(4,frozenset())):raise ValueError('Wrong fixed source class')
    if image.differential()!=S.Total(4,2,source.label,{}):raise ValueError('Typed supported differential square failed')
    if image.differential()==S.Total(4,2,None,{}):raise ValueError('Lost support at d squared')
    if source.smul(S.E).label!=source.label or source.smul(S.TAU).label is not None:
        raise ValueError('Supported zero collapsed into absence')
    if S.CyclicClass(14,1).transport(15)!=S.CyclicClass(15):raise ValueError('Original killed class not retained')
    if S.CyclicClass(15)==S.CyclicClass(None):raise ValueError('Internal homology zero became absent')
    reject(lambda:S.Scalar(False,1));reject(lambda:S.Total(4,1,None,{(0,0):1}))
    reject(lambda:S.CyclicClass(15,1));reject(lambda:S.CyclicClass(14,1).transport(13))
    return {'exact_algebra_identities':checks,'rejection_tests':4,
            'differential_square':'same-label zero at degree 2','global_zero_kernel_of_constant_charge_line_to_homology':'bottom only',
            'supported_zero_preimage_of_constant_charge_line':'zero for prefix 0..14; entire Z source fibre for prefix 15,16'}

def finite_checks(max_d):
    total=0;positive=0;dual_checks=0;homotopies=0
    for d in range(4,max_d+1):
        A15=frozenset(range(15));pts=S.support_cells(d,A15);gamma=S.signed_at_15(d)
        if any(not set(t[1])<=pts for t in gamma):raise ValueError('Signed chain outside support')
        if S.boundary(gamma)!=S.unit(pts):raise ValueError('Signed cover failed')
        if sum(n<0 for n in gamma.values())!=1:raise ValueError('Changed signed coefficient structure')
        fixed=S.fixed_vector_preimage(d)
        if S.boundary(fixed)!=S.unit(S.support_cells(d,frozenset())):raise ValueError('Fixed-vector preimage failed')
        full=S.support_cells(d,S.ALL);beta=C.replacements(d,5)
        C.check_partition(beta,full);positive+=1
        total+=len(gamma)
        for row in S.DUALS:
            A=S.ALL-{row['omitted']};P=S.support_cells(d,A)
            w={(u-d,v+d):n for (u,v),n in row['weights_at_minus_d_plus_d']}
            if not set(w)<=P or sum(w.values())>=0:raise ValueError('Dual support/evaluation failed')
            for tile in S.all_bones(P):
                if sum(w.get(c,0)for c in tile[1])<0:raise ValueError('Dual failed on actual contained bone')
                dual_checks+=1
        # Coherent original source corrections along all prefixes.
        _,bs=S.released(d)
        for j in range(17):
            A=frozenset(range(j));rhs=S.add_vectors(S.unit(S.support_cells(d,frozenset())),S.boundary({b:1 for b in bs[:j]}))
            if rhs!=S.unit(S.support_cells(d,A)):raise ValueError('Source correction identity failed')
            homotopies+=1
    return {'d_min':4,'d_max':max_d,'positive_full_patches':positive,
            'signed_chain_terms_replayed':total,'dual_bone_evaluations':dual_checks,'prefix_source_homotopies':homotopies}

def rees_checks():
    # Actual delay is established by the preceding evaluation and integral lift.
    q=15;gram=[[int(i+j==q-1)for j in range(q)]for i in range(q)]
    square=[[sum(gram[i][k]*gram[k][j]for k in range(q))for j in range(q)]for i in range(q)]
    if square!=[[int(i==j)for j in range(q)]for i in range(q)]:raise ValueError('Residue pairing inverse failed')
    theta={i:1 for i in range(q)};product=Counter(theta)
    for i,c in theta.items():product[i+1]-=c
    if {i:c for i,c in product.items()if c}!={0:1,15:-1}:raise ValueError('Boundary character failed')
    if -sum(i*c for i,c in product.items())!=15:raise ValueError('Defect trace failed')
    return {'base_field':'Q','source_image_lattice':'T^15 Q[T] w0','target_lattice':'Q[T] w0',
            'defect_length':15,'residue_pairing_rank':15,'tensor_and_symmetric_rank_one_lengths':[15*m for m in range(1,9)]}

def augmented_checks():
    _,bs=S.released(4)
    labels=[frozenset(),frozenset({0}),frozenset({1}),frozenset({0,1})]
    xs=[S.Augmented(4,None,0,{})]+[S.Augmented(4,A,r,{bs[i]:1 for i in A}) for A in labels for r in (-1,0,1)]
    count=0
    # The original cochain arrows, rather than a formal label-only sum, are used.
    for a,b in itertools.product(xs,repeat=2):
        if (a+b).differential()!=a.differential()+b.differential():raise ValueError('Augmented incidence square failed')
        count+=1
    for a in xs:
        for b,c in [(xs[1],xs[-1]),(xs[4],xs[7])]:
            if (a+b)+c!=a+(b+c):raise ValueError('Augmented reconstruction associativity failed')
            count+=1
        for scalar in (S.TAU,S.E,S.ONE,S.Scalar(True,-2)):
            if a.smul(scalar).differential()!=a.differential().smul(scalar):raise ValueError('Augmented split scalar square failed')
            count+=1
    n=S.Augmented(4,frozenset(range(15)),1,S.signed_at_15(4))
    p=S.Augmented(4,S.ALL,1,{t:1 for t in C.replacements(4,5)})
    if n.differential().amplitude or p.differential().amplitude:raise ValueError('Charge-one cycle failed')
    if not any(v<0 for v in n.chain.values()) or any(v<0 for v in p.chain.values()):raise ValueError('Original positive fibre classification changed')
    advanced=n.transport(S.ALL)
    difference=S.add_vectors(p.chain,S.scale(advanced.chain,-1))
    if S.boundary(difference):raise ValueError('Repair cycle difference failed')
    return {'coherent_linear_augmented_checks':count,'charge_one_signed_cycle_level':15,
            'charge_one_positive_cycle_level':16,'cycle_difference_original_tiles':len(difference)}

def run(max_d):
    start=time.monotonic();unbounded=all_parameter_checks();algebra=split_checks()
    finite=finite_checks(max_d);rees=rees_checks();augmented=augmented_checks()
    # Mutate original exact certificates; rejection must survive python -O.
    old=S.DUALS[0]['mass'];S.DUALS[0]['mass']=0
    try:reject(all_parameter_checks)
    finally:S.DUALS[0]['mass']=old
    old=S.PATCH['signed_new_bones'][2][1];S.PATCH['signed_new_bones'][2][1]=1
    try:reject(all_parameter_checks)
    finally:S.PATCH['signed_new_bones'][2][1]=old
    result={'record_date':'2026-09-15','sprint_turn':4,'status':'PASS','python_optimized':bool(sys.flags.optimize),
            'unbounded_parameter_proof':unbounded,'splitzero':algebra,'augmented_complex':augmented,'finite_replay':finite,'rees':rees,
            'additional_mutation_tests':2,'full_problem_7_resolved':False,'lean_rebuilt':False,
            'seconds':round(time.monotonic()-start,3)}
    result['input_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(ROOT.iterdir())if p.is_file()and p.suffix in ('.py','.json','.md')}
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--max-d',type=int,default=20);parser.add_argument('--output',type=Path,default=ROOT/'evidence/normal.json');args=parser.parse_args()
    if args.max_d<4:raise ValueError('At least the original d=4 is required')
    r=run(args.max_d);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
