"""Verify all-parameter literal collar tables with exact rational arithmetic."""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
import affine
from construction import TABLES, DIR

ROOT = Path(__file__).resolve().parent

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(n,a): return tuple(n*x for x in a)

def cells(f,u):
    _,k,x,y,_ = f; dx,dy = DIR[k]
    return add(x,(0,0,u*dx)),add(y,(0,0,u*dy))

def coordinates(f,u):
    x,y = cells(f,u)
    return sub(y,x),add(sub(mul(-1,x),mul(2,y)),(0,0,1)),add(add(mul(2,x),y),(0,0,-1))

def nonnegative(expr, upper, minimum):
    a,b,c = expr
    if b < 0: a,c = a+b*upper[0], c+b*upper[1]
    return a >= 0 and a*minimum+c >= 0

def collision(f,g,u,v,minimum):
    A,B = f[4],g[4]
    rows = [((-1,0,0),-minimum),((0,-1,0),0),((-A[0],1,0),A[1]),
            ((0,0,-1),0),((-B[0],0,1),B[1])]
    for x,y in zip(cells(f,u),cells(g,v)):
        a = (x[0]-y[0],x[1],-y[1]); b = y[2]-x[2]
        rows += [(a,b),(mul(-1,a),-b)]
    return rows

def verify_weights(rows, weights):
    if not weights or any(i not in range(len(rows)) or w<0 for i,w in weights.items()):
        raise ValueError('Invalid nonnegative certificate')
    for j in range(len(rows[0][0])):
        if sum(weights.get(i,0)*a[j] for i,(a,b) in enumerate(rows)) != 0:
            raise ValueError('Certificate left side does not cancel')
    if sum(weights.get(i,0)*b for i,(a,b) in enumerate(rows)) >= 0:
        raise ValueError('Certificate is not a strict contradiction')

def simultaneous_zero(x,y,minimum):
    roots = []
    for a,b in (x,y):
        if a: roots.append(-F(b,a))
        elif b: return False
    if not roots: return True
    return len(set(roots)) == 1 and roots[0].denominator == 1 and roots[0] >= minimum

def affine_bound(x,minimum): return x[0]>=0 and x[0]*minimum+x[1]>=0

def source_membership(stage,minimum):
    """Find exact original generator preimages; exclude all earlier releases."""
    data = TABLES[str(stage)]
    def shifts(first,last):
        return tuple(sum(TABLES[str(j)]['shift'][c] for j in range(first,last+1)) for c in (0,1))
    out = []
    for index,(kind,X,Y) in enumerate(data['removed']):
        found = None
        if kind == 'R':
            sx,sy = shifts(1,stage)
            # Original base anchor (d-2-2r-s, r-s)+(sx,sy).
            x = sub(X,(1,-2+sx)); y = sub(Y,(0,sy))
            r = tuple(-F(a-b,3) for a,b in zip(x,y)); s = sub(r,y)
            if (all(a.denominator == 1 for a in (*r,*s)) and affine_bound(r,minimum)
                    and affine_bound(s,minimum) and affine_bound(sub((1,-2),add(r,s)),minimum)):
                found = {'birth':0,'family':'q','r':list(map(int,r)),'s':list(map(int,s))}
        else:
            for birth in range(1,stage):
                sx,sy = shifts(birth+1,stage)
                for name,k,x,y,U in TABLES[str(birth)]['families']:
                    if k != kind: continue
                    dx = sub(X,(x[0],x[2]+sx)); dy = sub(Y,(y[0],y[2]+sy))
                    if x[1]: r = tuple(F(a,x[1]) for a in dx)
                    elif y[1]: r = tuple(F(a,y[1]) for a in dy)
                    else: r = (F(0),F(0))
                    if (mul(x[1],r) == dx and mul(y[1],r) == dy and
                        all(a.denominator == 1 for a in r) and affine_bound(r,minimum)
                        and affine_bound(sub(U,r),minimum)):
                        found = {'birth':birth,'family':name,'r':list(map(int,r))}; break
                if found: break
        if found is None: raise ValueError(('No original preimage',stage,index))
        # The source family is disjoint at birth. Earlier removals can hit it
        # exactly when both affine anchor coordinates agree at an integer d.
        for earlier in range(max(1,found['birth']+1),stage):
            sx,sy = shifts(earlier+1,stage)
            for k,x,y in TABLES[str(earlier)]['removed']:
                if k == kind and simultaneous_zero(sub(X,add(x,(0,sx))),sub(Y,add(y,(0,sy))),minimum):
                    raise ValueError(('Original tile already consumed',stage,index,earlier))
        out.append({'removed_index':index,**found})
    for (k,x,y),(l,z,w) in combinations(data['removed'],2):
        if k==l and simultaneous_zero(sub(x,z),sub(y,w),minimum):
            raise ValueError('Repeated source tile')
    return out

