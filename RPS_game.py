"""Game engine and the four opponent bots (freeCodeCamp starter code).

Do not modify this file: write all of your code in RPS.py.
"""


def play(player1, player2, num_games, verbose=False):
    """Play a match of `num_games` games between two player functions.

    Returns the win rate of player1 as a percentage (0-100).
    """
    p1_prev_play = ""
    p2_prev_play = ""
    results = {"p1": 0, "p2": 0, "tie": 0}

    for _ in range(num_games):
        p1_play = player1(p2_prev_play)
        p2_play = player2(p1_prev_play)

        if p1_play == p2_play:
            results["tie"] += 1
            winner = "Tie."
        elif (
            (p1_play == "P" and p2_play == "R")
            or (p1_play == "R" and p2_play == "S")
            or (p1_play == "S" and p2_play == "P")
        ):
            results["p1"] += 1
            winner = "Player 1 wins."
        else:
            results["p2"] += 1
            winner = "Player 2 wins."

        if verbose:
            print("Player 1:", p1_play, "| Player 2:", p2_play)
            print(winner)

        p1_prev_play = p1_play
        p2_prev_play = p2_play

    games_won = results["p1"] / num_games
    ties = results["tie"] / num_games
    losses = results["p2"] / num_games

    p1 = player1.__name__
    p2 = player2.__name__

    print(f"{p1} wins {results['p1']} of {num_games} games ({games_won * 100:.1f}%)")
    print(f"{p2} wins {results['p2']} of {num_games} games ({losses * 100:.1f}%)")
    print(f"Ties: {results['tie']} of {num_games} games ({ties * 100:.1f}%)")
    print()

    return games_won * 100


def quincy(prev_play, counter=[0]):
    """Always plays the same five-move sequence: R, R, P, P, S."""
    counter[0] += 1
    choices = ["R", "R", "P", "P", "S"]
    return choices[counter[0] % len(choices)]


def kris(prev_play):
    """Plays the move that beats the opponent's previous move."""
    if prev_play == "":
        return "R"
    elif prev_play == "R":
        return "P"
    elif prev_play == "P":
        return "S"
    elif prev_play == "S":
        return "R"


def mrugesh(prev_play, opponent_history=[]):
    """Counters the opponent's most frequent move in the last ten plays."""
    opponent_history.append(prev_play)

    last_ten = opponent_history[-10:]
    most_frequent = max(set(last_ten), key=last_ten.count)

    if most_frequent == "":
        most_frequent = "P"

    ideal_response = {"P": "S", "R": "P", "S": "R"}
    return ideal_response[most_frequent]


def abbey(prev_play, opponent_history=[], play_order=[{
    "RR": 0, "RP": 0, "RS": 0,
    "PR": 0, "PP": 0, "PS": 0,
    "SR": 0, "SP": 0, "SS": 0,
}]):
    """Predicts the next move from the last two plays, then counters it."""
    if not prev_play:
        prev_play = "R"
    opponent_history.append(prev_play)

    last_two = "".join(opponent_history[-2:])
    if len(last_two) == 2:
        play_order[0][last_two] += 1

    potential_plays = [
        prev_play + "R",
        prev_play + "P",
        prev_play + "S",
    ]

    sub_order = {k: play_order[0][k] for k in potential_plays if k in play_order[0]}

    prediction = max(sub_order, key=sub_order.get)[-1:]

    ideal_response = {"P": "S", "R": "P", "S": "R"}
    return ideal_response[prediction]
