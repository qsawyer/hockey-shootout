# Hockey Shootout — Specification

A quick terminal hockey shootout: you against the computer. You shoot on the computer's
goalie, and you play goalie against the computer's shots. Run it with `python shootout.py`.

## The net

The net is modeled as a 3 x 3 grid. Horizontal thirds are **top**, **middle**, **bottom**;
vertical thirds are **left**, **center**, **right**. Left and right are from the
shooter's point of view.

```
              left        center       right
           +-----------+-----------+-----------+
  top      | top-left  |           | top-right |
           | corner    |           | corner    |
           +-----------+-----------+-----------+
  middle   | under the |  (goalie  | under the |
           | left arm  |   body)   | right arm |
           +-----------+-----------+-----------+
  bottom   | bottom-   |  five     | bottom-   |
           | left      |  hole     | right     |
           | corner    |           | corner    |
           +-----------+-----------+-----------+
```

Each shot spot sits in exactly one horizontal third and exactly one vertical third:

| # | Shot spot            | Horizontal third | Vertical third |
|---|----------------------|------------------|----------------|
| 1 | Top-left corner      | top              | left           |
| 2 | Top-right corner     | top              | right          |
| 3 | Bottom-left corner   | bottom           | left           |
| 4 | Bottom-right corner  | bottom           | right          |
| 5 | Five hole            | bottom           | center         |
| 6 | Under the left arm   | middle           | left           |
| 7 | Under the right arm  | middle           | right          |

The middle-center cell is the goalie's body; nobody can shoot there.

## Requirements

### R1 — Player chooses where to shoot
On each of the player's shots the game shows the seven spots above as a numbered menu
and the player types a number (1–7) or the spot's short name (e.g. `five hole`).
Invalid input is rejected and the prompt repeats.

When the computer shoots, it picks one of the same seven spots uniformly at random.

### R2 — Goalie covers two thirds, horizontally or vertically
A goalie coverage is an orientation (**horizontal** or **vertical**) plus the two thirds
covered in that orientation. Covering two of three thirds is the same as leaving exactly
one third open, so there are six possible coverages:

| # | Coverage                          | Open third   |
|---|-----------------------------------|--------------|
| 1 | Horizontal: top + middle          | bottom       |
| 2 | Horizontal: top + bottom          | middle       |
| 3 | Horizontal: middle + bottom       | top          |
| 4 | Vertical: left + center           | right        |
| 5 | Vertical: left + right            | center       |
| 6 | Vertical: center + right          | left         |

**Who picks the coverage:**
- On the **player's** shots, the computer goalie picks one of the six coverages uniformly
  at random. The random choice is made through an injectable random source so tests can
  control it.
- On the **computer's** shots, the **player** is the goalie and picks the coverage from
  the menu above (number 1–6). The player chooses coverage *before* seeing the shot, and
  the computer chooses its shot without seeing the coverage.

### R3 — Save or goal
A shot is a **save** if the spot lies in one of the two covered thirds in the goalie's
chosen orientation; otherwise it is a **goal**. Concretely: with a horizontal coverage,
look at the spot's horizontal third; with a vertical coverage, look at the spot's
vertical third. Example: horizontal top + middle stops corners on top and both
under-arm shots but lets in the five hole and both bottom corners.

Against a uniformly random goalie every spot scores with probability 1/3, so no spot
is strictly better than another.

### R4 — Five shots each
Regulation is five rounds. In each round the player shoots first, then the computer.
All five rounds are always played, even if one side can no longer catch up (the
requirement says each side *gets* five shots).

### R5 — Sudden death
If the score is tied after five rounds, the game goes to sudden death: rounds 6, 7, ...
each consist of one player shot followed by one computer shot. After a sudden-death
round is complete, if the scores differ the leader wins; if still tied another round is
played. The game never ends in the middle of a round, so both sides always have taken
the same number of shots.

### R6 — Score and round before and after every shot
Immediately before and immediately after every shot the game prints a status line, e.g.

```
Round 3 of 5 | You 1 - 2 Computer
```

In sudden death the round is labeled `Round 6 (sudden death)`.

### R7 — Goal or save
After every shot the game prints `GOAL!` or `SAVE!` together with where the shot went
and what the goalie covered.

### R8 — Winner
When the game ends it prints the final score and `You win!` or `Computer wins!`.

### R9 — Play again
After the winner is shown the game asks `Play again? (y/n)`. `y`/`yes` starts a new game
from 0–0 in round 1; `n`/`no` exits. Other answers repeat the question. End of input
(Ctrl-D / Ctrl-Z) or Ctrl-C quits cleanly.

## Testability
- Game rules (shot result, scoring, round/shooter tracking, sudden death, game over,
  winner) are pure functions in `shootout.py` with no input or printing.
- The game loop takes `input_fn`, `output_fn` and `rng` parameters; tests pass scripted
  input, capture output and use a scripted random source.
