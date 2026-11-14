# Rock, Paper, Scissors — freeCodeCamp Machine Learning with Python

Solution for the freeCodeCamp "Rock, Paper, Scissors" project. The player in
`RPS.py` must beat four different bots (quincy, abbey, kris, mrugesh) in
1000-game matches, winning at least 60 % of the games in each match.

## Files

| File | Purpose |
| --- | --- |
| `RPS.py` | The `player` function — the solution (all work happens here) |
| `RPS_game.py` | Game engine and the four bots (unchanged) |
| `main.py` | Plays a match against every bot and then runs the unit tests |
| `test_module.py` | Unit tests: each bot must be beaten at least 60 % of the time |

## How the player works

A random player only wins ~50 % of the games, so `player` tries to predict the
opponent's next move and then plays the move that beats it. Several
predictors run in parallel and each one is scored on how accurate it has been
lately (with a decay, so recent form counts most); the counter of the most
reliable predictor is played.

* **Statistical predictors** learn from the history which move the opponent
  plays after a given situation: its last 1–4 moves, my last 1–2 moves, or a
  mix of both (`_key_opp_*`, `_key_mine_*`, `_key_mix_*`, `_key_all`).
* **Rule-based predictors** exploit bots whose moves are a deterministic
  function of my own moves:
  * `abbey` counters its order-1 guess about my next move, so the player
    replays abbey's own algorithm on the history it can see and counters that.
  * `kris` always plays the move that beats my last move.
  * `quincy` repeats the fixed cycle `R, R, P, P, S`.
  * `mrugesh` counters my most frequent move in my last ten plays; the
    prediction is used only when the ten-move tally has a clear winner.

## Running

```bash
python3 main.py          # play a match against each bot + run the tests
python3 -m unittest test_module -v
```

## Results (1000 games per bot)

| Opponent | Win rate |
| --- | --- |
| quincy | ≈ 99.6 % |
| abbey | ≈ 99.6 % |
| kris | ≈ 99.7 % |
| mrugesh | ≈ 89 % |
