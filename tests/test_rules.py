"""Tests for the game rules in shootout.py. Each test names the requirement it checks."""

import pytest

import shootout as s
from shootout import GOAL, SAVE, PLAYER, COMPUTER, Score


class ScriptedRandom:
    """Stand-in for random.Random whose choice() returns items by scripted index."""

    def __init__(self, indexes):
        self.indexes = list(indexes)
        self.seen = []

    def choice(self, seq):
        self.seen.append(tuple(seq))
        return seq[self.indexes.pop(0)]


def spot(name):
    return next(sp for sp in s.SHOT_SPOTS if sp.name == name)


def coverage(orientation, *covered):
    return next(c for c in s.COVERAGES
                if c.orientation == orientation and set(c.covered) == set(covered))


def play(score, results):
    """Apply a sequence of results, alternating shooters as the rules require."""
    for result in results:
        score = s.record_shot(score, s.next_shooter(score), result)
    return score


# ---- R1: shot spots -------------------------------------------------------

def test_R1_seven_shot_spots_are_corners_five_hole_and_under_arms():
    assert sorted(sp.name for sp in s.SHOT_SPOTS) == sorted([
        "top-left corner", "top-right corner", "bottom-left corner",
        "bottom-right corner", "five hole",
        "under the left arm", "under the right arm",
    ])


@pytest.mark.parametrize("name,row,column", [
    ("top-left corner", "top", "left"),
    ("top-right corner", "top", "right"),
    ("bottom-left corner", "bottom", "left"),
    ("bottom-right corner", "bottom", "right"),
    ("five hole", "bottom", "center"),
    ("under the left arm", "middle", "left"),
    ("under the right arm", "middle", "right"),
])
def test_R1_each_spot_is_in_the_thirds_given_in_spec(name, row, column):
    assert (spot(name).row, spot(name).column) == (row, column)


def test_R1_computer_shot_uses_injected_random_source():
    rng = ScriptedRandom([4])
    assert s.computer_shot(rng) == spot("five hole")
    assert rng.seen == [s.SHOT_SPOTS]


# ---- R2: goalie coverages -------------------------------------------------

def test_R2_six_coverages_two_thirds_in_one_orientation():
    expected = {
        ("horizontal", frozenset({"top", "middle"})),
        ("horizontal", frozenset({"top", "bottom"})),
        ("horizontal", frozenset({"middle", "bottom"})),
        ("vertical", frozenset({"left", "center"})),
        ("vertical", frozenset({"left", "right"})),
        ("vertical", frozenset({"center", "right"})),
    }
    actual = {(c.orientation, frozenset(c.covered)) for c in s.COVERAGES}
    assert actual == expected
    assert len(s.COVERAGES) == 6
    assert all(len(c.covered) == 2 for c in s.COVERAGES)


def test_R2_computer_goalie_uses_injected_random_source():
    rng = ScriptedRandom([5])
    assert s.computer_coverage(rng) == s.COVERAGES[5]
    assert rng.seen == [s.COVERAGES]


# ---- R3: save or goal -----------------------------------------------------

# For every coverage, the spots that should be GOALS (everything else is a save).
GOALS_BY_COVERAGE = [
    (("horizontal", "top", "middle"),
     {"bottom-left corner", "bottom-right corner", "five hole"}),
    (("horizontal", "top", "bottom"),
     {"under the left arm", "under the right arm"}),
    (("horizontal", "middle", "bottom"),
     {"top-left corner", "top-right corner"}),
    (("vertical", "left", "center"),
     {"top-right corner", "bottom-right corner", "under the right arm"}),
    (("vertical", "left", "right"),
     {"five hole"}),
    (("vertical", "center", "right"),
     {"top-left corner", "bottom-left corner", "under the left arm"}),
]


@pytest.mark.parametrize("cov,goal_spots", GOALS_BY_COVERAGE)
def test_R3_shot_result_for_every_spot_and_coverage(cov, goal_spots):
    c = coverage(*cov)
    for sp in s.SHOT_SPOTS:
        expected = GOAL if sp.name in goal_spots else SAVE
        assert s.shot_result(sp, c) == expected, (sp.name, c.description)


def test_R3_same_spot_can_be_save_horizontally_and_goal_vertically():
    # Top-right corner: covered by horizontal top+middle, open against vertical left+center.
    sp = spot("top-right corner")
    assert s.shot_result(sp, coverage("horizontal", "top", "middle")) == SAVE
    assert s.shot_result(sp, coverage("vertical", "left", "center")) == GOAL


