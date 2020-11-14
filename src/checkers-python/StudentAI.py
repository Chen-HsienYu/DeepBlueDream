# NOTE: print() will only work in manual mode

# COMMAND TO MANUALLY PLAY AGAINST StudentAI
# python3 src/checkers-python/main.py {col} {row} {p} m {start_player (0 or 1)}
# python3 src/checkers-python/main.py 7 7 2 m 0

# COMMAND TO TEST StudentAI AGAINST Random_AI
# python3 src/checkers-python/main.py {row} {column} {rows occupied by pieces} l {AI_1_path} {AI_2_path}
# python3 src/checkers-python/main.py 7 7 2 l Tools/Sample_AIs/Random_AI/main.py src/checkers-python/main.py

from random import randint
from BoardClasses import Move
from BoardClasses import Board
import time

# Students can modify anything except the class name and existing functions and variables.
class GameTreeNode():
    def __init__():
        self.children = list()
        self.visit_count = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0 # consider ties as a win for grading?
        self.board = 'placeholder'
        
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
        
        # code for random move
        moves = self.board.get_all_possible_moves(self.color)
        index = randint(0, len(moves) - 1)
        inner_index = randint(0, len(moves[index]) - 1)
        move = moves[index][inner_index]
        self.board.make_move(move, self.color)
        return move
    
        # code for MCTS
        root = 'placeholder'
        while time.time() < timeout:
            leaf = traverse(root)
            simulation_result = rollout(leaf)
            backpropagate(leaf, simulation_result)

        return best_child(root)
    
    # function for node traversal
    def traverse(node):
        while fully_expanded(node):
            node = best_uct(node)

        # in case no children are present / node is terminal
        return pick_univisted(node.children) or node

    # function for the result of the simulation
    def rollout(node):
        while non_terminal(node):
            node = rollout_policy(node)
        return result(node)

    # function for randomly selecting a child node
    def rollout_policy(node):
        return pick_random(node.children)

    # function for back-propagation
    def backpropagate(node, result):
        if is_root(node):
            return
        node.stats = update_stats(node, result)
        backpropagate(node.parent)

    # function for selecting the best child
    # node with highest number of visits
    def best_child(node):
        # pick child with highest number of visits
        return
