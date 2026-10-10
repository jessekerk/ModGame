# Here come the match-ups between players defined using the function repeated_games
from random_player import RandomPlayer #noqa
from modgame import repeated_games, repeated_games_2 #noqa

player1 = RandomPlayer()
player2 = RandomPlayer()

players = [player1, player2]
games_to_play = 5

#repeated_games(games_to_play, players)
repeated_games_2(games_to_play, player1=player1, player2=player2, verbose=True)