"""Tests for the game loop's input and output. Each test names the requirement it checks."""

import shootout as s
from shootout import PLAYER, COMPUTER, Score


class ScriptedRandom:
    """choice() returns the item at the next scripted index."""

    def __init__(self, indexes):
        self.indexes = list(indexes)

    def choice(self, seq):
        return seq[self.indexes.pop(0)]


class ScriptedInput:
    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.answers:
            raise EOFError
        return self.answers.pop(0)


# Indexes into SHOT_SPOTS / COVERAGES (order is fixed in shootout.py and spec.md).
TOP_LEFT = 0
FIVE_HOLE = 4
H_TOP_MIDDLE = 0       # leaves bottom open: five hole scores, top-left is saved
H_TOP_BOTTOM = 1       # leaves middle open: five hole is saved


def run_game(player_answers, rng_indexes):
    out = []
    inp = ScriptedInput(player_answers)
    result = s.play_game(inp, out.append, ScriptedRandom(rng_indexes))
    return result, out, inp


def regulation(player_scores, computer_scores):
    """Build inputs and rng for 5 rounds where each side scores in the listed rounds."""
    answers, rng = [], []
    for r in range(1, 6):
        answers.append("5")                                 # player shoots five hole
        rng.append(H_TOP_MIDDLE if r in player_scores else H_TOP_BOTTOM)
        answers.append("1")                                 # player covers top+middle
        rng.append(FIVE_HOLE if r in computer_scores else TOP_LEFT)
    return answers, rng


# Sanity check of the helper's assumptions, so a later failure is not misread.
def test_R3_helper_assumptions_hold():
    five_hole, top_left = s.SHOT_SPOTS[FIVE_HOLE], s.SHOT_SPOTS[TOP_LEFT]
    assert s.shot_result(five_hole, s.COVERAGES[H_TOP_MIDDLE]) == s.GOAL
    assert s.shot_result(five_hole, s.COVERAGES[H_TOP_BOTTOM]) == s.SAVE
    assert s.shot_result(top_left, s.COVERAGES[H_TOP_MIDDLE]) == s.SAVE


# ---- R1 / R2: menus -------------------------------------------------------

def test_R1_player_can_pick_spot_by_number_or_name_and_bad_input_reprompts():
    out = []
    inp = ScriptedInput(["9", "slapshot", "Five Hole"])
    labels = [sp.name for sp in s.SHOT_SPOTS]
    assert s.ask_choice("Where?", labels, inp, out.append) == FIVE_HOLE
    assert len(inp.prompts) == 3
    assert out.count("Please enter a number from 1 to 7.") == 2


def test_R2_player_picks_coverage_when_computer_shoots():
    # Score after the player's first shot, so the computer shoots next.
    score = s.record_shot(Score(), PLAYER, s.SAVE)
    out = []
    new = s.play_shot(score, ScriptedInput(["3"]), out.append, ScriptedRandom([FIVE_HOLE]))
    # Coverage 3 is horizontal middle+bottom: the five hole is saved.
    assert "You cover horizontal: middle + bottom." in out[-3]
    assert new.computer_goals == 0 and new.computer_shots == 1


# ---- R6 / R7: per-shot output ---------------------------------------------

def test_R6_R7_status_before_and_after_shot_and_goal_shown():
    out = []
    s.play_shot(Score(), ScriptedInput(["5"]), out.append, ScriptedRandom([H_TOP_MIDDLE]))
    status_lines = [line for line in out if line.startswith("Round ")]
    assert status_lines == [
        "Round 1 of 5 | You 0 - 0 Computer",
        "Round 1 of 5 | You 1 - 0 Computer",
    ]
    assert "GOAL!" in out and "SAVE!" not in out
    assert out.index("Round 1 of 5 | You 0 - 0 Computer") < out.index("GOAL!") \
        < out.index("Round 1 of 5 | You 1 - 0 Computer")


def test_R7_save_shown_when_goalie_covers_the_spot():
    out = []
    s.play_shot(Score(), ScriptedInput(["1"]), out.append, ScriptedRandom([H_TOP_MIDDLE]))
    assert "SAVE!" in out and "GOAL!" not in out


def test_R6_every_shot_has_status_before_and_after():
    answers, rng = regulation(player_scores={1}, computer_scores=set())
    _, out, _ = run_game(answers, rng)
    status_lines = [line for line in out if line.startswith("Round ")]
    assert len(status_lines) == 20                     # 10 shots x (before + after)
    assert status_lines[-1] == "Round 5 of 5 | You 1 - 0 Computer"


def test_R6_sudden_death_round_is_labeled():
    assert s.format_status(Score(3, 3, 5, 5), 6) == "Round 6 (sudden death) | You 3 - 3 Computer"


# ---- R4 / R5 / R8: full games ---------------------------------------------

def test_R4_R8_player_wins_after_five_rounds():
    answers, rng = regulation(player_scores={1, 2}, computer_scores={3})
    result, out, _ = run_game(answers, rng)
    assert result == PLAYER
    assert out[-2:] == ["Final score: You 2 - 1 Computer", "You win!"]
    assert not any("SUDDEN DEATH" in line for line in out)


def test_R5_R8_tied_game_goes_to_sudden_death_and_computer_wins():
    answers, rng = regulation(player_scores={1}, computer_scores={2})
    # Round 6: both score (still tied). Round 7: player saved, computer scores.
    answers += ["5", "1", "5", "1"]
    rng += [H_TOP_MIDDLE, FIVE_HOLE, H_TOP_BOTTOM, FIVE_HOLE]
    result, out, _ = run_game(answers, rng)
    assert result == COMPUTER
    assert sum("SUDDEN DEATH" in line for line in out) == 1
    assert "Round 7 (sudden death) | You 2 - 3 Computer" in out
    assert out[-2:] == ["Final score: You 2 - 3 Computer", "Computer wins!"]


# ---- R9: play again -------------------------------------------------------

def test_R9_play_again_accepts_yes_and_no_and_reprompts_otherwise():
    out = []
    assert s.ask_play_again(ScriptedInput(["maybe", "Y"]), out.append) is True
    assert out == ["Please answer y or n."]
    assert s.ask_play_again(ScriptedInput(["yes"]), [].append) is True
    assert s.ask_play_again(ScriptedInput(["no"]), [].append) is False
    assert s.ask_play_again(ScriptedInput(["N"]), [].append) is False


def test_R9_main_plays_again_from_zero_then_quits():
    game1, rng1 = regulation(player_scores={1}, computer_scores=set())
    game2, rng2 = regulation(player_scores=set(), computer_scores={1})
    out = []
    inp = ScriptedInput(game1 + ["y"] + game2 + ["n"])
    s.main(inp, out.append, ScriptedRandom(rng1 + rng2))
    # Game 1 ends 1-0; the first status line of game 2 is back at round 1, 0-0.
    first_status_of_game2 = next(line for line in out[out.index("You win!"):]
                                 if line.startswith("Round "))
    assert first_status_of_game2 == "Round 1 of 5 | You 0 - 0 Computer"
    assert out.count("You win!") == 1 and out.count("Computer wins!") == 1
    assert sum(p.startswith("Play again?") for p in inp.prompts) == 2
    assert out[-1] == "Thanks for playing!"


def test_R9_end_of_input_quits_cleanly():
    out = []
    s.main(ScriptedInput([]), out.append, ScriptedRandom([]))
    assert out[-1] == "Thanks for playing!"
