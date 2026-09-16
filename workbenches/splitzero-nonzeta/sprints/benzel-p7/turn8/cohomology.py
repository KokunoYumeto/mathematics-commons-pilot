"""Original matching comparison kernels and Split-Zero support complexes.

Integer generators, original cell incidences, and all support labels are
retained. This module does not substitute signed cycles for positive tilings.
"""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass
import construction as C
import geometry as G


def clean(v):
    G.require(all(type(n)is int for n in v.values()),'Integral coefficients required')
    return {g:n for g,n in v.items() if n}


def add(*vectors):
    z=Counter()
    for v in vectors:z.update(v)
    return clean(z)


def scale(n,v):
    G.require(type(n)is int,'Integer scalar required')
    return clean({g:n*c for g,c in v.items()})


def unit(generators):return dict(Counter(generators))

def join(a,b):
    if a is None:return b
    if b is None:return a
    return frozenset(a)|frozenset(b)

@dataclass(frozen=True)
class Scalar:
    present:bool
    amplitude:int=0
    def __post_init__(self):
        G.require(type(self.present)is bool and type(self.amplitude)is int,'G(Z) scalar type')
        G.require(self.present or self.amplitude==0,'Absent scalar has no amplitude')
    def __add__(self,b):return Scalar(self.present or b.present,self.amplitude+b.amplitude)
    def __mul__(self,b):return Scalar(self.present and b.present,self.amplitude*b.amplitude)
    def reflection(self):return self.amplitude

TAU=Scalar(False);E=Scalar(True,0);ONE=Scalar(True,1)

class Supports:
    def __init__(self,m:int,k:int):
        self.m=m;self.k=k;self.old=tuple(sorted(C.source(m,k)))
        self.omega=G.omega(G.triangular(m)-3*k)
    def label(self,A):
        if A is None:return None
        A=frozenset(A)
        G.require(all(type(i)is int and 0<=i<len(self.old)for i in A),'Release label outside original source')
        return A
    def cells(self,A):
        A=self.label(A)
        if A is None:return frozenset()
        return self.omega|frozenset(p for i in A for p in self.old[i][1])
    def eta(self,A,B):
        A=self.label(A);B=self.label(B)
        G.require(A is not None and B is not None and A<=B,'Supported inclusion required')
        return unit(self.old[i]for i in B-A)
    def validate_chain(self,A,n):
        cells=self.cells(A);n=clean(n)
        for t in n:
            G.anchor(t);G.require(set(t[1])<=cells,'Original tile outside this support')
        return n
    def augmented_d(self,A,r,n):
        G.require(type(r)is int and (A is not None or r==0),'Typed charge at bottom')
        n=self.validate_chain(A,n)
        return add(G.chain_boundary(n),scale(-r,unit(self.cells(A))))
    def augmented_transition(self,A,B,r,n):
        n=self.validate_chain(A,n)
        if A is None:
            G.require(r==0 and not n,'Bottom module is zero');return 0,{}
        return r,add(n,scale(r,self.eta(A,B)))
    def positive_cycle(self,A,r,n):
        n=self.validate_chain(A,n)
        return r==1 and all(v>=0 for v in n.values()) and not self.augmented_d(A,r,n)

@dataclass
class Total:
    m:int
    k:int
    degree:int
    label:object
    amplitude:dict
    def __post_init__(self):
        S=Supports(self.m,self.k);self.label=S.label(self.label);self.amplitude=clean(self.amplitude)
        cells=S.cells(self.label)
        if self.degree==0:
            S.validate_chain(self.label,self.amplitude)
            G.require(all(t[0]!='R'for t in self.amplitude),'This is the bone subcomplex')
        elif self.degree==1:G.require(set(self.amplitude)<=cells,'Original cell outside support')
        elif self.degree==2:G.require(not self.amplitude,'Degree two is the zero module')
        else:raise ValueError('Degrees are 0,1,2')
    def __add__(self,b):
        G.require((self.m,self.k,self.degree)==(b.m,b.k,b.degree),'Cochain type mismatch')
        return Total(self.m,self.k,self.degree,join(self.label,b.label),add(self.amplitude,b.amplitude))
    def smul(self,a):return Total(self.m,self.k,self.degree,self.label if a.present else None,scale(a.amplitude,self.amplitude))
    def d(self):
        G.require(self.degree<2,'Following degree absent')
        return Total(self.m,self.k,self.degree+1,self.label,G.chain_boundary(self.amplitude)if self.degree==0 else{})

