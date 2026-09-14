#!/usr/bin/env python3
"""Exact replay of the third collar, support kernel and integral bone quotient.

The third-collar constructor has no search or numerical dependencies. Fourth-
collar entries are individual stored witnesses, not an all-parameter theorem.
Run alongside the unchanged turn-1 check.py. Python standard library only.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import time
import check as prior

ROOT = Path(__file__).resolve().parent
Cell = tuple[int, int]
Tile = tuple[str, tuple[Cell, ...]]
RingElement = tuple[int, int, int]  # a + b*omega + c*sigma; c modulo 3


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def third_bones(d: int) -> tuple[Tile, ...]:
    require(isinstance(d, int) and d >= 3, 'The third collar uses integer d>=3')
    out = [prior.bone('D', (-d-5+r, d+3-2*r)) for r in range(d+3)]
    out.extend(prior.bone('D', p) for p in
               ((-d-4, d+3), (-d-4, d+4), (-d-3, d+4)))
    out.extend(prior.bone('D', (-d-2+2*r, d+4-r)) for r in range(d+1))
    out.extend(prior.bone('H', (-d-3+2*r, d+5-r)) for r in range(d+2))
    out.extend(prior.bone('H', p) for p in ((d, 3), (d-2, 0), (d-2, 1)))
    out.extend(prior.bone('V', p) for p in
               ((d+1, 0), (d+2, 0), (d+3, 1), (d+4, -1), (d+5, -3)))
    return tuple(out)


def released_tiles(d: int) -> tuple[Tile, ...]:
    return (prior.stone((d-2, 0)), prior.bone('H', (d-1, 1)),
            prior.bone('H', (d, 0)))


def third_tiling(d: int) -> tuple[Tile, ...]:
    old = prior.translate(prior.second_tiling(d), (1, -2))
    released = released_tiles(d)
    require(all(old.count(t) == 1 for t in released), 'Released tile not in source')
    return tuple(t for t in old if t not in released) + third_bones(d)


def reflected(tiles: tuple[Tile, ...]) -> tuple[Tile, ...]:
    """Original barycentric involution (i,j,k)->(i,k,j)."""
    kinds = {'R': 'R', 'D': 'H', 'H': 'D', 'V': 'V'}
    return tuple((kinds[k], tuple(sorted((i, 1-i-j) for i, j in cells)))
                 for k, cells in tiles)


def cleaned(c: Counter) -> Counter:
    return Counter({k: v for k, v in c.items() if v != 0})


def signed_boundary(positive: tuple[Tile, ...], negative: tuple[Tile, ...]) -> Counter:
    result = prior.incidence(positive)
    result.subtract(prior.incidence(negative))
    return cleaned(result)


def bones_through(p: Cell) -> tuple[Tile, ...]:
    return tuple(prior.bone(k, (p[0]-u*di, p[1]-u*dj))
                 for k, (di, dj) in prior.DIRECTIONS.items() for u in range(3))


def ring_add(x: RingElement, y: RingElement) -> RingElement:
    return (x[0]+y[0], x[1]+y[1], (x[2]+y[2]) % 3)


def ring_scale(n: int, x: RingElement) -> RingElement:
    return (n*x[0], n*x[1], (n*x[2]) % 3)


def ring_mul(x: RingElement, y: RingElement) -> RingElement:
    a, b, c = x
    d, e, f = y
    return (a*d-b*e, a*e+b*d-b*e, ((a+b)*f+(d+e)*c) % 3)


def ring_power(x: RingElement, exponent: int) -> RingElement:
    require(exponent >= 0, 'Use explicit inverse for negative exponent')
    result = (1, 0, 0)
    while exponent:
        if exponent % 2:
            result = ring_mul(result, x)
        x = ring_mul(x, x)
        exponent //= 2
    return result


def cell_class(p: Cell) -> RingElement:
    """Proved expression X^i Y^j = omega^(i+2j) + j*sigma."""
    i, j = p
    a, b = ((1, 0), (0, 1), (-1, -1))[(i+2*j) % 3]
    return (a, b, j % 3)


def observed(coefficients: Counter) -> RingElement:
    result = (0, 0, 0)
    for p, n in coefficients.items():
        result = ring_add(result, ring_scale(n, cell_class(p)))
    return result


def jet_reduction(x: RingElement) -> tuple[int, int, int]:
    a, b, c = x
    return ((a+b) % 3, (b+c) % 3, c % 3)


def periodic_matrix() -> list[list[int]]:
    """Original boundary matrix after the proved X^3=Y^3=1 quotient."""
    cells = [(i, j) for i in range(3) for j in range(3)]
    columns = [Counter(((i+u*di) % 3, (j+u*dj) % 3) for u in range(3))
               for i, j in cells for di, dj in ((1, 0), (0, 1), (1, -1))]
    return [[column[p] for column in columns] for p in cells]


def smith_certificate(matrix: list[list[int]]) -> tuple[list[list[int]], list[list]]:
    """Integer row/column operations, each with an explicit integer inverse."""
    A = deepcopy(matrix)
    m, n = len(A), len(A[0])
    operations = []

    def swap(axis: str, i: int, j: int) -> None:
        if i == j:
            return
        if axis == 'r':
            A[i], A[j] = A[j], A[i]
        else:
            for row in A:
                row[i], row[j] = row[j], row[i]
        operations.append([axis, 'swap', i, j])

    def add(axis: str, i: int, j: int, q: int) -> None:
        if not q:
            return
        if axis == 'r':
            A[i] = [x+q*y for x, y in zip(A[i], A[j])]
        else:
            for row in A:
                row[i] += q*row[j]
        operations.append([axis, 'add', i, j, q])

    for k in range(min(m, n)):
        choices = [(abs(A[i][j]), i, j) for i in range(k, m)
                   for j in range(k, n) if A[i][j]]
        if not choices:
            break
        _, i, j = min(choices)
        swap('r', k, i)
        swap('c', k, j)
        while True:
            while True:
                changed = False
                for i in range(k+1, m):
                    if A[i][k]:
                        add('r', i, k, -(A[i][k] // A[k][k]))
                        if A[i][k]:
                            swap('r', i, k)
                        changed = True
                        break
                if changed:
                    continue
                for j in range(k+1, n):
                    if A[k][j]:
                        add('c', j, k, -(A[k][j] // A[k][k]))
                        if A[k][j]:
                            swap('c', j, k)
                        changed = True
                        break
                if not changed:
                    break
            bad = next(((i, j) for i in range(k+1, m) for j in range(k+1, n)
                        if A[i][j] % A[k][k]), None)
            if bad is None:
                break
            add('r', k, bad[0], 1)
        if A[k][k] < 0:
            A[k] = [-x for x in A[k]]
            operations.append(['r', 'neg', k])
    return A, operations


def replay_operations(matrix: list[list[int]], operations: list[list],
                      inverse: bool = False) -> list[list[int]]:
    """Independent elementary-operation interpreter; not a Smith algorithm."""
    A = deepcopy(matrix)
    for operation in (reversed(operations) if inverse else operations):
        axis, kind, i, *tail = operation
        require(axis in ('r', 'c'), 'Invalid axis')
        # Work by transposition for column operations, unlike the producer.
        if axis == 'c':
            A = [list(row) for row in zip(*A)]
        if kind == 'swap':
            j = tail[0]
            A[i], A[j] = A[j], A[i]
        elif kind == 'neg':
            A[i] = [-x for x in A[i]]
        elif kind == 'add':
            j, q = tail
            require(i != j, 'Non-unimodular self addition')
            if inverse:
                q = -q
            for column in range(len(A[0])):
                A[i][column] += q*A[j][column]
        else:
            raise ValueError('Invalid operation')
        if axis == 'c':
            A = [list(row) for row in zip(*A)]
    return A


def algebra_checks() -> dict:
    X, Y, one, zero = (0, 1, 0), (-1, -1, 1), (1, 0, 0), (0, 0, 0)
    sigma = ring_add(one, ring_add(X, Y))
    require(sigma == (0, 0, 1), 'Stone class lost')
    require(ring_scale(3, sigma) == zero and sigma != zero, 'Stone order')
    require(ring_mul(sigma, sigma) == zero, 'Square-zero relation')
    require(ring_mul(X, sigma) == sigma and ring_mul(Y, sigma) == sigma,
            'Translation action on the stone class')
    require(ring_power(X, 3) == one and ring_power(Y, 3) == one, 'Explicit units')
    for Z in (X, Y, ring_mul(X, ring_power(Y, 2))):
        require(ring_add(one, ring_add(Z, ring_mul(Z, Z))) == zero,
                'Original bone generator relation')
    for i in range(-20, 21):
        for j in range(-20, 21):
            direct = ring_mul(ring_power(X, i % 3), ring_power(Y, j % 3))
            require(direct == cell_class((i, j)), 'Original monomial map')
            require(jet_reduction(direct) == (1, i % 3, j % 3), 'Jet square')
    # Arbitrary signed coefficient tests retain the integer Eisenstein part.
    signed_tests = 0
    for i in range(-5, 6):
        for j in range(-5, 6):
            poly = Counter({(i, j): 7, (i+1, j): -4, (i, j-2): -5})
            require(jet_reduction(observed(poly)) == prior.jet(poly), 'Signed reduction')
            signed_tests += 1
    A = periodic_matrix()
    diagonal, operations = smith_certificate(A)
    require(replay_operations(A, operations) == diagonal, 'Smith forward certificate')
    require(replay_operations(diagonal, operations, inverse=True) == A,
            'Smith inverse certificate')
    expected = [1, 1, 1, 1, 1, 1, 3, 0, 0]
    require([diagonal[i][i] for i in range(9)] == expected, 'Integral torsion changed')
    require(all(v == (expected[i] if i == j else 0)
                for i, row in enumerate(diagonal) for j, v in enumerate(row)),
            'Off-diagonal coefficient survived')
    return {'periodic_boundary_matrix': A, 'smith_diagonal': expected,
            'unimodular_operations': operations, 'integer_inverse_replayed': True,
            'laurent_monomials_checked': 41**2, 'signed_polynomials_checked': signed_tests,
            'abelian_group': 'Z^2 direct_sum Z/3',
            'ring': 'Z[omega]/(omega^2+omega+1) semidirect_square_zero F_3*sigma',
            'scope': 'Finite algebra replay accompanies the explicit all-element inverse maps in TURN2.md.'}


def fourth_checks() -> list[dict]:
    source = ROOT/'evidence/turn2/fourth-witnesses.json'
    rows = json.loads(source.read_text())
    require([row['d'] for row in rows] == list(range(4, 11)), 'Fourth witness scope drift')
    receipts = []
    for row in rows:
        d = row['d']
        moved = prior.translate(third_tiling(d), tuple(row['shift']))
        stone = prior.stone(tuple(row['right_stone_anchor']))
        old = tuple(prior.bone(k, tuple(p)) for k, p in row['released_old_bones'])
        new = tuple(prior.bone(k, tuple(p)) for k, p in row['replacement_bones'])
        require(len(old) == 8 and len(set(old)) == 8, 'Eight distinct released bones')
        released = (stone,)+old
        require(all(moved.count(t) == 1 for t in released), 'Fourth source mismatch')
        result = tuple(t for t in moved if t not in released)+new
        target = prior.region(d+12, 2*d+12)
        prior.verify_tiles(result, target)
        require(sum(k == 'R' for k, _ in result) == d*(d-1)//2-4, 'Fourth stone count')
        inner = {prior.add(p, tuple(row['shift'])) for p in prior.region(d+9, 2*d+9)}
        patch = (target-inner)|set(stone[1])
        p = tuple(row['right_stone_anchor'])
        require(not any(set(t[1]) <= patch for t in bones_through(p)), 'Fourth zero-release obstruction')
        receipts.append({'d': d, 'a': d+12, 'b': 2*d+12, 'h': 4,
                         'released_old_bones': len(old), 'replacement_bones': len(new),
                         'cells': len(target), 'full_tiles': len(result),
                         'tiling_sha256': digest(result), 'zero_release_obstruction_cell': p,
                         'status': 'EXACT_FINITE_WITNESS; NOT_A_UNIFORM_FOURTH_COLLAR_PROOF'})
    return receipts


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def run(max_d: int, output: Path) -> dict:
    require(max_d >= 3, 'Need d>=3')
    started = time.monotonic()
    rows = []
    examples = []
    for d in range(3, max_d+1):
        inner_original = prior.region(d+6, 2*d+6)
        outer = prior.region(d+9, 2*d+9)
        require(inner_original == prior.region_rows(d+6, 2*d+6), 'Inner coordinate definitions')
        require(outer == prior.region_rows(d+9, 2*d+9), 'Outer coordinate definitions')
        require(len(outer) == prior.area(d, 3), 'Area identity')
        source = prior.second_tiling(d)
        prior.verify_tiles(source, inner_original)
        inner = {prior.add(p, (1, -2)) for p in inner_original}
        require(inner <= outer, 'Original containing translation')
        S, U, V = released_tiles(d)
        P0 = (outer-inner)|set(S[1])
        P2 = P0|set(U[1])|set(V[1])
        beta = third_bones(d)
        prior.verify_tiles(beta, P2)
        require(len(beta) == 3*d+17, 'Third replacement count')
        result = third_tiling(d)
        prior.verify_tiles(result, outer)
        R = sum(k == 'R' for k, _ in result)
        require(R == d*(d-1)//2-3 and len(result)-R == 9*d+27, 'Original tile counts')
        reverse = reflected(result)
        prior.verify_tiles(reverse, prior.region_rows(2*d+9, d+9))
        require(Counter(reflected(reverse)) == Counter(result), 'Reflection inverse')
        r0 = Counter({p: 1 for p in P0})
        require(signed_boundary(beta, (U, V)) == r0, 'Exact signed preimage for inclusion kernel')
        p = (d-2, 0)
        forbidden = []
        for tile in bones_through(p):
            require(set(tile[1]) <= inner, 'Nine candidate bones are within the inner source')
            missing = sorted(set(tile[1])-P0)
            require(bool(missing), 'Nonzero-source evaluation no longer kills every bone')
            forbidden.append({'kind': tile[0], 'cells': tile[1], 'outside_P0': missing})
        require(r0[p] == 1, 'Primitive source class')
        require(observed(r0) == (0, 0, 0), 'Support class has nonzero global observation')
        raw_collar = Counter({q: 1 for q in outer-inner})
        require(observed(raw_collar) == (0, 0, 2), 'Original collar class')
        require(observed(Counter({q: 1 for q in outer})) == (0, 0, R % 3), 'Whole region class')
        for kind, cells in result:
            expected = (0, 0, 1) if kind == 'R' else (0, 0, 0)
            require(observed(Counter(cells)) == expected, 'Integral tile observation')
        rows.append({'d': d, 'h': 3, 'a': d+9, 'b': 2*d+9, 'cells': len(outer),
                     'right_stones': R, 'bones': len(result)-R,
                     'released_old_bones': 2, 'replacement_bones': len(beta),
                     'nonzero_source_class_witness_cell': p,
                     'tiling_sha256': digest(result), 'reflected_tiling_sha256': digest(reverse)})
        if d in (3, 4, 5, 10):
            examples.append({'d': d, 'complete_tiling': result, 'positive_patch': beta,
                             'released_source_tiles': (S, U, V), 'obstruction_candidates': forbidden})
    algebra = algebra_checks()
    fourth = fourth_checks()
    receipt = {'record_date': '2026-09-15', 'sprint_turn': 2, 'status': 'PASS',
               'python_optimized': not __debug__, 'd_min': 3, 'd_max': max_d,
               'third_collar_parameter_values': len(rows),
               'third_collar_full_tilings_including_reflections': 2*len(rows),
               'second_collar_sources_rechecked': len(rows),
               'positive_third_patch_identities': len(rows),
               'signed_inclusion_kernel_identities': len(rows),
               'infinite_order_source_witnesses_replayed': len(rows),
               'candidate_bones_at_obstruction_checked': 9*len(rows),
               'third_target_tile_placements_including_reflections': 2*sum(r['cells']//3 for r in rows),
               'fourth_finite_parameter_values': len(fourth),
               'fourth_finite_witness_tile_placements': sum(r['full_tiles'] for r in fourth),
               'smith_diagonal': algebra['smith_diagonal'],
               'smith_unimodular_operations': len(algebra['unimodular_operations']),
               'laurent_monomials_checked': algebra['laurent_monomials_checked'],
               'signed_polynomials_checked': algebra['signed_polynomials_checked'],
               'rows': rows, 'fourth_finite_receipts': fourth,
               'seconds': round(time.monotonic()-started, 3),
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'turn1_script_sha256': hashlib.sha256((ROOT/'check.py').read_bytes()).hexdigest(),
               'fourth_input_sha256': hashlib.sha256((ROOT/'evidence/turn2/fourth-witnesses.json').read_bytes()).hexdigest(),
               'scope': 'Written all-d third-collar and ring proofs with finite replay; fourth collar only the seven supplied cases. No full P7 resolution or Lean build.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2)+'\n')
    (output.parent/'algebra-certificate.json').write_text(json.dumps(algebra, indent=2)+'\n')
    (output.parent/'third-examples.json').write_text(json.dumps(examples, indent=2)+'\n')
    summary = {k: v for k, v in receipt.items() if k not in ('rows', 'fourth_finite_receipts')}
    print(json.dumps(summary, indent=2))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-d', type=int, default=100)
    parser.add_argument('--output', type=Path, default=ROOT/'evidence/turn2/normal.json')
    args = parser.parse_args()
    run(args.max_d, args.output)


if __name__ == '__main__':
    main()
