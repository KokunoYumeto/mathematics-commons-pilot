"""Original integer benzel cells, tiles, and inverse coordinate maps.

No floating point, optimizer, or external package is used by this module.
"""
from __future__ import annotations
from collections import Counter
from math import isqrt

OFFSETS = {'R': ((0, 0), (1, 0), (0, 1)),
           'H': ((0, 0), (1, 0), (2, 0)),
           'V': ((0, 0), (0, 1), (0, 2)),
           'D': ((0, 0), (1, -1), (2, -2))}
DIRECTIONS = {'H': (1, 0), 'V': (0, 1), 'D': (1, -1)}

def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)

def triangular(n: int) -> int:
    require(type(n) is int and n >= 0, 'Nonnegative original integer required')
    return n * (n - 1) // 2

def block(n: int) -> int:
    """Unique r>=1 with C(r,2)<n<=C(r+1,2)."""
    require(type(n) is int and n >= 1, 'Positive original band argument required')
    r = (isqrt(8 * n + 1) - 1) // 2
    if r * (r + 1) // 2 < n:
        r += 1
    require(triangular(r) < n <= triangular(r + 1), 'Integer inverse failure')
    return r

def parameters(d: int, h: int) -> tuple[int, int]:
    require(type(d) is int and type(h) is int and d >= 3 and 0 <= h <= triangular(d),
            'Use d>=3 and 0<=h<=C(d,2), all integers')
    return d + 3 * h, 2 * d + 3 * h

def differences(p: tuple[int, int]) -> tuple[int, int, int]:
    x, y = p
    return y - x, 1 - x - 2 * y, 2 * x + y - 1

def contains(a: int, b: int, p: tuple[int, int]) -> bool:
    return all(1 - a <= z <= b - 1 for z in differences(p))

def region_ab(a: int, b: int) -> frozenset:
    require(type(a) is int and type(b) is int and a >= 1 and b >= 1, 'Positive integer bounds required')
    out = set()
    bound = max(a, b) + 2
    for x in range(-bound, bound + 1):
        low = max(x + 1 - a, -((b + x - 2) // 2), 2 - a - 2 * x)
        high = min(x + b - 1, (a - x) // 2, b - 2 * x)
        out.update((x, y) for y in range(low, high + 1))
    return frozenset(out)

def region(d: int, h: int) -> frozenset:
    return region_ab(*parameters(d, h))

def tile(kind: str, x: int, y: int) -> tuple:
    require(kind in OFFSETS and type(x) is int and type(y) is int, 'Literal original tile required')
    return kind, tuple(sorted((x + u, y + v) for u, v in OFFSETS[kind]))

def anchor(t: tuple) -> tuple[int, int]:
    kind, cells = t
    require(kind in OFFSETS and len(cells) == 3 and len(set(cells)) == 3, 'Invalid tile')
    for x, y in cells:
        for u, v in OFFSETS[kind]:
            if tile(kind, x - u, y - v) == t:
                return x - u, y - v
    raise ValueError('Cells do not have the original tile shape')

def rho(p: tuple[int, int]) -> tuple[int, int]:
    x, y = p
    return y, 1 - x - y

def reflect(p: tuple[int, int]) -> tuple[int, int]:
    x, y = p
    return x, 1 - x - y

def rotate_tile(t: tuple, power: int = 1) -> tuple:
    out = t
    for _ in range(power % 3):
        kind, cells = out
        out = {'R':'R', 'H':'V', 'V':'D', 'D':'H'}[kind], tuple(sorted(map(rho, cells)))
    return out

def reflect_tile(t: tuple) -> tuple:
    kind, cells = t
    return {'R':'R', 'H':'D', 'V':'V', 'D':'H'}[kind], tuple(sorted(map(reflect, cells)))

def orbit(p: tuple[int, int]) -> frozenset:
    return frozenset((p, rho(p), rho(rho(p))))

def incidence(tiles) -> Counter:
    return Counter(p for _, cells in tiles for p in cells)

def chain_boundary(chain: dict) -> dict:
    result = Counter()
    for (_, cells), coefficient in chain.items():
        require(type(coefficient) is int, 'Integral chain coefficient required')
        for p in cells:
            result[p] += coefficient
    return {p: n for p, n in result.items() if n}

def check_partition(tiles, cells) -> None:
    for t in tiles:
        anchor(t)
    require(incidence(tiles) == Counter({p: 1 for p in cells}), 'Incomplete, overlapping, or external cell coverage')

def decode(tiles) -> tuple:
    return tuple((k, tuple(sorted(tuple(c) for c in cs))) for k, cs in tiles)

def encode_anchors(tiles) -> list:
    return [[k, *anchor((k, cs))] for k, cs in sorted(tiles)]

def decode_anchors(rows) -> tuple:
    return tuple(tile(k, x, y) for k, x, y in rows)

def cell_rank(p: tuple[int, int]) -> tuple[int, int, int, int]:
    """Inverse to (k,m,j) -> rho^j(k-m,-m), with rank C(k,2)+m+1."""
    z = p
    for j in range(3):
        u, v, w = differences(z)
        if u < v and u < w:
            k = -u
            m = -z[1]
            require(k >= 1 and 0 <= m < k and z == (k-m, -m), 'Original shell inverse failed')
            return triangular(k) + m + 1, k, m, j
        z = rho(rho(z))
    raise ValueError('Original differences have no unique minimum')

def omega(delta: int) -> frozenset:
    require(type(delta) is int and delta >= 0, 'Nonnegative invariant required')
    out = set()
    for n in range(1, delta + 1):
        k = block(n)
        m = n - triangular(k) - 1
        out.update(orbit((k - m, -m)))
    require(len(out) == 3 * delta, 'Repeated original shell cell')
    return frozenset(out)
