__author__ = 'Ales Kocur'

import copy, itertools, random, sys
from enum import Enum, IntEnum



COLUMN_SEPARATOR = '|'

class Player(IntEnum):
    none = 0
    X = 1
    O = 2

class DirectionHorizontal(Enum):
    left = 0
    center = 1
    right = 2

class DirectionVertical(Enum):
    top = 0
    middle = 1
    bottom = 2

class Direction:
    vertical = DirectionVertical.top
    horizontal = DirectionHorizontal.left



    def __init__(self, vertical, horizontal):
        self.vertical = vertical
        self.horizontal = horizontal

OPPOSITE_DIRECTIONS = [[Direction(DirectionVertical.top, DirectionHorizontal.left),
                               Direction(DirectionVertical.bottom, DirectionHorizontal.right)],
                               [Direction(DirectionVertical.top, DirectionHorizontal.center),
                               Direction(DirectionVertical.bottom, DirectionHorizontal.center)],
                               [Direction(DirectionVertical.top, DirectionHorizontal.right),
                               Direction(DirectionVertical.bottom, DirectionHorizontal.left)],
                               [Direction(DirectionVertical.middle, DirectionHorizontal.left),
                               Direction(DirectionVertical.middle, DirectionHorizontal.right)]]

class Position:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_outside_bounds(self, x_min, y_min, x_max, y_max):
        return self.x < x_min or self.y < y_min or self.x > x_max or self.y > y_max

class TicTacToe:

    def __init__(self, size=3, starting_player=Player.X, ai_player=Player.O):

        if size < 3:
            size = 3

        if size < 5:
            self._required_in_line = 3
        else:
            self._required_in_line = 5

        self.ai_player = ai_player
        self.board = [[Player.none for x in range(size)] for x in range(size)]
        self.starting_player = starting_player
        self._is_end = (False, Player.none)
        self.turn_count = 0
        self.ai_next_move = Position(0, 0)
        self.positioning_board = [[False for x in range(size)] for x in range(size)]

#   PUBLIC METHODS
    def move(self, position):

        if position.is_outside_bounds(0, 0, len(self.board)-1, len(self.board)-1):
            return False

        if self.board[position.x][position.y] != Player.none:
            return False

        self._perform_move(position, self.whose_turn())
        self._is_end_state_for_move(position)
        self.turn_count += 1

        board_size = len(self.board)
        if self.turn_count == board_size * board_size:
            self._is_end = (True, Player.none)

        return True

    # Did already win someone?
    def has_winner(self):
        return self._is_end[0]

    # Get winner
    def winner(self):
        return self._is_end[1]

    # Determine whose turn is it
    def whose_turn(self):
        if self.turn_count % 2 == 0:
            return self.starting_player
        else:
            return Player.O if self.starting_player == Player.X else Player.X

    # Draw game board
    def draw(self):

        self.print_number_line()
        self._print_line()
        for index_r, row in enumerate(self.board):

            print(COLUMN_SEPARATOR, end='')

            for index_c, item in enumerate(row):
                if index_c == 0:
                    if index_r < 10:
                        print("  {} ".format(index_r), end=COLUMN_SEPARATOR)
                    else:
                        print(" {} ".format(index_r), end=COLUMN_SEPARATOR)
                if item == Player.none:
                    print('   ', end=COLUMN_SEPARATOR)
                else:
                    print(' {} '.format(item.name), end=COLUMN_SEPARATOR)
            self._print_line()

    def draw_available_positions(self):

        self.print_number_line()
        self._print_line()
        for index_r, row in enumerate(self.positioning_board):

            print(COLUMN_SEPARATOR, end='')

            for index_c, item in enumerate(row):
                if index_c == 0:
                    if index_r < 10:
                        print("  {} ".format(index_r), end=COLUMN_SEPARATOR)
                    else:
                        print(" {} ".format(index_r), end=COLUMN_SEPARATOR)
                if item == Player.none:
                    print('   ', end=COLUMN_SEPARATOR)
                else:
                    print(' {} '.format("H" if item else " "), end=COLUMN_SEPARATOR)
            self._print_line()

    def print_number_line(self):
        print('    ', COLUMN_SEPARATOR, end='')
        for index in range (0, len(self.board)):
            if index < 10:
                print(' {} '.format(index), end=COLUMN_SEPARATOR)
            else:
                print('{} '.format(index), end=COLUMN_SEPARATOR)


    def next_ai_move(self):

        if self.turn_count == 0:
            middle = int(len(self.board) / 2)
            self.ai_next_move = Position(middle, middle)
        elif self.turn_count == 1:
            self.ai_next_move = self.determine_first_move()
        else:
            self.minimax(0, -sys.maxsize, sys.maxsize)

        return self.ai_next_move

#   PRIVATE METHODS

    def determine_first_move(self):

        available_positions = self.available_positions()
        return random.choice(available_positions)

    # Printing horizontal line
    def _print_line(self):
        print('\n     ' + len(self.board) * '-' * 4)

