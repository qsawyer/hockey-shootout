"""Hockey shootout: a quick terminal game against the computer.

Game rules live in the pure functions at the top of this file. Input and
printing live in the game loop at the bottom. See spec.md for the rules.
"""

from dataclasses import dataclass, replace

REGULATION_ROUNDS = 5

PLAYER = "player"
COMPUTER = "computer"

GOAL = "goal"
SAVE = "save"

HORIZONTAL = "horizontal"
VERTICAL = "vertical"

ROWS = ("top", "middle", "bottom")      # horizontal thirds
COLUMNS = ("left", "center", "right")   # vertical thirds


@dataclass(frozen=True)
class ShotSpot:
    name: str
    row: str      # horizontal third the spot is in
    column: str   # vertical third the spot is in


# R1: the seven places a shooter can aim.
SHOT_SPOTS = (
    ShotSpot("top-left corner", "top", "left"),
    ShotSpot("top-right corner", "top", "right"),
    ShotSpot("bottom-left corner", "bottom", "left"),
    ShotSpot("bottom-right corner", "bottom", "right"),
    ShotSpot("five hole", "bottom", "center"),
    ShotSpot("under the left arm", "middle", "left"),
    ShotSpot("under the right arm", "middle", "right"),
)


@dataclass(frozen=True)
class Coverage:
    orientation: str          # HORIZONTAL or VERTICAL
    covered: tuple            # the two thirds the goalie covers

    @property
    def description(self):
        return f"{self.orientation}: {' + '.join(self.covered)}"


def _two_of(thirds):
    return [tuple(t for t in thirds if t != left_open) for left_open in reversed(thirds)]


# R2: covering two of three thirds, horizontally or vertically -> six choices.
COVERAGES = tuple(
    [Coverage(HORIZONTAL, pair) for pair in _two_of(ROWS)]
    + [Coverage(VERTICAL, pair) for pair in _two_of(COLUMNS)]
)


def shot_result(spot, coverage):
    """R3: SAVE if the spot is in a covered third, otherwise GOAL."""
    third = spot.row if coverage.orientation == HORIZONTAL else spot.column
    return SAVE if third in coverage.covered else GOAL


def computer_shot(rng):
    """R1: the computer shooter picks a spot using the injected random source."""
    return rng.choice(SHOT_SPOTS)


def computer_coverage(rng):
    """R2: the computer goalie picks a coverage using the injected random source."""
    return rng.choice(COVERAGES)


@dataclass(frozen=True)
class Score:
    player_goals: int = 0
    computer_goals: int = 0
    player_shots: int = 0
    computer_shots: int = 0


def next_shooter(score):
    """R4/R5: the player shoots first in every round, then the computer."""
    return PLAYER if score.player_shots == score.computer_shots else COMPUTER


def current_round(score):
    """The round the next shot belongs to (1-based)."""
    return score.player_shots + 1 if next_shooter(score) == PLAYER else score.player_shots


def round_of_last_shot(score):
    """The round the most recent shot belonged to (1-based)."""
    return max(score.player_shots, score.computer_shots)


def is_sudden_death(round_number):
    """R5: every round after regulation is sudden death."""
    return round_number > REGULATION_ROUNDS


def record_shot(score, shooter, result):
    """R4: return a new Score with one more shot (and goal, if scored) for shooter."""
    if is_game_over(score):
        raise ValueError("the game is already over")
    if shooter != next_shooter(score):
        raise ValueError(f"it is not {shooter}'s turn to shoot")
    scored = 1 if result == GOAL else 0
    if shooter == PLAYER:
        return replace(score, player_shots=score.player_shots + 1,
                       player_goals=score.player_goals + scored)
    return replace(score, computer_shots=score.computer_shots + 1,
                   computer_goals=score.computer_goals + scored)


def is_game_over(score):
    """R4/R5: over once a full round is done, regulation is finished, and it is not tied."""
    return (score.player_shots == score.computer_shots
            and score.player_shots >= REGULATION_ROUNDS
            and score.player_goals != score.computer_goals)


