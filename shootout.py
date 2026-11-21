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
