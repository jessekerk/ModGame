"""Run example Mod game experiments."""

from modgame import ModController
from random_player import RandomPlayer

if __name__ == "__main__":
    controller = ModController(m=5)
    controller.join(RandomPlayer("Random0"))
    controller.join(RandomPlayer("Random1"))
    results = controller.repeated_games(5, debug=True)
    print("\nResults:", results)