def winner(score):
    """R8: PLAYER or COMPUTER once the game is over, otherwise None."""
    if not is_game_over(score):
        return None
    return PLAYER if score.player_goals > score.computer_goals else COMPUTER


# ---------------------------------------------------------------------------
# Input and printing. Everything below takes input_fn / output_fn / rng so
# tests can script the player, capture output, and control the computer.
# ---------------------------------------------------------------------------

def format_status(score, round_number):
    """R6: one line with the round and the score."""
    if is_sudden_death(round_number):
        label = f"Round {round_number} (sudden death)"
    else:
        label = f"Round {round_number} of {REGULATION_ROUNDS}"
    return f"{label} | You {score.player_goals} - {score.computer_goals} Computer"


def ask_choice(prompt, labels, input_fn, output_fn):
    """Show a numbered menu and return the chosen index. Accepts a number or a label."""
    output_fn(prompt)
    for number, label in enumerate(labels, start=1):
        output_fn(f"  {number}. {label}")
    while True:
        answer = input_fn(f"Choose 1-{len(labels)}: ").strip().lower()
        if answer.isdigit() and 1 <= int(answer) <= len(labels):
            return int(answer) - 1
        for index, label in enumerate(labels):
            if answer == label.lower():
                return index
        output_fn(f"Please enter a number from 1 to {len(labels)}.")


def play_shot(score, input_fn, output_fn, rng):
    """Play the next shot (player's or computer's) and return the new score."""
    shooter = next_shooter(score)
    round_number = current_round(score)
    output_fn("")
    output_fn(format_status(score, round_number))                       # R6 before

    if shooter == PLAYER:
        index = ask_choice("Your shot. Where do you shoot?",            # R1
                           [sp.name for sp in SHOT_SPOTS], input_fn, output_fn)
        spot = SHOT_SPOTS[index]
        cover = computer_coverage(rng)                                  # R2
        shot_line = f"You shoot {spot.name}. The goalie covers {cover.description}."
    else:
        index = ask_choice("You're in goal. Which two thirds do you cover?",  # R2
                           [c.description for c in COVERAGES], input_fn, output_fn)
        cover = COVERAGES[index]
        spot = computer_shot(rng)                                       # R1
        shot_line = f"Computer shoots {spot.name}. You cover {cover.description}."

    result = shot_result(spot, cover)                                   # R3
    score = record_shot(score, shooter, result)
    output_fn(shot_line)
    output_fn("GOAL!" if result == GOAL else "SAVE!")                   # R7
    output_fn(format_status(score, round_number))                       # R6 after
    return score


def play_game(input_fn, output_fn, rng):
    """Play one full shootout and return the winner (PLAYER or COMPUTER)."""
    score = Score()
    announced_sudden_death = False
    while not is_game_over(score):
        if is_sudden_death(current_round(score)) and not announced_sudden_death:
            output_fn("")
            output_fn("Tied after 5 rounds - SUDDEN DEATH!")             # R5
            announced_sudden_death = True
        score = play_shot(score, input_fn, output_fn, rng)
    result = winner(score)
    output_fn("")
    output_fn(f"Final score: You {score.player_goals} - {score.computer_goals} Computer")
    output_fn("You win!" if result == PLAYER else "Computer wins!")    # R8
    return result


def ask_play_again(input_fn, output_fn):
    """R9: ask until the answer is yes or no."""
    while True:
        answer = input_fn("Play again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        output_fn("Please answer y or n.")


def main(input_fn=input, output_fn=print, rng=None):
    if rng is None:
        import random
        rng = random.Random()
    output_fn("HOCKEY SHOOTOUT - 5 shots each, sudden death if tied.")
    try:
        while True:
            play_game(input_fn, output_fn, rng)
            if not ask_play_again(input_fn, output_fn):              # R9
                break
    except (EOFError, KeyboardInterrupt):
        output_fn("")
    output_fn("Thanks for playing!")


if __name__ == "__main__":
    main()
