__author__ = 'Ales Kocur'

from TicTacToe import *

#game = Game(size=4, starting_player=Player.X, ai_player=Player.O)
game = TicTacToe()
game.draw()

while not game.has_winner():

    print('== {} playing =='.format(game.whose_turn().name))

    if (game.whose_turn() == game.ai_player):
        print("{}'s thinking...".format(game.ai_player.name))
        position = game.next_ai_move()
    else:
        x = int(input('Row index:'))
        y = int(input('Column index:'))
        position = Position(x, y)

    #print('Choosen position: {} {}'.format(position.x, position.y))

    if game.move(position):
        game.draw()
    else:
        print('Unallowed move! Try again...')


if (game.winner() == Player.none):
    print("It's a draw!")
else:
    print('{} won!'.format(game.winner().name))




