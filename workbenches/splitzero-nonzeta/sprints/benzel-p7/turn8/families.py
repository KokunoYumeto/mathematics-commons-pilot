"""Shared literal affine families used by construction and symbolic proof.

There is no parameter substitution in the symbolic evaluator. The finite
expander checks every original index length before producing cell anchors.
"""
from __future__ import annotations
from pathlib import Path
import json
import geometry as G

ROOT=Path(__file__).resolve().parent

def specifications():
    data=json.loads((ROOT/'families.json').read_text(encoding='utf-8'))
    for key in ('source','corner','long','deleted'):
        G.require(isinstance(data[key],list),'Missing literal family')
        for row in data[key]:
            G.require(row['kind'] in G.OFFSETS,'Unknown original prototile')
            for name,size in (('x',5),('y',5),('I',3)):
                G.require(len(row[name])==size and all(type(z)is int for z in row[name]),'Malformed affine index')
            G.require(row['J'] is None or (len(row['J'])==4 and all(type(z)is int for z in row['J'])),'Malformed inner index')
    return data

def expand(key:str,m:int,k:int):
    G.require(type(k)is int and type(m)is int and k>=2 and m>=3*k+2,'Shared-family domain k>=2, m>=3k+2')
    out=[]
    for row in specifications()[key]:
        nm,nk,c=row['I'];n=nm*m+nk*k+c
        G.require(n>=0,'Negative outer index range')
        for i in range(n):
            if row['J'] is None:nj=1
            else:
                jm,jk,jc,ji=row['J'];nj=jm*m+jk*k+jc+ji*i
            G.require(nj>=0,'Negative inner index range')
            for j in range(nj):
                x=sum(a*b for a,b in zip(row['x'],(m,k,i,j,1)))
                y=sum(a*b for a,b in zip(row['y'],(m,k,i,j,1)))
                out.append(G.tile(row['kind'],x,y))
    return tuple(out)
