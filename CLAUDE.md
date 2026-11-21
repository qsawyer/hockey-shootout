# CLAUDE.md

Standing rules for working in this repository.

## Stack
- Python 3, standard library only. The only third-party package allowed is `pytest` (for tests).
- Do not add other dependencies.

## Running
- Play the game: `python shootout.py`
- Run the tests: `python -m pytest`

## Code layout
- `shootout.py` holds the game. Game rules (shot results, scoring, sudden death, winner)
  live in pure functions separate from input/printing so they can be tested.
- Randomness (the computer's choices) is injected, never called directly from the rules,
  so tests can control it.
- `spec.md` explains how the game meets each requirement in `problem.md`.
- `docs/decisions/` holds decision records as Y-statements.

## Tests
- Tests live in `tests/` and use pytest.
- Every test names the requirement ID it checks (R1...R9) in its name or docstring.
- Every test must be able to fail: it must check a concrete outcome that would be wrong
  if the code under test were wrong.
- All tests must pass before committing.

## Git
- Never undo or amend a commit (no `git commit --amend`, `git reset`, `git revert` of
  pushed history, or force pushes). Fix mistakes with a new commit.
- Make small commits. Each message says what changed and why.
- Do not push unless asked.
