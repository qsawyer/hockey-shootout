# Hockey Shootout

A quick terminal hockey shootout against the computer, for people who want a short game
without much commitment.

## What it does

- You and the computer each take 5 shots, alternating, you first.
- On your shot you pick a spot: one of the four corners, the five hole, or under the
  left or right arm.
- The goalie covers two thirds of the net, either horizontally (top / middle / bottom)
  or vertically (left / center / right). If your shot is in a covered third it's a
  save, otherwise it's a goal.
- When the computer shoots, you play goalie and choose which two thirds to cover.
- If it's tied after 5 rounds, it goes to sudden death, one shot each per round, until
  a round ends with someone ahead.
- The round and score are shown before and after every shot, then the winner, then
  you're asked whether to play again.

The full rules, including which thirds each shot spot is in, are in [spec.md](spec.md).

## Requirements

Python 3 (standard library only). `pytest` is needed only to run the tests.

## How to run

```
python shootout.py
```

Type the number of your choice (or the spot's name, e.g. `five hole`) at each prompt.

## How to run the tests

```
python -m pip install pytest   # once
python -m pytest
```
