"""Run example Mod game experiments."""

from modgame import ModController
from random_player import RandomPlayer
from zero_order_player import ProbabilisticPlayer

if __name__ == "__main__":
    m = 5

    controller = ModController(m=m)
    controller.join(RandomPlayer("Random0"))
    controller.join(ProbabilisticPlayer(m=m))

    results = controller.repeated_games(10000, debug=False)
    print("\nResults:", results)
