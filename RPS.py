"""freeCodeCamp: Rock, Paper, Scissors.

`player(prev_play)` receives the opponent's previous move ("" on the first
game of a match) and returns my next move: "R", "P" or "S".

Strategy
--------
Picking randomly only wins ~50 % of the time, so this player tries to guess
what the opponent is about to play and then plays the move that beats it.
Several guessers ("predictors") run in parallel:

* Statistical predictors: they learn, from the opponent's history, which move
  tends to follow a given situation (the opponent's last 1-4 moves, my last
  moves, or a mix of both).
* Rule-based predictors: because the moves of some bots are a deterministic
  function of my own moves, the player simulates those bots directly
  (abbey's order-1 counter table, kris's "beat the last move" rule and
  quincy's fixed five-move cycle).

Every predictor is scored on how often it has been right lately (with a decay
so recent form matters most).  The player then plays the counter of the
currently most reliable predictor.
"""

import random
from collections import Counter, defaultdict

MOVES = ("R", "P", "S")
# BEATS[x] is the move that defeats x.
BEATS = {"R": "P", "P": "S", "S": "R"}

DECAY = 0.9            # how much older rounds count when scoring predictors
MIN_OBSERVATIONS = 3   # a predictor needs this much history to be trusted
PRIOR = 1.0            # Laplace smoothing: an untested predictor scores 50 %


# ---------------------------------------------------------------------------
# Statistical predictors: each one builds a "key" from the history and learns
# which move the opponent plays after that key.
# ---------------------------------------------------------------------------
def _key_all(o, m):
    return ("all",)


def _key_opp_1(o, m):
    return tuple(o[-1:])


def _key_opp_2(o, m):
    return tuple(o[-2:])


def _key_opp_3(o, m):
    return tuple(o[-3:])


def _key_opp_4(o, m):
    return tuple(o[-4:])


def _key_mine_1(o, m):
    return ("me",) + tuple(m[-1:])


def _key_mine_2(o, m):
    return ("me",) + tuple(m[-2:])


def _key_mix_1(o, m):
    return ("mix",) + tuple(m[-1:]) + tuple(o[-1:])


def _key_mix_2(o, m):
    return ("mix",) + tuple(m[-1:]) + tuple(o[-2:])


# (key builder, how many past opponent moves the key needs)
STAT_KEYS = (
    (_key_opp_2, 2),
    (_key_opp_3, 3),
    (_key_opp_1, 1),
    (_key_opp_4, 4),
    (_key_mix_1, 1),
    (_key_mix_2, 2),
    (_key_mine_1, 1),
    (_key_mine_2, 1),
    (_key_all, 0),
)

N_STAT = len(STAT_KEYS)
IDX_ABBEY = N_STAT
IDX_KRIS = N_STAT + 1
IDX_QUINCY = N_STAT + 2
IDX_MRUGESH = N_STAT + 3
N_MODELS = N_STAT + 4

QUINCY_MOVES = ("R", "R", "P", "P", "S")


class _State:
    """Everything the player remembers during one match."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.opp = []                                  # opponent's moves
        self.mine = []                                 # my moves
        self.models = [defaultdict(Counter) for _ in range(N_STAT)]
        self.good = [0.0] * N_MODELS                   # decayed correct guesses
        self.total = [0.0] * N_MODELS                  # decayed guesses made
        self.last_keys = [None] * N_STAT
        self.last_preds = [None] * N_MODELS
        # Simulated state of the rule-based opponents.
        self.abbey_hist = ["R"]   # abbey appends "R" to its history on game 1
        self.abbey_order = {}
        for a in MOVES:
            for b in MOVES:
                self.abbey_order[a + b] = 0
        self.quincy_calls = 0


STATE = _State()


def _predict_stat(model, key):
    """The move the opponent played most often after `key` (None if unseen)."""
    counts = model.get(key)
    if not counts:
        return None
    best_count = max(counts.values())
    for move in MOVES:            # deterministic tie-break
        if counts.get(move) == best_count:
            return move
    return None


def _predict_abbey():
    """Replay abbey's algorithm: it counters its order-1 guess about me."""
    hist = STATE.abbey_hist
    if not hist:
        return "P"
    last = hist[-1]
    sub = {last + move: STATE.abbey_order.get(last + move, 0) for move in MOVES}
    # abbey uses max(), i.e. the first pair with the highest count.
    best_pair = max(sub, key=sub.get)
    return BEATS[best_pair[-1]]


