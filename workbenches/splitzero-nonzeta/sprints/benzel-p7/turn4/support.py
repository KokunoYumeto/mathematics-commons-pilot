"""Original fifth-collar supports and typed G(Z) cochain operations.

The bottom support is None. The empty RELEASE SET is a nonbottom support
containing the collar and source stone. These are never identified.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import hashlib, importlib.util, json
from functools import lru_cache

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'turn3'
PINS = {'construction.py': '08c27a9f678a98e24b8b94e397f915d066c9f8a6',
        'tables.json': '27135b9dcadd96481b5330e8889c9bbab4871714'}
for name, digest in PINS.items():
    data = (PARENT/name).read_bytes()
    actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual != digest:
        raise ValueError('Changed original source: '+name)
spec = importlib.util.spec_from_file_location('original_benzel_construction', PARENT/'construction.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
ALL = frozenset(range(16))
DUALS = json.loads((ROOT/'dual_certificates.json').read_text())
PATCH = json.loads((ROOT/'signed_patch.json').read_text())

def shifted_tile(t, d):
    kind, u, v = t
    return C.tile(kind, u-d, v+d)

@lru_cache(maxsize=128, typed=True)
def released(d):
    original = C.removed(d,5)
    return original[0], original[1:]

@lru_cache(maxsize=128, typed=True)
def base_support(d):
    stone, _ = released(d)
    source = C.translate(C.tiling(d,4),(1,1))
    collar = C.region(d,5) - set(C.incidence(source))
    return frozenset(collar | set(stone[1]))

@lru_cache(maxsize=4096, typed=True)
def support_cells(d, A):
    if type(d) is not int or d < 4:
        raise ValueError('The original domain is integer d>=4')
    if A is None:
        return frozenset()
    A = frozenset(A)
    if not A <= ALL:
        raise ValueError('Release label outside original dictionary')
    stone, bones = released(d)
    return base_support(d) | frozenset(c for i in A for c in bones[i][1])

def all_bones(cells):
    return tuple(C.tile(kind,x,y) for x,y in sorted(cells) for kind in 'DHV'
                 if set(C.tile(kind,x,y)[1]) <= cells)

def boundary(chain):
    out = Counter()
    for tile, value in chain.items():
        for cell in tile[1]:
            out[cell] += value
    return {c:n for c,n in out.items() if n}

def unit(cells):
    return {c:1 for c in cells}

def add_vectors(*vs):
    out=Counter()
    for v in vs:
        out.update(v)
    return {c:n for c,n in out.items() if n}

def scale(v,n):
    return {c:n*x for c,x in v.items() if n*x}

def signed_at_15(d):
    """An integral bone chain over the actual 15-release support."""
    gamma=Counter({t:1 for t in C.replacements(d,5)})
    for t in PATCH['removed_new_bones']:
        gamma[shifted_tile(t,d)] -= 1
    for t,n in PATCH['signed_new_bones']:
        gamma[shifted_tile(t,d)] += n
    return {t:n for t,n in gamma.items() if n}

def fixed_vector_preimage(d):
    """Boundary equals the fixed collar-plus-stone vector on release level zero."""
    gamma=Counter(signed_at_15(d))
    _,bs=released(d)
    for b in bs[:15]:
        gamma[b]-=1
    return {t:n for t,n in gamma.items() if n}

@dataclass(frozen=True)
class Scalar:
    present: bool
    amplitude: int = 0
    def __post_init__(self):
        if type(self.amplitude) is not int or (not self.present and self.amplitude):
            raise ValueError('Absent scalar cannot carry nonzero amplitude')
    def __add__(self, other):
        return Scalar(self.present or other.present, self.amplitude+other.amplitude)
    def __mul__(self, other):
        return Scalar(self.present and other.present, self.amplitude*other.amplitude)
    def reflection(self):
        return self.amplitude
TAU=Scalar(False)
E=Scalar(True,0)
ONE=Scalar(True,1)

def join(A,B):
    if A is None:return B
    if B is None:return A
    return frozenset(A)|frozenset(B)

@dataclass
class Total:
    """A reconstructed original cochain: degree 0 tiles, 1 cells, 2 zero."""
    d: int
    degree: int
    label: frozenset | None
    amplitude: dict
    def __post_init__(self):
        if self.label is not None:self.label=frozenset(self.label)
        cells=support_cells(self.d,self.label)
        self.amplitude={g:n for g,n in self.amplitude.items() if n}
        if any(type(n) is not int for n in self.amplitude.values()):
            raise ValueError('Cochain coefficients must remain integral')
        if self.degree==0:
            permitted=set(all_bones(cells))
        elif self.degree==1:permitted=set(cells)
        elif self.degree==2:permitted=set()
        else:raise ValueError('Original degrees are 0,1,2')
        if not set(self.amplitude)<=permitted:
            raise ValueError('Generator outside its original support/degree')
    def __add__(self,other):
        if (self.d,self.degree)!=(other.d,other.degree):raise ValueError('Typed degree mismatch')
        return Total(self.d,self.degree,join(self.label,other.label),
                     add_vectors(self.amplitude,other.amplitude))
    def smul(self,a):
        return Total(self.d,self.degree,self.label if a.present else None,
                     scale(self.amplitude,a.amplitude))
    def differential(self):
        if self.degree==0:return Total(self.d,1,self.label,boundary(self.amplitude))
        if self.degree==1:return Total(self.d,2,self.label,{})
        raise ValueError('No following degree supplied')

@dataclass(frozen=True)
class CyclicClass:
    """The computed integral subdiagram generated by the original residual.

