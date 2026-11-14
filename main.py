"""Run the match tests for the Rock, Paper, Scissors challenge."""
from RPS_game import play, mrugesh, abbey, kris, quincy
from RPS import player
from test_module import UnitTests


def main():
    for bot in (quincy, abbey, kris, mrugesh):
        print(f"--- player vs {bot.__name__} ---")
        play(player, bot, 1000)
        print()


if __name__ == "__main__":
    main()
    # Uncomment the next two lines to run the unit tests automatically.
    import unittest
    unittest.main(argv=[""], exit=False)