# Performing move
    def _perform_move(self, move, player):
        if self.board[move.x][move.y] == Player.none:
            self.board[move.x][move.y] = player

        for x in range(move.x-1, move.x+2):
            for y in range(move.y-1, move.y+2):
                if not (Position(x, y).is_outside_bounds(0, 0, len(self.board)-1, len(self.board)-1)):
                    self.positioning_board[x][y] = True

# Determine end state of the game
    def _is_end_state_for_move(self, last_move):
        player = self.board[last_move.x][last_move.y]


        for directions in OPPOSITE_DIRECTIONS:
            count = [[0], [0]]
            ends_with = [[Player.none], [Player.none]]

            for direction_index in range(len(directions)):
                self._states_in_direction(self._new_position_by_direction(last_move, directions[direction_index]),
                                         directions[direction_index], player, count[direction_index], ends_with[direction_index])

            if sum(list(itertools.chain(*count))) + 1 >= self._required_in_line:
                self._is_end = (True, player)

# Calculate rating
    def calculate_rating_for_move(self, move):
        player = self.board[move.x][move.y]
        rating = 0

        for directions in OPPOSITE_DIRECTIONS:
            count = [[0], [0]]
            ends_with = [[Player.none], [Player.none]]
            opponents_count = [[0], [0]]
            opponents_ends_with = [[Player.none], [Player.none]]

            for direction_index in range(len(directions)):
                self._states_in_direction(self._new_position_by_direction(move, directions[direction_index]),
                                         directions[direction_index], player, count[direction_index],
                                         ends_with[direction_index])
                self._states_in_direction(self._new_position_by_direction(move, directions[direction_index]),
                                         directions[direction_index], TicTacToe._opposite_player(player), opponents_count[direction_index],
                                         opponents_ends_with[direction_index])

            count_sum = sum(list(itertools.chain(*count))) + 1 # number of players moves in direction

            if count_sum == 2:
                rating += 1

            if ends_with[0][0] is Player.none and ends_with[1][0] is Player.none: # if there is open on both sides
                if count_sum == 3:
                    rating += 10
                if count_sum >= 4:
                    rating += 10000
            elif ends_with[0][0] is Player.none or ends_with[1][0] is Player.none: # if there is open on one side
                if count_sum == 3:
                    rating += 5
                if count_sum >= 4:
                    rating += 10000

            opponents_count_sum = sum(list(itertools.chain(*opponents_count)))

            if opponents_count_sum >= 3:
                rating += 21000

        return rating

# Get opposite player of argument
    @classmethod
    def _opposite_player(cls, player):
        return Player.X if player == Player.O else Player.O

# Recursive method for counting moves in specific direction
    def _states_in_direction(self, position, direction, player, count, ends_with):

        if position.is_outside_bounds(0, 0, len(self.board)-1, len(self.board)-1):
            ends_with[0] = TicTacToe._opposite_player(player)
            return

        if self.board[position.x][position.y] != player:
            ends_with[0] = self.board[position.x][position.y]
            return
        else:
            count[0] += 1
            next_position = self._new_position_by_direction(position, direction)
            self._states_in_direction(next_position, direction, player, count, ends_with)

# Returns new position object shifted in given direction
    def _new_position_by_direction(self, position, direction):
        new_position = Position(position.x, position.y)

        if direction.vertical == DirectionVertical.top:
            new_position.x -= 1
        elif direction.vertical == DirectionVertical.bottom:
            new_position.x += 1

        if direction.horizontal == DirectionHorizontal.left:
            new_position.y -= 1
        elif direction.horizontal == DirectionHorizontal.right:
            new_position.y += 1

        return new_position


# Minimax algorithm

    def available_positions(self):
        positions = []

        for r_index, rows in enumerate(self.board):
            for i_index, item in enumerate(rows):

                if item is Player.none and self.positioning_board[r_index][i_index] is True:
                    positions.append(Position(r_index, i_index))

        return positions

# Copy of game with given move
    def game_state_with_move(self, move):
        game_copy = copy.deepcopy(self)
        game_copy.move(move)
        return game_copy

    def minimax(self, depth, alpha, beta, last_node_rating=0):

        if self.has_winner() == True or depth >= 3:

            if self.winner() == self.ai_player:
                return sys.maxsize
            elif self.winner() == Player.none:
                return last_node_rating
            else:
                return -sys.maxsize


        ai_on_move = self.whose_turn() == self.ai_player

        depth += 1
        rates, moves = [], []

        for position in self.available_positions():

            possible_game = self.game_state_with_move(position)

            if ai_on_move:
                rating_for_move = last_node_rating + (possible_game.calculate_rating_for_move(position) * (1-(depth / 10)))
            else:
                rating_for_move = last_node_rating


            moves.append(position)

            rates.append(possible_game.minimax(depth, alpha, beta, rating_for_move))

            if ai_on_move:
                alpha = max(alpha, rates[-1])
            else:
                beta = min(beta, rates[-1])


            if alpha >= beta:
                break

        m_value = max(rates) if ai_on_move else min(rates)

        index = rates.index(m_value)

        self.ai_next_move = moves[index]

        return rates[index]
