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

        # code for random move
#         moves = self.board.get_all_possible_moves(self.color)
#         index = randint(0, len(moves) - 1)
#         inner_index = randint(0, len(moves[index]) - 1)
#         move = moves[index][inner_index]
#         self.board.make_move(move, self.color)
#         return move

class GameTreeNode():
    opponent = {1:2, 2:1}

    def __init__(self, board, color, move):
        #self.children = board.get_all_possible_moves(self.color)
        #self.parent = 0
        #self.losses = 0
        #self.ties = 0 # consider ties as a win for grading?
        self.board = board
        self.color = color
        self.move = move
        self.visit_count = 0
        self.wins = 0
        self.win_rate = 0
        
    def simulate_random(self):
        temp_board = deepcopy(self.board)
        temp_board.make_move(self.move, self.color)
            
        temp_color = GameTreeNode.opponent[self.color]
        while temp_board.is_win(temp_color) == 0:
            temp_moves = temp_board.get_all_possible_moves(temp_color)
            
            if len(temp_moves) == 0:
                break
#             temp_board.show_board()
#             print(temp_color)
#             print(temp_moves)
            
            i = randint(0, len(temp_moves) - 1)
            j = randint(0, len(temp_moves[i]) - 1)
            temp_move = temp_moves[i][j]
            
            temp_board.make_move(temp_move, temp_color)
            temp_color = GameTreeNode.opponent[temp_color]
            
        self.visit_count += 1
        if temp_board.is_win(self.color) == self.color:
            self.wins += 1
        self.win_rate = self.wins / self.visit_count
        
        return       
        
class StudentAI():
    time_limit = 15

    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.opponent = {1:2, 2:1}
        self.color = 2

    def get_move(self, move):
        timeout = time.time() + StudentAI.time_limit

        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
            moves = self.board.get_all_possible_moves(self.color)
            index = randint(0, len(moves) - 1)
            inner_index = randint(0, len(moves[index]) - 1)
            move = moves[index][inner_index]
            self.board.make_move(move, self.color)
            return move

        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1 and len(moves[0]) == 1:
            self.board.make_move(moves[0][0], self.color)
            return moves[0][0]
        
        children = list()
        for i in range(len(moves)):
            for j in range(len(moves[i])):
                children.append(GameTreeNode(self.board, self.color, moves[i][j]))
        
        while time.time() < timeout:
            i = randint(0, len(children) - 1)
            children[i].simulate_random()
        
        sorted_moves = sorted(children, key=lambda x: x.win_rate)
        print(sorted_moves[-1].visit_count)
        move = sorted_moves[-1].move
        self.board.make_move(move, self.color)
        return move
    