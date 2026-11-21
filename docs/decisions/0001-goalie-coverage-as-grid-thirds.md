# 0001 — Model goalie coverage as two of three grid thirds

**Status:** accepted
**Date:** 2026-11-21
**Requirements:** R1, R2, R3

## Decision (Y-statement)

In the context of **deciding whether a shot is a save or a goal (R3)**,
facing **seven shot spots (R1) and a goalie that covers "two thirds of the net,
horizontally or vertically" (R2), with no rule in problem.md for which spots fall in
which third**,
we decided for **placing the net on a 3 x 3 grid, giving every shot spot exactly one
row (top/middle/bottom) and one column (left/center/right), and representing a goalie
choice as an orientation plus the two covered thirds; a shot is saved if its row (for
horizontal) or column (for vertical) is covered**,
and neglected **(a) a hand-written lookup table listing which spots each of the six
coverages stops, and (b) a simpler "goalie guesses one spot" model that ignores
thirds**,
to achieve **a rule that is stated once, easy to explain in the spec, easy to test
exhaustively (7 spots x 6 coverages), and fair — against a random goalie every spot
scores exactly 1/3 of the time**,
accepting that **some placements are judgment calls (the five hole counts as the
bottom-center cell, under-the-arm shots as middle-left/right, and the middle-center
cell is the goalie's body and not a target), and that adding a new spot means choosing
its grid cell rather than freely deciding which coverages stop it**.

## Alternatives considered

- **Lookup table per coverage.** Most flexible (any coverage could stop any set of
  spots), but 42 hand-entered cells with no underlying logic are easy to get
  inconsistent and hard for a player to reason about.
- **Goalie guesses a single spot.** Simple, but contradicts R2, which explicitly
  describes covering thirds.
