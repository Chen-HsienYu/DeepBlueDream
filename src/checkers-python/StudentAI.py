# NOTE: print() will only work in manual mode

# module load python/3.5.2

# COMMAND TO MANUALLY PLAY AGAINST StudentAI
# python3 src/checkers-python/main.py {col} {row} {p} m {start_player (0 or 1)}
# python3 src/checkers-python/main.py 7 7 2 m 0

# COMMAND TO TEST StudentAI AGAINST Random_AI
# python3 src/checkers-python/main.py {row} {column} {rows occupied by pieces} l {AI_1_path} {AI_2_path}
# python3.5 src/checkers-python/main.py 7 7 2 l Tools/Sample_AIs/Random_AI/main.py src/checkers-python/main.py

from random import randint
from BoardClasses import Move
from BoardClasses import Board
import time
from copy import deepcopy

#         CODE FOR PICKING RANDOM MOVE
#         moves = self.board.get_all_possible_moves(self.color)
#         index = randint(0, len(moves) - 1)
#         inner_index = randint(0, len(moves[index]) - 1)
#         move = moves[index][inner_index]
#         self.board.make_move(move, self.color)
#         return move

class GameTreeNode():
    opponent = {1:2, 2:1}

    def __init__(self, board, color, move):
#         self.children = list()
#         self.parent = None
#         self.ties = 0 # consider ties as half a win for grading (not for tournament)?
        self.board = board
        self.color = color
        self.move = move
        self.visit_count = 0
        self.wins = 0
        self.win_rate = 0

    def simulate_random(self):
        '''
        Create a copy of the board and simulate a game with random moves
        '''
        temp_board = deepcopy(self.board)
        # execute child node's first move
        temp_board.make_move(self.move, self.color)

        # change to opponents color
        temp_color = GameTreeNode.opponent[self.color]
        while temp_board.is_win(temp_color) == 0:
            temp_moves = temp_board.get_all_possible_moves(temp_color)
            if len(temp_moves) == 0: # idk why while condition doesn't catch this
                break
#             temp_board.show_board()
#             print(temp_color)
#             print(temp_moves)

            # select random move
            i = randint(0, len(temp_moves) - 1)
            j = randint(0, len(temp_moves[i]) - 1)
            temp_move = temp_moves[i][j]

            # execute random move
            temp_board.make_move(temp_move, temp_color)
            # switch players
            temp_color = GameTreeNode.opponent[temp_color]

        self.backpropogate(temp_board.is_win(self.color))
        return

    def backpropogate(self, win_val):
        '''
        Update statistics
        '''
        self.visit_count += 1
        if  win_val == self.color:
            self.wins += 1
        self.win_rate = self.wins / self.visit_count # delete this for UCB

#         if self.parent != None:
#             self.parent.backpropogate()
        return

class StudentAI():
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.opponent = {1:2, 2:1}
        self.color = 2
        self.time_limit = 15 # seconds per turn

    def get_move(self, move):
        timeout = time.time() + self.time_limit

        # check if opponent gave a turn and execute it
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        # if first move of game, change self.color and make random move
        else:
            self.color = 1
            moves = self.board.get_all_possible_moves(self.color)
            index = randint(0, len(moves) - 1)
            inner_index = randint(0, len(moves[index]) - 1)
            move = moves[index][inner_index]
            self.board.make_move(move, self.color)
            return move

        # check if only one move is possible
        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1 and len(moves[0]) == 1:
            self.board.make_move(moves[0][0], self.color)
            return moves[0][0]

        # create all children of root
        children = list()
        for i in range(len(moves)):
            for j in range(len(moves[i])):
                children.append(GameTreeNode(self.board, self.color, moves[i][j]))

        # pick random moves and simulate outcomes
        while time.time() < timeout:
            i = randint(0, len(children) - 1)
            children[i].simulate_random()

        # select move with highest win rate
        sorted_moves = sorted(children, key=lambda x: x.win_rate)
        print(sorted_moves[-1].visit_count)
        move = sorted_moves[-1].move
        self.board.make_move(move, self.color)
        return move