class MatchingKernel:
    """Construct K=B_new/(B_old intersect B_new), on original cell edges.

A and B are the actual matchings of the displayed repair. Each closed
component gives exactly one primitive intersection relation. Forest paths
give integral duals on every original cell, not numerical nullspace vectors.
"""
    def __init__(self,A,B):
        self.A=tuple(sorted(A));self.B=tuple(sorted(B));self.na=len(self.A);self.nb=len(self.B)
        ao={};bo={}
        for ts,owners in ((self.A,ao),(self.B,bo)):
            for j,t in enumerate(ts):
                G.anchor(t)
                for p in t[1]:
                    G.require(p not in owners,'Input is not an original matching');owners[p]=j
        self.edges=[];self.ground=self.na+self.nb;self.adj={v:[]for v in range(self.ground+1)}
        for cell in sorted(set(ao)|set(bo)):
            u=ao[cell]if cell in ao else self.ground
            v=self.na+bo[cell]if cell in bo else self.ground
            self.edges.append((u,v,cell))
            self.adj[u].append((v,cell,1));self.adj[v].append((u,cell,-1))
        self.parents={};self.roots={};self.closed=[];seen=set()
        # The ground component includes every open component and preserves
        # all original single-owner cell edges. Remaining components are closed.
        for seed in [self.ground]+list(range(self.ground)):
            if seed in seen:continue
            comp=set();todo=[seed]
            while todo:
                u=todo.pop()
                if u in comp:continue
                comp.add(u);todo.extend(v for v,_,_ in self.adj[u]if v not in comp)
            seen|=comp
            if self.ground in comp:root=self.ground
            else:
                bs=sorted(v-self.na for v in comp if self.na<=v<self.ground)
                G.require(bs,'Closed component has no new bone')
                root=self.na+bs[0];self.closed.append((tuple(sorted(v for v in comp if v<self.na)),tuple(bs)))
            self.parents[root]=None;self.roots[root]=root;Q=deque([root])
            while Q:
                u=Q.popleft()
                for v,cell,sign in sorted(self.adj[u]):
                    if v in self.parents:continue
                    self.parents[v]=(u,cell,sign);self.roots[v]=root;Q.append(v)
        pivots={bs[0]for _,bs in self.closed}
        self.basis=tuple(j for j in range(self.nb)if j not in pivots)
    def coordinates(self,b):
        G.require(len(b)==self.nb and all(type(z)is int for z in b),'Original new-bone coefficient vector required')
        v=list(b)
        for _,bs in self.closed:
            pivot=b[bs[0]]
            for j in bs:v[j]-=pivot
        return tuple(v[j]for j in self.basis)
    def inverse_coordinates(self,coords):
        G.require(len(coords)==len(self.basis) and all(type(z)is int for z in coords),'Kernel coordinate type')
        out=[0]*self.nb
        for j,n in zip(self.basis,coords):out[j]=n
        return tuple(out)
    def dual(self,j):
        G.require(j in self.basis,'New-bone pivot has no independent coordinate')
        u=self.na+j;out=Counter()
        while self.parents[u] is not None:
            parent,cell,sign=self.parents[u];out[cell]+=sign;u=parent
        return clean(out)
    def pairing(self,y,t):return sum(y.get(p,0)for p in t[1])
    def check_relations(self):
        for ais,bs in self.closed:
            G.require(G.incidence(self.A[i]for i in ais)==G.incidence(self.B[j]for j in bs),'Intersection generator mismatch')
        return len(self.closed)
    def check_dual(self,j):
        y=self.dual(j);root=self.roots[self.na+j]
        G.require(all(self.pairing(y,t)==0 for t in self.A),'Dual fails original old boundary')
        for z,t in enumerate(self.B):
            wanted=int(z==j)-int(root==self.na+z)
            G.require(self.pairing(y,t)==wanted,'Dual forest path is not the stated original evaluation')
        return len(y)