def verify(record=True):
    results=[];certificates={}
    if set(TABLES) != {'1','2','3','4','5'}: raise ValueError('Unexpected stage scope')
    for stage in range(1,6):
        data=TABLES[str(stage)];minimum=data['d_min'];families=data['families']
        if minimum != (3 if stage<4 else 4): raise ValueError('Parameter domain changed')
        names=[f[0] for f in families]
        if len(names)!=len(set(names)):raise ValueError('Duplicate family label')
        source=source_membership(stage,minimum)
        sx,sy=data['shift'];inc=(sy-sx,-sx-2*sy,2*sx+sy)
        low=(-1,0,1-3*stage);high=(2,0,3*stage-1)
        il=[(-1,0,4-3*stage+x) for x in inc]
        ih=[(2,0,3*stage-4+x) for x in inc]
        if any(x < -3 or x>3 for x in inc):raise ValueError('Inner embedding not certified')
        inside=Counter();inside_labels={};checks=0
        for f in families:
            name,k,x,y,U=f
            if not nonnegative((U[0],0,U[1]),(0,0),minimum):raise ValueError('Empty range')
            if U != [0,0] and x[1]*DIR[k][1]-y[1]*DIR[k][0]==0:
                raise ValueError('Within-family cell injectivity unavailable')
            for u in range(3):
                coords=coordinates(f,u)
                if not all(nonnegative(sub(c,low),U,minimum) and nonnegative(sub(high,c),U,minimum) for c in coords):
                    raise ValueError(('Outer containment',stage,name,u))
                checks+=6
                is_in=all(nonnegative(sub(c,l),U,minimum) and nonnegative(sub(h,c),U,minimum) for c,l,h in zip(coords,il,ih))
                if is_in:
                    if U != [0,0]:raise ValueError('Indexed inside family requires partition')
                    X,Y=cells(f,u);inside[((X[0],X[2]),(Y[0],Y[2]))]+=1
                    inside_labels.setdefault(name,[]).append(u)
                elif not any(nonnegative(w,U,minimum) for c,l,h in zip(coords,il,ih)
                             for w in (sub(sub(l,c),(0,0,1)),sub(sub(c,h),(0,0,1)))):
                    raise ValueError(('Unresolved inner cutoff',stage,name,u))
        released=Counter()
        for k,X,Y in data['removed']:
            offsets=((0,0),(1,0),(0,1)) if k=='R' else tuple((u*DIR[k][0],u*DIR[k][1]) for u in range(3))
            for x,y in offsets:released[((X[0],X[1]+x),(Y[0],Y[1]+y))]+=1
        if inside!=released:raise ValueError('Source intersection not equal as affine multisets')
        slope=sum(f[4][0] for f in families);constant=sum(f[4][1]+1 for f in families)
        if (3*slope,3*constant)!=(9,18*stage-12+sum(released.values())):
            raise ValueError('Area polynomial does not close')
        proofs=[]
        for f,g in combinations(families,2):
            for u in range(3):
                for v in range(3):
                    rows=collision(f,g,u,v,minimum);weights=affine.contradiction(rows)
                    if weights is None:raise ValueError(('No all-parameter certificate',stage,f[0],g[0],u,v))
                    # Acceptance does not trust the eliminator's internal checks.
                    verify_weights(collision(f,g,u,v,minimum),weights)
                    proofs.append({'pair':[f[0],g[0]],'offsets':[u,v],'weights':[[i,str(w)]for i,w in sorted(weights.items())]})
        certificates[str(stage)]=proofs
        results.append({'stage':stage,'d_min':minimum,'source_preimages':source,'inside_offsets':inside_labels,
                        'outer_inequalities':checks,'matched_source_cells':sum(inside.values()),
                        'new_bones':[slope,constant],'collision_certificates':len(proofs),
                        'status':'ALL_PARAMETER_EXACT_PASS'})
    if record:
        dest=ROOT/'evidence';dest.mkdir(exist_ok=True)
        (dest/'all-parameter-certificates.json').write_text(json.dumps(certificates,separators=(',',':'))+'\n')
        (dest/'all-parameter-summary.json').write_text(json.dumps(results,indent=2)+'\n')
    return results

if __name__=='__main__':
    ans=verify();print(json.dumps([{k:v for k,v in a.items()if k not in ('source_preimages','inside_offsets')}for a in ans],indent=2))
