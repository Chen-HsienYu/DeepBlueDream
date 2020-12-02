
from random import randint
from BoardClasses import Move, Board
import time
from copy import deepcopy
from math import sqrt, log
#from operator import itemgetter, attrgetter

OPPONENT = {1:2, 2:1}
# MAX_PROCESSES = 1 # unused for now
TIME_LIMIT = 9 # seconds per turn
C_VAL = 0.7 # exploration constant for UCB

def get_random_move(board, color) -> Move:
    '''
    Given a board state and color, returns a random move.
    '''
    moves = board.get_all_possible_moves(color)
    index = randint(0, len(moves) - 1)
    inner_index = randint(0, len(moves[index]) - 1)
    return moves[index][inner_index]
    
class StudentAI():
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2
        self.mcts = MCTS(TreeNode(self.board, self.color, None, None))
        
        # Unused for now
#         if MAX_PROCESSES > 1:
#             print('start generating tree')
            
        # Use these for dynamically setting move timer?
#         self.move_counter = 0
#         self.total_time = 8 * 60 - 1
        
    def get_move(self, move) -> Move:
        '''
        merge trees
        prune tree with opponent move
        stop sub processes
        MCTS
        start again right before returning move
        '''
        # Check if opponent gave a turn and execute it
        if len(move) != 0:
            self.play_move(move, OPPONENT[self.color])
        # If first move of game, change self.color and make random move
        else:
            self.color = 1
            self.mcts.root = TreeNode(self.board, self.color, None, None)
            # hardcode in popular opening moves here???
            move_chosen = get_random_move(self.board, self.color)
            self.play_move(move_chosen, self.color)
            return move_chosen
        
        # Check if only one move is possible
        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1 and len(moves[0]) == 1:
            self.play_move(moves[0][0], self.color)
            return moves[0][0]        
        
        move_chosen = self.mcts.search()
        self.play_move(move_chosen, self.color)
        return move_chosen
    
    def play_move(self, move, color):
        """
        Updates board and tree root using Move given,
        either Move we just played or Move given by opponent.
        """
        self.board.make_move(move, color)
        
        for child in self.mcts.root.children.items():
            if str(move) == str(child[0]) and child[1] != None:
                self.mcts.root = child[1]
                self.mcts.root.parent = None
                return

        self.mcts.root = TreeNode(self.board, OPPONENT[color], None, None)
    
class MCTS():
    def __init__(self, root):
        self.root = root
              
    def search(self) -> Move:
        '''
        Performs Monte Carlo Tree Search until time runs out.
        Returns the best move.
        '''
        timeout = time.time() + TIME_LIMIT
                
        while time.time() < timeout:
            self.simulate(self.selection(self.root))
        
        return self.best_child()
    
    def selection(self, node) -> 'TreeNode':
        '''
        Recursively traverses the tree to find a terminal node with the highest UCB value,
        then expands a new unexplored node.
        '''
        if len(node.children) == 0:
            return node
        if None not in node.children.values():
            sorted_children = sorted(node.children.values(), key=lambda x: x.get_ucb(), reverse=True)
            return self.selection(sorted_children[0])
        for move, child in node.children.items():
            if child == None:
                node.children[move] = TreeNode(node.board, OPPONENT[node.color], move, node)
                return node.children[move]
                                
    def simulate(self, node) -> None:
        '''
        Create a copy of the board and simulate a game with random moves.
        Backpropogates the result at the end of the simulated game.
        
        eventually add a basic heuristic...
        '''
        temp_board = deepcopy(node.board)
        temp_color = node.color
        win_val = temp_board.is_win(OPPONENT[temp_color])
        
        while (win_val == 0):
            temp_move = get_random_move(temp_board, temp_color)
            temp_board.make_move(temp_move, temp_color)
            win_val = temp_board.is_win(temp_color)
            temp_color = OPPONENT[temp_color]

        node.backpropogate(win_val)
    
    def best_child(self) -> Move:
        '''
        Return the move with highest visit count.
        
        TODO: account for child nodes that are None b/c low on time
        '''
        sorted_moves = sorted(self.root.children.items(), key=lambda x: x[1].visit_count, reverse=True)
        return sorted_moves[0][0]
    
class TreeNode():
    def __init__(self, board, color, move, parent):
        self.board = deepcopy(board)
        self.color = color
        self.parent = parent
        self.visit_count = 1 # change this to zero?
        self.wins_for_parent = 0
        
        # Execute nodes' first move
        if move != None:
            self.board.make_move(move, OPPONENT[self.color])
        self.children = self._create_children()

    def _create_children(self) -> 'list[TreeNode]':
        '''
        Returns a dict where key=all possible moves, value=None.
        '''
        children = dict()
        # If game is already over, do not create children        
        if self.board.is_win(OPPONENT[self.color]) != 0:
            return children

        moves_list = self.board.get_all_possible_moves(self.color)
        for i in range(len(moves_list)):
            for j in range(len(moves_list[i])):
                children[moves_list[i][j]] = None
        return children
 
    def backpropogate(self, win_val) -> None:
        '''
        Update statistics
        
        consider ties as half a win for grading?
        '''
        self.visit_count += 1
        if win_val == OPPONENT[self.color]:
            self.wins_for_parent += 1
#       if win_val == -1:
#           self.wins += 0.5
         
        if self.parent != None:
            self.parent.backpropogate(win_val)
     
    def get_ucb(self) -> float:
        '''
        Returns UCB value.
        '''
        return self.wins_for_parent/self.visit_count + C_VAL * sqrt(log(self.parent.visit_count)/self.visit_count)
        
# REMOVE THIS BEFORE SUBMITTING #
if __name__ == '__main__':
    import os
    os.system('python3 main.py 7 7 2 m main.py')
# REMOVE THIS BEFORE SUBMITTING #
