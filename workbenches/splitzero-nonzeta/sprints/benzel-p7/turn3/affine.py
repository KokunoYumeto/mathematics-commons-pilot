"""Exact rational certificate generation. Acceptance recomputes all constraints."""
from fractions import Fraction as F

def contradiction(constraints):
    rows = [(tuple(map(F, a)), F(b), {i: F(1)}) for i, (a, b) in enumerate(constraints)]
    n = len(rows[0][0]); used = set()
    def prune(rows):
        best = {}
        for a, b, w in rows:
            if not any(a):
                if b < 0: return [], w
                continue
            scale = next(abs(x) for x in a if x)
            key = tuple(x/scale for x in a); rhs = b/scale
            if key not in best or rhs < best[key][1]:
                best[key] = key, rhs, {i: c/scale for i, c in w.items()}
        return list(best.values()), None
    rows, proof = prune(rows)
    if proof is not None: return proof
    for _ in range(n):
        if not rows: return None
        j = min((j for j in range(n) if j not in used), key=lambda j:
                sum(a[j] > 0 for a,b,w in rows)*sum(a[j] < 0 for a,b,w in rows))
        used.add(j)
        pos = [r for r in rows if r[0][j] > 0]
        neg = [r for r in rows if r[0][j] < 0]
        nxt = [r for r in rows if not r[0][j]]
        for a,b,w in pos:
            for c,d,v in neg:
                x,y = -c[j],a[j]
                weights = {i: x*z for i,z in w.items()}
                for i,z in v.items(): weights[i] = weights.get(i,0)+y*z
                nxt.append((tuple(x*p+y*q for p,q in zip(a,c)),x*b+y*d,weights))
        rows, proof = prune(nxt)
        if proof is not None: return proof
    return None
