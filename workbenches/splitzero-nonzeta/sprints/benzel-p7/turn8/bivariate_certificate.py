"""Exact two-parameter original-cell incidence identities.

Ring Z[X^±1,Y^±1,Mx^±1,My^±1,Kx^±1,Ky^±1], with Mx=X^m,
My=Y^m, Kx=X^k, Ky=Y^k under the stated specialization map.
Every inverted factor involves X,Y only. No sampled parameter value is
used to certify the identity.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import json

Z=(0,)*6

def require(b,msg):
    if not b:raise ValueError(msg)
def mono(v=Z,c=1):return {tuple(v):c} if c else {}
def add(a,b):
    out=dict(a)
    for v,n in b.items():out[v]=out.get(v,0)+n
    return {v:n for v,n in out.items() if n}
def neg(a):return {v:-n for v,n in a.items()}
def mul(a,b):
    out={}
    for v,c in a.items():
        for w,d in b.items():
            u=tuple(x+y for x,y in zip(v,w));out[u]=out.get(u,0)+c*d
    return {v:n for v,n in out.items() if n}
def translate(a,v):return {tuple(x+y for x,y in zip(w,v)):n for w,n in a.items()}
def factor(v):return add(mono(),mono((*v,0,0,0,0),-1))

@dataclass(frozen=True)
class Term:
    num:dict
    den:tuple=()
    def associated(self):
        num=self.num;den=[]
        for v in self.den:
            require(v!=(0,0),'Zero denominator')
            if v[0]<0 or(v[0]==0 and v[1]<0):
                w=(-v[0],-v[1])
                # 1/(1-X^-a Y^-b) = -X^a Y^b/(1-X^a Y^b)
                num=neg(translate(num,(*w,0,0,0,0)));v=w
            den.append(v)
        return Term(num,tuple(sorted(den)))

class E:
    def __init__(self,terms=()):self.terms=tuple(t.associated() for t in terms if t.num)
    def __add__(self,b):return E(self.terms+b.terms)
    def __neg__(self):return E(Term(neg(t.num),t.den)for t in self.terms)
    def __sub__(self,b):return self+-b
    def __mul__(self,b):return E(Term(mul(t.num,u.num),t.den+u.den)for t in self.terms for u in b.terms)
    def transform(self,A,offset=(0,0)):
        def vmap(v):
            out=[]
            for i in range(0,6,2):
                x,y=v[i:i+2];out.extend((A[0][0]*x+A[0][1]*y,A[1][0]*x+A[1][1]*y))
            out[0]+=offset[0];out[1]+=offset[1]
            return tuple(out)
        terms=[]
        for t in self.terms:
            num={}
            for v,n in t.num.items():
                w=vmap(v);num[w]=num.get(w,0)+n
            den=tuple((A[0][0]*x+A[0][1]*y,A[1][0]*x+A[1][1]*y)for x,y in t.den)
            terms.append(Term(num,den))
        return E(terms)
    def verify_zero(self):
        common=Counter()
        for t in self.terms:
            for v,n in Counter(t.den).items():common[v]=max(common[v],n)
        out={};count=0
        for t in self.terms:
            p=t.num
            for v,n in (common-Counter(t.den)).items():
                for _ in range(n):p=mul(p,factor(v))
            count+=len(p);out=add(out,p)
        require(not out,'Nonzero integer Laurent numerator: '+str(list(out.items())[:5]))
        return {'rational_terms':len(self.terms),'denominator_factors':[[list(v),n]for v,n in sorted(common.items())],
                'expanded_terms_before_addition':count,'remaining_numerator_terms':0,
                'proof_domain':'k>=2, m>=3*k+2, both integers; formal identity verified before specialization'}

def point(x0=0,y0=0,xm=0,ym=0,xk=0,yk=0):return E((Term(mono((x0,y0,xm,ym,xk,yk))),))
def char(kind):
    offsets={'H':[(0,0),(1,0),(2,0)],'V':[(0,0),(0,1),(0,2)],
             'D':[(0,0),(1,-1),(2,-2)],'R':[(0,0),(1,0),(0,1)]}[kind]
    return E((Term({(x,y,0,0,0,0):1 for x,y in offsets}),))
def power(r,I):
    """r=(a,b); I=(coefficient of m, coefficient of k, constant)."""
    a,b=r;nm,nk,c=I;return point(a*c,b*c,a*nm,b*nm,a*nk,b*nk)
def geo(r,I):
    require(r!=(0,0),'This certificate does not replace a constant ratio by a geometric fraction')
    numerator=(point()-power(r,I)).terms
    return E(Term(t.num,t.den+(r,))for t in numerator)
def family(kind,x,y,I,J=None):
    """x,y=(m,k,i,j,constant); 0<=i<I; 0<=j<J0+J_i*i."""
    xm,xk,xi,xj,xc=x;ym,yk,yi,yj,yc=y
    start=point(xc,yc,xm,ym,xk,yk);r=(xi,yi);s=(xj,yj)
    if J is None:ans=geo(r,I)
    else:
        jm,jk,jc,ji=J
        require(s!=(0,0),'Inner constant ratio not part of this certificate')
        ans=geo(r,I)-power(s,(jm,jk,jc))*geo((r[0]+ji*s[0],r[1]+ji*s[1]),I)
        ans=E(Term(t.num,t.den+(s,))for t in ans.terms)
    return char(kind)*start*ans

def rotate(e):return e.transform(((0,1),(-1,-1)),(0,1))
def reflect(e):return e.transform(((1,0),(-1,-1)),(0,1))
def orbit(e):return e+rotate(e)+rotate(rotate(e))

def group(key):
    import families
    ans=E()
    for row in families.specifications()[key]:
        ans+=family(row['kind'],row['x'],row['y'],row['I'],row['J'])
    return ans

def source_sector():return group('source')
def corner():return group('corner')

def identity():
    # Long H: ell=i, y=1-m+k-i+j, j<m-3k+i.
    long=group('long')
    B=orbit(long+point(ym=-1)*corner())
    A=orbit(reflect(source_sector()))
    Del=orbit(group('deleted'))
    M=orbit(family_cell())
    return B-A-Del+M

def family_cell():
    return point(0,1,0,-1,3,3)*geo((-1,-1),(0,3,0))

def base_case_identity():
    # k=1, checked separately so no negative loop length enters a proof.
    long=family('H',(0,0,1,0,2),(-1,0,1,0,2),(1,0,-3))
    C=point(-1,1)*char('V')+point()*char('V')+point(1,-1)*char('V')+point(0,3)*char('D')
    sec=family('H',(-1,0,1,0,0),(0,0,1,0,1),(0,0,3))
    sec+=family('H',(-1,0,1,0,2),(0,0,1,0,4),(1,0,-2))
    B=orbit(long+point(ym=-1)*C)
    A=orbit(reflect(sec))
    deleted=orbit(point(-2,0,1,0)*char('R'))
    missing=orbit(point(1,2,0,-1)*geo((1,1),(0,0,3)))
    return B-A-deleted+missing

def verify_index_nonnegativity():
    import families
    receipt=[]
    # Exact affine bijection: k=K+2, m=M+3K+8; K,M are nonnegative.
    # Inverse: K=k-2, M=m-3k-2.
    def expansion(a):
        am,ak,c=a
        return (am,3*am+ak,8*am+2*ak+c)
    for group in ('source','corner','long','deleted'):
        for index,row in enumerate(families.specifications()[group]):
            I=tuple(row['I']);bound=expansion(I)
            require(all(c>=0 for c in bound),'Unproved nonnegative outer range')
            item={'group':group,'index':index,'I_in_M_K_constant':bound}
            if row['J'] is not None:
                jm,jk,jc,ji=row['J']
                # A linear function of i attains its minimum at 0 or I-1.
                endpoint=(jm,jk,jc) if ji>=0 else (jm+ji*I[0],jk+ji*I[1],jc+ji*(I[2]-1))
                jbound=expansion(endpoint)
                require(all(c>=0 for c in jbound),'Unproved nonnegative inner range')
                item['J_lower_bound_in_M_K_constant']=jbound
            receipt.append(item)
    return receipt

def verify_all():
    main=identity().verify_zero()
    base=base_case_identity().verify_zero()
    base['proof_domain']='k=1, every integer m>=5; no negative index length'
    return {'status':'PASS','main':main,'k1':base,'exact_index_bounds':verify_index_nonnegativity()}

if __name__=='__main__':
    print(json.dumps(verify_all(),indent=2))