def _abbey_observe(my_move):
    """Update the abbey simulation after I have played `my_move`."""
    hist = STATE.abbey_hist
    hist.append(my_move)
    if len(hist) >= 2:
        pair = hist[-2] + hist[-1]
        STATE.abbey_order[pair] = STATE.abbey_order.get(pair, 0) + 1


def _predict_kris():
    """kris plays the move that beats my previous move."""
    if not STATE.mine:
        return "R"
    return BEATS[STATE.mine[-1]]


def _predict_quincy():
    """quincy repeats a fixed five-move cycle: R, R, P, P, S."""
    n = STATE.quincy_calls + 1
    return QUINCY_MOVES[n % len(QUINCY_MOVES)]


def _predict_mrugesh():
    """mrugesh counters my most frequent move in my last ten plays.

    When two or more moves share the top count, its tie-break is not worth
    guessing, so this predictor abstains (returns None) in that case.
    """
    hist = [""] + STATE.mine          # mrugesh records "" for the first game
    last_ten = hist[-10:]
    counts = Counter(last_ten)
    if "" in counts:
        return None
    top = max(counts.values())
    leaders = [move for move in MOVES if counts.get(move) == top]
    if len(leaders) != 1:
        return None
    return BEATS[leaders[0]]


def _score(i):
    """Smoothed accuracy of model i (0.5 means "no idea")."""
    return (STATE.good[i] + PRIOR) / (STATE.total[i] + 2 * PRIOR)


def _register_previous_round(prev_play):
    """Score every predictor and teach the statistical models."""
    STATE.opp.append(prev_play)

    for i in range(N_STAT):
        key = STATE.last_keys[i]
        if key is not None:
            STATE.models[i][key][prev_play] += 1

    STATE.quincy_calls += 1

    for i in range(N_MODELS):
        STATE.good[i] *= DECAY
        STATE.total[i] *= DECAY
        if STATE.last_preds[i] is not None:
            STATE.total[i] += 1
            if STATE.last_preds[i] == prev_play:
                STATE.good[i] += 1


def _current_predictions():
    """Ask every predictor what it expects the opponent to play next."""
    o, m = STATE.opp, STATE.mine
    preds = [None] * N_MODELS

    for i, (key_builder, needed) in enumerate(STAT_KEYS):
        key = key_builder(o, m) if len(o) >= needed else None
        STATE.last_keys[i] = key
        if key is not None:
            preds[i] = _predict_stat(STATE.models[i], key)

    preds[IDX_ABBEY] = _predict_abbey()
    preds[IDX_KRIS] = _predict_kris()
    preds[IDX_QUINCY] = _predict_quincy()
    preds[IDX_MRUGESH] = _predict_mrugesh()

    STATE.last_preds = preds
    return preds


def _choose():
    preds = _current_predictions()

    candidates = [
        i for i, p in enumerate(preds)
        if p is not None and STATE.total[i] >= MIN_OBSERVATIONS
    ]
    if candidates:
        # Best accuracy wins; on a tie the earlier (often more specific)
        # predictor keeps the advantage, which keeps the play stable.
        best = max(candidates, key=lambda i: (_score(i), -i))
        return BEATS[preds[best]]

    # Cold start: counter the opponent's most common move once there is data,
    # otherwise stay unpredictable.
    if len(STATE.opp) >= MIN_OBSERVATIONS:
        most = Counter(STATE.opp).most_common(1)[0][0]
        return BEATS[most]
    return random.choice(MOVES)


def player(prev_play, opponent_history=[]):
    """Return my next move, given the opponent's previous move."""
    if prev_play == "":
        # A new match is starting: forget the previous one.
        STATE.reset()
        opponent_history.clear()
        move = random.choice(MOVES)
        STATE.mine.append(move)
        _abbey_observe(move)
        return move

    opponent_history.append(prev_play)
    if len(STATE.opp) + 1 != len(opponent_history):
        # Keep the local history in sync if a previous match left something.
        STATE.opp = list(opponent_history[:-1])

    _register_previous_round(prev_play)

    move = _choose()
    STATE.mine.append(move)
    _abbey_observe(move)
    return move
