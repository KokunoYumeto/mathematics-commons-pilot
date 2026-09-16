#!/usr/bin/env python3
"""Deterministic exact finite checks. No network, theorem prover or agent launch.
Run: python tools/check_progress.py. Writes bounded certificates and a receipt.
Every check uses explicit exceptions, so python -O does not disable validation.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from fractions import Fraction as Q
from itertools import combinations,product
from math import comb,factorial
from pathlib import Path
import hashlib,json,sys,time
from benzel import (cells,placements,count_polynomial,covers,move_graph,forest,
                    delta,right_partition,find_cover)
ROOT=Path(__file__).resolve().parents[1]

def require(ok,message):
    if not ok: raise AssertionError(message)

def dump(name,obj):
    p=ROOT/'evidence'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return {'path':'evidence/'+name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def independent_tiles(V):
    """Second geometry implementation: classify each 3-subset by axial offsets."""
    offsets={'L':{(0,0),(1,0),(1,-1)},'R':{(0,0),(1,0),(0,1)},
             'B0':{(0,0),(1,-1),(2,-2)},'B1':{(0,0),(1,0),(2,0)},
             'B2':{(0,0),(0,1),(0,2)}}
    result={}
    for ids in combinations(range(len(V)),3):
        pair={(V[i][0],V[i][1]) for i in ids}
        for k,shape in offsets.items():
            # Check every possible placement of the distinguished offset (0,0).
            if any({(x-a,y-b) for x,y in pair}==shape for a,b in pair):
                result[sum(1<<i for i in ids)]=k
    return result

def verify_cover(V,T,kind):
    full=(1<<len(V))-1; union=0
    for t in T:
        require(t in kind and not union&t,'invalid or overlapping tile')
        union|=t
    require(union==full,'uncovered cell')

def benzel_checks():
    geometries=0;rows=[];certs=[];jets=0
    for a in range(2,8):
        for b in range(a,min(7,2*a)+1):
            V=cells(a,b);_,K=placements(V)
            require(K==independent_tiles(V),'triple versus axial tile generators disagree')
            geometries+=1
            poly,states=count_polynomial(V);T,K=covers(V)
            require(len(T)==len(set(T))==sum(poly),'independent cover count disagrees')
            histogram=Counter()
            for t in T:
                verify_cover(V,t,K)
                r=sum(K[x]=='R' for x in t);l=sum(K[x]=='L' for x in t)
                require(r-l==delta(a,b),'original invariant differs from literal cover')
                histogram[r+l]+=1
            require(all(histogram[i]==c for i,c in enumerate(poly)),'stone histogram differs')
            c=abs(delta(a,b));P=Counter()
            for s,v in enumerate(poly):
                if v:
                    require(s>=c and (s-c)%2==0,'wrong parity support')
                    P[(s-c)//2]+=v
            F3=sum(v*3**s for s,v in enumerate(poly));moments=[]
            for m in range(max(P,default=0)+1):
                moments.append(sum(v*comb(j,m) for j,v in P.items() if j>=m))
            require(F3==3**c*sum(8**m*x for m,x in enumerate(moments)),'exact jet identity')
            for r in range(1,25):
                M=(r+2)//3
                require(F3%2**r==(3**c*sum(8**m*x for m,x in enumerate(moments[:M])))%2**r,'truncated jet identity')
                jets+=1
            edges=move_graph(T,K);roots,parent,components=forest(len(T),edges)
            require(len(components)==1,'disconnected move graph in claimed window')
            # Verify each spanning edge independently from cells and tile types.
            for i,p in enumerate(parent):
                if i==p: continue
                before=set(T[i])-set(T[p]);after=set(T[p])-set(T[i])
                require(len(before)==len(after)==2,'tree edge is not a 2-flip')
                require(sum(before)==sum(after),'2-flip changes the covered cells')
                kb=sorted(K[x] for x in before);ka=sorted(K[x] for x in after)
                opposite=(kb==['L','R'] and ka[0]==ka[1] and ka[0][0]=='B') or (ka==['L','R'] and kb[0]==kb[1] and kb[0][0]=='B')
                mixed=any(s in kb and s in ka and len(set(kb+ka))==3 and
                          all(x==s or x[0]=='B' for x in kb+ka) for s in ('L','R'))
                require(opposite or mixed,'edge outside the two original Figure-5 types')
            # Parent chains themselves are the integral boundary certificates.
            for i in range(len(T)):
                path=[];j=i;seen=set()
                while parent[j]!=j:
                    require(j not in seen,'cyclic parent chain');seen.add(j)
                    path.append((parent[j],j));j=parent[j]
                boundary=Counter()
                for u,v in path:boundary[v]+=1;boundary[u]-=1
                target=Counter();target[i]+=1;target[roots[0]]-=1
                require(all(boundary[k]==target[k] for k in set(boundary)|set(target)), 'path boundary not T-root')
            row={'a':a,'b':b,'cells':len(V),'tilings':len(T),'move_edges':len(edges),
                 'components':len(components),'reduced_H0_rank':0,'delta':delta(a,b),
                 'stone_polynomial':list(poly),'minority_moments':moments,
                 'weight_one':sum(poly),'weight_three':F3,'dp_states':states}
            rows.append(row)
            certs.append({'a':a,'b':b,'cells':V,'tilings':T,'parent':parent,'root':roots[0]})
    manifest=dump('benzel-small-certificates.json',certs)
    constructions=[]
    for a in range(2,31):
        for b in range(2,31):
            if a>2*b or b>2*a or (a+b)%3!=1:continue
            V=set(cells(a,b));partition=right_partition(a,b)
            flat=[v for t in partition for v in t]
            require(len(flat)==len(set(flat))==len(V) and set(flat)==V,'residue construction is not exact cover')
            constructions.append({'a':a,'b':b,'cells':len(V),'right_stones':len(partition)})
    claim4=[];p7=[]
    for a in range(2,13):
        for b in range(a,min(12,2*a)+1):
            V=cells(a,b);D=delta(a,b)
            for target,kinds,eligible,out in [('P04',('L','B0','B1','B2'),D<=0,claim4),
                                               ('P07',('R','B0','B1','B2'),D>=0,p7)]:
                if not eligible:continue
                witness,states,K=find_cover(V,kinds)
                require(witness is not None,target+' lacks cover in stated finite window')
                verify_cover(V,witness,K)
                out.append({'a':a,'b':b,'delta':D,'states':states,'cells':V,'witness':witness})
    claim6=[]
    for n in range(5,12):
        p,states=count_polynomial(cells(n,2*n-3),('R','B0','B1','B2'))
        value,remainder=divmod((3*n+3)*factorial(3*n-7),factorial(n-5)*factorial(2*n-1))
        require(remainder==0 and sum(p)==value,'P06 exact formula disagrees')
        claim6.append({'n':n,'cells':len(cells(n,2*n-3)),'count':value,'dp_states':states})
    return {'scope':'Original benzel coordinates; finite claims do not settle P4/P6/P7/P19',
            'literal_geometry_crosschecks':geometries,'small_regions':rows,
            'weighted_jet_congruence_checks':jets,'P14_residue_constructions':constructions,
            'P04_witnesses':claim4,'P07_witnesses':p7,'P06_formula_checks':claim6,
            'spanning_certificates':manifest}

def subsequences_dp(w,k):
    levels=[[1]]+[[0]*(1<<j) for j in range(1,k+1)]
    for bit in w:
        b=int(bit)
        for j in range(k,0,-1):
            for v,c in enumerate(levels[j-1]):levels[j][2*v+b]+=c
    return tuple(tuple(v) for v in levels)

def subsequences_indices(w,k):
    c=[0]*(1<<k)
    for ids in combinations(range(len(w)),k):
        value=0
        for i in ids:value=2*value+int(w[i])
        c[value]+=1
    return tuple(c)

def word_checks():
    rows=[];checks=0;minimum={}
    for k in range(1,5):
        for n in range(k,13):
            fibres=defaultdict(list)
            for v in range(1<<n):
                w=f'{v:0{n}b}';sig=subsequences_dp(w,k)[k]
                require(sig==subsequences_indices(w,k),'deck algorithms disagree')
                checks+=1;fibres[sig].append(w)
            collisions=[v for v in fibres.values() if len(v)>1]
            rows.append({'n':n,'k':k,'words':1<<n,'fibres':len(fibres),
                         'collision_fibres':len(collisions),'largest_fibre':max(map(len,fibres.values())),
                         'first_collision':collisions[0][:2] if collisions else None})
            if collisions and k not in minimum:minimum[k]={'n':n,'witness':collisions[0][:2]}
    rec=[];u,v='0','1'
    for k in range(1,8):
        u,v=u+v,v+u;U=subsequences_dp(u,k+1);V=subsequences_dp(v,k+1)
        require(U[:k+1]==V[:k+1],'recursive family fails equal k-decks')
        leading=U[k+1][1]-V[k+1][1]
        require(leading==(-1)**(k-1)*2**((k-1)*(k-2)//2),'wrong first separating coefficient')
        rec.append({'k':k,'length':len(u),'first_word':u,'second_word':v,
                    'separating_pattern':'0'*k+'1','coefficient_difference':leading})
    # Source-level double-count identity, with exact division on realizable decks.
    for n in range(1,9):
        for k in range(1,min(n,4)+1):
            for value in range(1<<n):
                w=f'{value:0{n}b}';D=subsequences_dp(w,k)
                for j in range(k):
                    for pat in range(1<<j):
                        total=sum(count*subsequences_indices(f'{u:0{k}b}',j)[pat] for u,count in enumerate(D[k]))
                        require(total==comb(n-j,k-j)*D[j][pat],'lower-deck morphism identity')
    return {'exhaustive_dual_implementation_checks':checks,'n_max':12,'k_max':4,
            'all_windows':rows,'first_collisions_with_exhaustive_smaller_lengths':minimum,
            'known_recursive_family_replayed':rec,'claim':'Finite scans and reproduced known family; no general reconstruction bound solved'}

def mm(A,B):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]

def charpoly(A):
    """Exact Faddeev-LeVerrier coefficients, decreasing degree including leading 1."""
    n=len(A);B=[[int(i==j) for j in range(n)] for i in range(n)];out=[Q(1)]
    for k in range(1,n+1):
        B=mm(A,B);c=-sum(B[i][i] for i in range(n))/Q(k);out.append(c)
        for i in range(n):B[i][i]+=c
    require(all(x==0 for row in B for x in row),'Cayley-Hamilton residual')
    return out

def determinant(A):
    """Independent exact rational elimination, including row swaps."""
    A=[[Q(x) for x in row] for row in A];n=len(A);answer=Q(1)
    for k in range(n):
        pivot=next((i for i in range(k,n) if A[i][k]),None)
        if pivot is None:return Q(0)
        if pivot!=k:A[k],A[pivot]=A[pivot],A[k];answer=-answer
        p=A[k][k];answer*=p
        for i in range(k+1,n):
            q=A[i][k]/p
            for j in range(k+1,n):A[i][j]-=q*A[k][j]
    return answer

def matrix_checks():
    # Exact coefficient-map section for the full sign pattern [[+,+],[-,-]].
    section=0
    for u,v in product(range(-10,11),repeat=2):
        a=1+abs(u)+abs(v);d=-u-a;z=a*d-v
        require(a>0 and d<0 and z<0,'section left original sign chamber')
        require(charpoly([[a,1],[z,d]])==[1,u,v],'coefficient-map section identity')
        for b in (Q(1,3),Q(1),Q(5)):
            A=[[a,b],[z/b,d]];S=[[1,0],[0,1/b]];Si=[[1,0],[0,b]]
            require(mm(mm(Si,A),S)==[[a,1],[z,d]],'displayed diagonal conjugation fails')
        require(determinant([[-1,0],[a,-1]])==1,'coefficient Jacobian minor')
        section+=1
    def X(x):
        a,b,c,d,e,f,g,h=map(Q,x);A=[[Q(0) for _ in range(8)] for _ in range(8)]
        for i in range(7):A[i][i+1]=1
        for i,j,v in ((0,0,a),(1,0,g),(1,1,b),(2,1,c),(5,1,h),(7,0,f),(7,3,e),(7,5,d)):A[i][j]=v
        return A
    special=[('nilpotent',(1,-1,1,1,-1,1,-2,1),[1]+[0]*8),
             ('unipotent',(Q(1737,848),Q(5047,848),Q(-4452,193),Q(35,4),Q(2,7),Q(25,2),Q(1007374319,138787072),Q(-1325,7)),[(-1)**j*comb(8,j) for j in range(9)])]
    proofs=[]
    for name,x,expected in special:
        A=X(x);require(charpoly(A)==expected,'Shitov special matrix polynomial')
        for t in range(-4,5):
            det=determinant([[t*int(i==j)-A[i][j] for j in range(8)] for i in range(8)])
            value=sum(Q(c)*t**(8-j) for j,c in enumerate(expected))
            require(det==value,'independent determinant differs')
        proofs.append({'name':name,'coordinates':list(map(str,x)),'charpoly':expected,'evaluation_points':list(range(-4,5))})
    # Grone--Merris controls: spectra certified by exact characteristic polynomials.
    families=[]
    for n in range(1,10):
        edges=list(combinations(range(n),2));families.append((f'K{n}',n,edges,[n]*(n-1)+[0]))
    for a in range(1,5):
        for b in range(a,10-a):
            n=a+b;edges=[(i,a+j) for i in range(a) for j in range(b)]
            families.append((f'K{a},{b}',n,edges,[n]+[a]*(b-1)+[b]*(a-1)+[0]))
    spectral=[]
    for name,n,edges,spectrum in families:
        B=[[int(i==v)-int(i==u) for u,v in edges] for i in range(n)]
        L=mm(B,list(map(list,zip(*B)))) if edges else [[0]*n for _ in range(n)]
        expected=[Q(1)]
        for x in spectrum:
            new=[Q(0)]*(len(expected)+1)
            for i,c in enumerate(expected):new[i]+=c;new[i+1]-=x*c
            expected=new
        require(charpoly(L)==expected,'certified Laplacian spectrum mismatch')
        degree=[L[i][i] for i in range(n)];ds=[sum(d>=k for d in degree) for k in range(1,n+1)]
        spectrum=sorted(spectrum,reverse=True)
        require(all(sum(spectrum[:k])<=sum(ds[:k]) for k in range(1,n+1)),'majorization control')
        spectral.append({'graph':name,'spectrum':spectrum,'conjugate_degrees':ds})
    return {'AIM_S21_section_checks':section,'Shitov_exact_matrix_controls':proofs,
            'Grone_Merris_exact_families':spectral,
            'scope':'2x2 sign-map section; two 8x8 source matrices; exact finite graph spectra, not independent full Bai/Shitov proof audit'}

def parking_checks():
    # Reproduce the published forward and inverse DFS maps against independent sets.
    rows=[]
    families=[]
    for n in range(2,7):families.append((f'K{n}',n,tuple(combinations(range(n),2))))
    for mask in range(1<<6):
        edges=tuple(e for i,e in enumerate(combinations(range(4),2)) if mask>>i&1)
        reach={0}
        for _ in range(4):
            reach|={v for u,v in edges if u in reach}|{u for u,v in edges if v in reach}
        if len(reach)==4:families.append((f'G4-{mask}',4,edges))
    for name,n,edges in families:
        adj=[sorted((v if u==i else u for u,v in edges if i in (u,v)),reverse=True) for i in range(n)]
        def forward(values):
            f=[0]+list(values);burnt={0};tree=[]
            def visit(i):
                for j in adj[i]:
                    if j in burnt:continue
                    if f[j]==0:burnt.add(j);tree.append((i,j));visit(j)
                    else:f[j]-=1
            visit(0);return tuple(tree),burnt
        def inverse(tree):
            t=set(tree);burnt={0};values=[0]*n
            def visit(i):
                for j in adj[i]:
                    if j in burnt:continue
                    if (i,j) in t:burnt.add(j);visit(j)
                    else:values[j]+=1
            visit(0);require(len(burnt)==n,'inverse did not traverse input tree')
            return tuple(values[1:])
        def parking(f):
            for mask in range(1,1<<(n-1)):
                S={i for i in range(1,n) if mask>>(i-1)&1}
                if not any(f[i-1]<sum(j not in S for j in adj[i]) for i in S):return False
            return True
        def oriented(es):
            out=[];seen={0}
            while len(seen)<n:
                found=False
                for u,v in es:
                    if (u in seen)!=(v in seen):
                        if v in seen:u,v=v,u
                        out.append((u,v));seen.add(v);found=True
                if not found:return None
            return tuple(out)
        trees={frozenset(oriented(t)) for t in combinations(edges,n-1) if oriented(t) is not None}
        image=set();pfcount=0;hist=Counter()
        for f in product(*(range(len(adj[i])) for i in range(1,n))):
            valid=parking(f);T,burnt=forward(f)
            require(valid==(len(burnt)==n),'subset parking test differs from burning')
            if not valid:continue
            require(inverse(T)==f,'DFS inverse law')
            require(frozenset(T) in trees,'DFS image outside enumerated spanning trees')
            require(frozenset(T) not in image,'duplicate DFS tree');image.add(frozenset(T));pfcount+=1
            parent=dict((v,u) for u,v in T);kap=0
            for j in range(1,n):
                i=parent[j]
                while i:
                    kap+=int(i>j and j in adj[parent[i]]);i=parent[i]
            g=len(edges)-n+1
            require(kap==g-sum(f),'degree versus kappa-inversion identity')
            hist[sum(f)]+=1
        require(image==trees,'forward map omits a tree')
        for T in trees:require(frozenset(forward(inverse(tuple(T)))[0])==T,'second inverse law')
        rows.append({'graph':name,'vertices':n,'edges':len(edges),'parking_functions':pfcount,
                     'trees':len(trees),'degree_histogram':dict(hist)})
    return {'source':'Perkinson-Yang-Yu 1309.2201v2 Algorithms 1-2 and Theorems 3,5',
            'cases':rows,'scope':'Finite complete graphs K2 through K6 and every connected labelled graph on four vertices'}

def main():
    outputs={}
    for name,fn in [('benzels',benzel_checks),('words',word_checks),('matrices',matrix_checks),('parking',parking_checks)]:
        print('Checking '+name,flush=True);t=time.monotonic();value=fn();outputs[name]=dump(name+'.json',value)
        print('PASS '+name+' '+str(round(time.monotonic()-t,3))+'s',flush=True)
    result={'state':'PASS','validation':'Exact finite arithmetic and displayed certificates',
            'groups':outputs,'python':sys.version,'optimized':not __debug__,
            'upstream_Lean_build':False,'independent_specialist_review':False,
            'new_full_open_problem_resolutions':0,'agents_launched':0}
    dump('checks.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
