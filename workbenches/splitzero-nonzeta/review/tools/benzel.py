"""Exact benzel cells, the five original prototiles, covers and Figure-5 moves.
All arithmetic is integral. Coordinates are triples summing to one.
"""
from __future__ import annotations
from collections import defaultdict, deque
from functools import lru_cache
from itertools import combinations

E=((1,0,0),(0,1,0),(0,0,1))
DIR=((1,-1,0),(1,0,-1),(0,1,-1))
def plus(x,y): return tuple(a+b for a,b in zip(x,y))
def minus(x,y): return tuple(a-b for a,b in zip(x,y))

def cells(a:int,b:int):
    if min(a,b)<2 or a>2*b or b>2*a: raise ValueError('outside original benzel domain')
    m=max(a,b)+2
    return tuple((i,j,1-i-j) for i in range(-m,m+1) for j in range(-m,m+1)
                 if all(1-a <= d <= b-1 for d in (j-i,1-i-2*j,2*i+j-1)))

def placements(V, kinds=('R','L','B0','B1','B2')):
    V=tuple(V); lookup={v:i for i,v in enumerate(V)}; out={}
    def add(tile,kind):
        tile=frozenset(tile)
        if kind in kinds and len(tile)==3 and tile<=lookup.keys():
            mask=sum(1<<lookup[v] for v in tile); out[mask]=kind
    for v in V:
        for j,d in enumerate(DIR): add((minus(v,d),v,plus(v,d)),f'B{j}')
        for e in E:
            u=minus(v,e); add((plus(u,f) for f in E),'R')
            u=plus(v,e); add((minus(u,f) for f in E),'L')
    return tuple(sorted(out)),out

def count_polynomial(V,kinds=('R','L','B0','B1','B2')):
    """Coefficient s counts covers with exactly s stones. Fewest-options pivot."""
    tiles,kind=placements(V,kinds); n=len(V)
    at=[tuple(t for t in tiles if t>>i&1) for i in range(n)]
    @lru_cache(None)
    def rec(mask):
        if not mask: return (1,)
        opts=min((tuple(t for t in at[i] if t&mask==t) for i in range(n) if mask>>i&1),key=len)
        ans=[]
        for t in opts:
            p=rec(mask^t); shift=int(kind[t] in ('R','L'))
            if len(ans)<len(p)+shift: ans.extend([0]*(len(p)+shift-len(ans)))
            for j,c in enumerate(p): ans[j+shift]+=c
        while ans and ans[-1]==0: ans.pop()
        return tuple(ans)
    p=rec((1<<n)-1)
    return p,rec.cache_info().currsize

def covers(V,kinds=('R','L','B0','B1','B2'),limit=20000):
    """Independent enumeration: fixed least-cell pivot, no DP counting cache."""
    tiles,kind=placements(V,kinds); n=len(V)
    at=[tuple(t for t in tiles if t>>i&1) for i in range(n)]
    ans=[]
    def rec(mask,selected):
        if not mask:
            if len(ans)>=limit: raise RuntimeError('explicit cover bound exceeded')
            ans.append(tuple(sorted(selected))); return
        i=(mask&-mask).bit_length()-1
        for t in at[i]:
            if t&mask==t: rec(mask^t,selected+(t,))
    rec((1<<n)-1,())
    return tuple(sorted(ans)),kind

def allowed_pair_change(before,after,kind):
    if len(before)!=2 or len(after)!=2: return False
    b=[kind[t] for t in before]; a=[kind[t] for t in after]
    # Figure 5: opposite stones <-> two parallel bones.
    if sorted(b)==['L','R'] and a[0]==a[1] and a[0].startswith('B'): return True
    if sorted(a)==['L','R'] and b[0]==b[1] and b[0].startswith('B'): return True
    # Same-oriented stone + bone <-> that orientation + a different bone direction.
    for s in ('R','L'):
        if b.count(s)==a.count(s)==1:
            bb=next(x for x in b if x!=s); aa=next(x for x in a if x!=s)
            if bb.startswith('B') and aa.startswith('B') and bb!=aa: return True
    return False

def move_graph(T,kind):
    buckets=defaultdict(list)
    for i,t in enumerate(T):
        for pair in combinations(t,2):
            remain=tuple(x for x in t if x not in pair)
            buckets[remain].append((i,pair))
    edges=set()
    for group in buckets.values():
        for (i,p),(j,q) in combinations(group,2):
            if allowed_pair_change(p,q,kind): edges.add((min(i,j),max(i,j)))
    return tuple(sorted(edges))

def forest(n,edges):
    adj=[[] for _ in range(n)]
    for i,j in edges: adj[i].append(j); adj[j].append(i)
    parent=[None]*n; roots=[]; components=[]
    for r in range(n):
        if parent[r] is not None: continue
        roots.append(r);parent[r]=r;q=deque([r]);c=[]
        while q:
            v=q.popleft();c.append(v)
            for w in adj[v]:
                if parent[w] is None: parent[w]=v;q.append(w)
        components.append(c)
    return roots,parent,components

if __name__=='__main__':
    import time
    for a in range(2,8):
        for b in range(a,min(7,2*a)+1):
            t=time.monotonic(); V=cells(a,b);p,states=count_polynomial(V)
            print(a,b,len(V),sum(p),p,states,round(time.monotonic()-t,3),flush=True)

def delta(a,b):
    """Conway--Lagarias stone-count value; source area invariant is 3*delta."""
    r=(a+b)%3
    numerator=(3*(a-b)**2-a-b if r==0 else
               -a*a+4*a*b-b*b-a-b+2 if r==1 else
               3*(a-b)**2+a+b-2)
    q,rem=divmod(numerator,6)
    if rem: raise ArithmeticError('nonintegral stone-count invariant')
    return q

def right_partition(a,b):
    """Direct residue construction for the original a+b == 1 (mod 3) family."""
    if (a+b)%3!=1: raise ValueError('wrong residue family')
    V=cells(a,b); residue=(2-a)%3; anchors=set()
    for v in V:
        choices=[minus(v,e) for e in E if (minus(v,e)[1]-minus(v,e)[0])%3==residue]
        if len(choices)!=1: raise ArithmeticError('anchor uniqueness failed')
        anchors.add(choices[0])
    return tuple(sorted(tuple(sorted(plus(u,e) for e in E)) for u in anchors))

def find_cover(V,kinds,max_states=100000):
    """A witness, None for exhaustive nonexistence, or explicit bound exception."""
    tiles,kind=placements(V,kinds); n=len(V); visited=0
    at=[tuple(t for t in tiles if t>>i&1) for i in range(n)]
    @lru_cache(None)
    def rec(mask):
        nonlocal visited
        visited+=1
        if visited>max_states: raise RuntimeError('existence-search state cap exceeded')
        if not mask: return ()
        opts=min((tuple(t for t in at[i] if t&mask==t) for i in range(n) if mask>>i&1),key=len)
        for t in opts:
            rest=rec(mask^t)
            if rest is not None: return (t,)+rest
        return None
    return rec((1<<n)-1),visited,kind
