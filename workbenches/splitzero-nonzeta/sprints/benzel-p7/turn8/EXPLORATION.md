# Search record and next mathematical calculation

16 September 2026. The result accepted for written-proof replay is the unbounded
q=3k construction in PROOF.md. Exploratory successes or failures below do not
extend its parameter domain.

The first broad-strip trials left corner regions not filled by the tested search.
Releasing nearby original bones exposed a regular corner. Two explicit horizontal
caps followed by original V/D bone blocks produced the table in PROOF §3. The
accepted result is the exact parameter-preserving identity, not a pattern fit or
an optimization status. Two special vertical column starts were corrected during
development: `5-k` and `6-4k`. The shared symbolic table and original-cell replays
both use the corrected values; mutation tests reject altered anchors.

For q=3k+1 and q=3k+2, translating the new q=3k patch as in the older corner
construction yields small unfilled components near different corners. At the
explicit tested case k=3,m=100, the residue-1 corner jet values are (0,1,0),
(0,0,0),(0,2,0); the residue-2 values are (0,2,1),(0,0,1),(0,1,1). The coordinate
map is the literal original jet X->1+e,Y->1+f in characteristic 3 with e^2=ef=f^2=0.
Each original bone has zero image. Thus a corner with its stated nonzero jet
cannot be filled by bones, including signed bones, while the sum over all
corners is zero. The actual original supports of that calculation remain in
the local search history. No unproved all-k corner identification is substituted
for this finite observation.

This led to the intercorner band homotopies printed in PROOF §8 and implemented
in `transports.py`. They have exact endpoints, original generator paths and
reverse signed maps. Finite tests of the proposed channels pass at their listed
parameters and local searches find positive endpoint repairs. Those are not yet
an all-parameter positive endpoint formula for either remaining residue.

In particular, several local and global optimization calls returned time limits
or infeasibility statuses; no such status is used as a mathematical nonexistence
result. The proved rotation obstruction is different and explicit: a
rho-invariant tiling has right-stone count 0 or 1 modulo 3, since only R(0,0) is
fixed. The inclusion of fixed tilings into all original tilings is retained;
asymmetric tilings are not excluded.

The continuation should start from the original endpoint generators in
`transports.py`, the full source-to-tail map, and a parameter-dependent endpoint
repair in the two remaining classes. It must verify the actual source membership,
positive support partitions, and both cochain/positive-fibre maps. A vanishing
combined jet or an integer signed lift does not supply that missing positive
partition. No conditional theorem is offered as a completed result.