level=None is bottom. At levels 0..14 the class is free of rank one;
levels 15,16 have only their own supported zero. This model is justified
by the integral preimage and evaluation retraction in PROOF.md.
"""
    level: int | None
    value: int=0
    def __post_init__(self):
        if self.level is not None and (type(self.level) is not int or not 0<=self.level<=16):
            raise ValueError('Unknown support level')
        if type(self.value) is not int:raise ValueError('Integral class required')
        if (self.level is None or self.level>=15) and self.value:
            raise ValueError('This fibre has zero amplitude only')
    def transport(self,j):
        if j is None or (self.level is not None and j<self.level):raise ValueError('No reverse transition')
        return CyclicClass(j, self.value if j<15 else 0)
    def __add__(self,other):
        if self.level is None:return other
        if other.level is None:return self
        j=max(self.level,other.level)
        return CyclicClass(j,self.value+other.value if j<15 else 0)
    def smul(self,a):
        if not a.present:return CyclicClass(None)
        return CyclicClass(self.level,a.amplitude*self.value)

@dataclass
class Augmented:
    """The genuine linear complex whose charge-one positive cycles are repairs.

The coherent arrow A->B sends (r,n) to (r,n+r*eta_AB); addition must
transport BOTH summands through these actual arrows before adding.
"""
    d: int
    label: frozenset | None
    charge: int
    chain: dict
    def __post_init__(self):
        if type(self.charge) is not int:raise ValueError('Integral charge required')
        if self.label is not None:self.label=frozenset(self.label)
        self.chain=Total(self.d,0,self.label,self.chain).amplitude
        if self.label is None and self.charge:raise ValueError('Bottom fibre has charge zero')
    def transport(self,B):
        if B is None:
            if self.label is not None:raise ValueError('No transport into absent support')
            return self
        B=frozenset(B)
        if not B<=ALL or (self.label is not None and not self.label<=B):raise ValueError('Invalid support arrow')
        if self.label is None:return Augmented(self.d,B,0,{})
        _,bs=released(self.d)
        eta={bs[i]:self.charge for i in B-self.label}
        return Augmented(self.d,B,self.charge,add_vectors(self.chain,eta))
    def __add__(self,other):
        if self.d!=other.d:raise ValueError('Different parameter fibres')
        J=join(self.label,other.label);a=self.transport(J);b=other.transport(J)
        return Augmented(self.d,J,a.charge+b.charge,add_vectors(a.chain,b.chain))
    def smul(self,a):
        if not a.present:return Augmented(self.d,None,0,{})
        return Augmented(self.d,self.label,a.amplitude*self.charge,scale(self.chain,a.amplitude))
    def differential(self):
        vec=add_vectors(boundary(self.chain),scale(unit(support_cells(self.d,self.label)),-self.charge))
        return Total(self.d,1,self.label,vec)
