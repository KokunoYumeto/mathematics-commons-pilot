"""Uniform q=3k positive repairs on the original benzel cells.

Written research proof in PROOF.md; no solver is used. Domain: integer k>=1,
m>=3k+2, d>=m. Output uses the literal R,H,V,D prototiles.
"""
from __future__ import annotations
import geometry as G
import packing as P
from collections import Counter,defaultdict

def corner_new(k:int):
 G.require(type(k)is int and k>=1,'Positive integer corner parameter required')
 if k==1:return tuple(G.tile(t,x,y)for t,x,y in [('V',-1,1),('V',0,0),('V',1,-1),('D',0,3)])
 import families
 # The original corner anchors have zero coefficient of m in every family.
 G.require(all(not r['x'][0] and not r['y'][0] and not r['I'][0] and
               (r['J']is None or not r['J'][0]) for r in families.specifications()['corner']),
           'Corner acquired an undeclared m dependence')
 return families.expand('corner',3*k+2,k)

def new_bones(m,k):
 G.require(type(k)is int and type(m)is int and k>=1 and m>=3*k+2,'Use integers k>=1 and m>=3k+2')
 out=[]
 for l in range(k):
  for y in range(1-m+k-l,1-2*k):
   out.extend(G.rotate_tile(G.tile('H',y+m+3*l,y),p)for p in range(3))
 for t in corner_new(k):
  knd,cc=t;t=(knd,tuple(sorted((x,y-m)for x,y in cc)))
  out.extend(G.rotate_tile(t,p)for p in range(3))
 return tuple(out)

def deleted(m,k):return tuple(G.rotate_tile(G.tile('R',m-2-a,-a),p)for a in range(k)for p in range(3))

def source_labels(m:int,k:int):
    G.require(type(k)is int and k>=1 and type(m)is int and m>=3*k+2,
              'Use integers k>=1 and m>=3k+2')
    labels=[]
    for ell in range(k-1):
        labels += [(y,ell)for y in range(ell+1,m+2*k-3)]
        labels += [(m+2*k-2+ell+j,ell)for j in range(2)]
    labels += [(y,k-1)for y in range(k,m+3*k-1)]
    for ell in range(k,2*k-1):
        labels += [(y,ell)for y in range(ell+1,2*k+1)]
    G.require(len(labels)==len(set(labels)),'Duplicate original source label')
    out=[]
    for y,ell in labels:
        G.require(1<=y<=m+3*k and 0<=ell<min(y,3*k),'Source leaves common body')
        r=m-1 if y<=3*k else m
        x=y-r-2-3*ell
        for p in range(3):
            t=G.reflect_tile(G.rotate_tile(G.tile('H',x,y),p))
            out.append((p,y,ell,t))
    return tuple(out)

def source(m:int,k:int):
    return tuple(t for p,y,ell,t in source_labels(m,k))

def retained_stones(m:int,k:int):
    G.require(type(k)is int and k>=1 and type(m)is int and m>=3*k+2,
              'Use integers k>=1 and m>=3k+2')
    base=set(P.base_stones(m));rem=deleted(m,k)
    G.require(len(set(rem))==3*k and set(rem)<=base,'Original corner deletions not distinct base tiles')
    return tuple(sorted(base-set(rem)))

def patch(m:int,k:int):
    return new_bones(m,k)+retained_stones(m,k)

def receiving_generator(d:int,m:int,k:int,p:int,y:int,ell:int):
    G.require(type(d)is int and d>=m>=3*k+2 and k>=1,'Invalid exterior parameter')
    h=G.triangular(d)-G.triangular(m)+3*k
    if y<=h:
        j=y-1-ell;L=1-2*y-G.block(y+G.triangular(m)-3*k)
        role='prefix'
    else:
        G.require(d==m and y>3*k,'Unexpected finite tail role')
        j=3*k-1-ell;L=y-9*k-m+1
        role='tail'
    t=G.reflect_tile(G.rotate_tile(G.tile('H',L+3*j,y),p))
    return role,j,t

def complete(d:int,m:int,k:int):
    G.require(type(d)is int and type(m)is int and type(k)is int and k>=1 and d>=m>=3*k+2,
              'Use integer k>=1, m>=3k+2, d>=m')
    h=G.triangular(d)-G.triangular(m)+3*k
    old=P.packing(d,h);A=set(source(m,k))
    G.require(A<=set(old),'Source-to-target original generator map failed')
    return tuple(t for t in old if t not in A)+patch(m,k)
