# Odd-sum calibration proof

## Statement

For every integer `n >= 0`, the sum of the first `n` positive odd integers is `n^2`.

## Proof

For `n >= 0`,

```text
sum(k = 1..n, 2k - 1)
  = 2 * sum(k = 1..n, k) - n
  = 2 * n(n + 1)/2 - n
  = n^2.
```

For `n = 0`, both the empty sum and `0^2` are zero. This also covers the boundary convention explicitly.

## Scope

This is a deliberately elementary calibration artifact. It makes no novelty claim and says nothing about any open problem.