# ---- R4: five shots each --------------------------------------------------

def test_R4_player_shoots_first_then_shooters_alternate():
    score = Score()
    shooters = []
    for _ in range(10):
        shooter = s.next_shooter(score)
        shooters.append(shooter)
        score = s.record_shot(score, shooter, SAVE)
    assert shooters == [PLAYER, COMPUTER] * 5


def test_R4_goals_are_counted_for_the_shooter_only():
    score = play(Score(), [GOAL, SAVE, GOAL, GOAL])
    assert (score.player_goals, score.computer_goals) == (2, 1)
    assert (score.player_shots, score.computer_shots) == (2, 2)


def test_R4_shooting_out_of_turn_is_rejected():
    with pytest.raises(ValueError):
        s.record_shot(Score(), COMPUTER, GOAL)


def test_R4_game_not_over_before_both_sides_take_five_shots_even_if_decided():
    # Player 3-0 after three rounds: computer cannot catch up, but shots remain.
    score = play(Score(), [GOAL, SAVE] * 3)
    assert not s.is_game_over(score)
    # Player has shot 5 times, computer only 4: still not over.
    score = play(score, [SAVE, SAVE, SAVE])
    assert (score.player_shots, score.computer_shots) == (5, 4)
    assert not s.is_game_over(score)


def test_R4_game_over_after_five_each_when_not_tied():
    score = play(Score(), [GOAL, SAVE] + [SAVE, SAVE] * 4)
    assert (score.player_shots, score.computer_shots) == (5, 5)
    assert s.is_game_over(score)


def test_R4_rounds_count_one_to_five():
    score = Score()
    rounds = []
    for _ in range(10):
        rounds.append(s.current_round(score))
        score = s.record_shot(score, s.next_shooter(score), SAVE)
    assert rounds == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]


# ---- R5: sudden death -----------------------------------------------------

def test_R5_tied_after_five_rounds_goes_to_sudden_death():
    score = play(Score(), [GOAL, GOAL] + [SAVE, SAVE] * 4)
    assert not s.is_game_over(score)
    assert s.current_round(score) == 6
    assert s.is_sudden_death(s.current_round(score))
    assert s.next_shooter(score) == PLAYER


def test_R5_regulation_rounds_are_not_sudden_death():
    assert [s.is_sudden_death(r) for r in range(1, 7)] == [False] * 5 + [True]


def test_R5_sudden_death_waits_for_computer_to_answer():
    score = play(Score(), [SAVE, SAVE] * 5 + [GOAL])
    assert not s.is_game_over(score)
    assert s.next_shooter(score) == COMPUTER


def test_R5_sudden_death_continues_while_tied():
    score = play(Score(), [SAVE, SAVE] * 5 + [GOAL, GOAL, SAVE, SAVE])
    assert not s.is_game_over(score)
    assert s.current_round(score) == 8


def test_R5_sudden_death_ends_when_a_round_is_not_tied():
    score = play(Score(), [SAVE, SAVE] * 5 + [GOAL, GOAL, SAVE, GOAL])
    assert s.is_game_over(score)
    assert s.round_of_last_shot(score) == 7


def test_R5_no_shots_allowed_after_game_over():
    score = play(Score(), [GOAL, SAVE] + [SAVE, SAVE] * 4)
    with pytest.raises(ValueError):
        s.record_shot(score, PLAYER, GOAL)


# ---- R8: winner -----------------------------------------------------------

def test_R8_player_wins_with_more_goals():
    score = play(Score(), [GOAL, SAVE] + [SAVE, SAVE] * 4)
    assert s.winner(score) == PLAYER


def test_R8_computer_wins_with_more_goals():
    score = play(Score(), [SAVE, GOAL] + [SAVE, SAVE] * 4)
    assert s.winner(score) == COMPUTER


def test_R8_computer_wins_in_sudden_death():
    score = play(Score(), [SAVE, SAVE] * 5 + [SAVE, GOAL])
    assert s.winner(score) == COMPUTER


def test_R8_no_winner_while_game_in_progress():
    assert s.winner(play(Score(), [GOAL, SAVE] * 2)) is None
    assert s.winner(play(Score(), [SAVE, SAVE] * 5)) is None
