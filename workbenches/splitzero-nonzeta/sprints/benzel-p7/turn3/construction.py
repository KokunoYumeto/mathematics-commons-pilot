"""Literal integer tilings for the first five collars; no search or solver."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
TABLES = json.loads((ROOT / 'tables.json').read_text(encoding='utf-8'))
DIR = {'D': (1, -1), 'H': (1, 0), 'V': (0, 1)}

def tile(kind, x, y):
    offsets = ((0, 0), (1, 0), (0, 1)) if kind == 'R' else tuple(
        (u*DIR[kind][0], u*DIR[kind][1]) for u in range(3))
    return kind, tuple(sorted((x+a, y+b) for a, b in offsets))

def translate(tiles, shift):
    x, y = shift
    return tuple((k, tuple(sorted((a+x, b+y) for a, b in cells))) for k, cells in tiles)

def incidence(tiles):
    return Counter(c for _, cells in tiles for c in cells)

def differences(x, y):
    return y-x, 1-x-2*y, 2*x+y-1

def region(d, h):
    if type(d) is not int or type(h) is not int or d < 3 or h < 0:
        raise ValueError('Original parameter domain requires integer d>=3,h>=0')
    a, b = d+3*h, 2*d+3*h
    out = set()
    # All barycentric coordinates have absolute value <=max(a,b)+2.
    for x in range(-b-2, b+3):
        low = max(x+1-a, -((b+x-2)//2), 2-a-2*x)
        high = min(x+b-1, (a-x)//2, b-2*x)
        out.update((x, y) for y in range(low, high+1))
    return out

def replacements(d, h):
    a = TABLES[str(h)]
    return tuple(tile(k, X[0]*d+X[1]*r+X[2], Y[0]*d+Y[1]*r+Y[2])
                 for _, k, X, Y, U in a['families'] for r in range(U[0]*d+U[1]+1))

def removed(d, h):
    return tuple(tile(k, X[0]*d+X[1], Y[0]*d+Y[1])
                 for k, X, Y in TABLES[str(h)]['removed'])

def tiling(d, h):
    if type(d) is not int or type(h) is not int or h not in range(6):
        raise ValueError('Use integer h in 0..5')
    if d < (3 if h < 4 else 4):
        raise ValueError('Outside the proved construction domain')
    current = tuple(tile('R', d-2-2*r-s, r-s)
                    for r in range(d-1) for s in range(d-1-r))
    for stage in range(1, h+1):
        old = translate(current, TABLES[str(stage)]['shift'])
        take = removed(d, stage)
        if len(set(take)) != len(take) or any(old.count(t) != 1 for t in take):
            raise ValueError('A released original tile is missing or repeated')
        current = tuple(t for t in old if t not in take) + replacements(d, stage)
    return current

def reflect(tiles):
    kinds = {'R': 'R', 'D': 'H', 'H': 'D', 'V': 'V'}
    return tuple((kinds[k], tuple(sorted((x, 1-x-y) for x, y in cells)))
                 for k, cells in tiles)

def check_partition(tiles, cells):
    for kind, points in tiles:
        if kind not in (*DIR, 'R') or len(points) != 3 or len(set(points)) != 3:
            raise ValueError('Invalid placed tile')
        if kind == 'R':
            x = min(a for a, _ in points); y = min(b for _, b in points)
            good = set(points) == {(x, y), (x+1, y), (x, y+1)}
        else:
            dx, dy = DIR[kind]
            good = any(set(points) == {(x+t*dx, y+t*dy) for t in (-1, 0, 1)}
                       for x, y in points)
        if not good:
            raise ValueError('Tile fails independent shape classification')
    if incidence(tiles) != Counter({c: 1 for c in cells}):
        raise ValueError('Incorrect containment, overlap, or coverage')

def decode(tiles):
    return tuple((k, tuple(tuple(c) for c in cells)) for k, cells in tiles)
