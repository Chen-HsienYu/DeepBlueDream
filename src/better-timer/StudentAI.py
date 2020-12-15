from random import randint
from BoardClasses import Move, Board
from time import time
from copy import deepcopy
from math import sqrt, log
from operator import attrgetter#, itemgetter

OPPONENT = {1:2, 2:1}
C_VAL = sqrt(2) # exploration constant for UCB
SIMULATION_DEPTH = 60 # max moves for simulated games
INITIAL_TIME_DIVISOR_C = 0.5

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
        self.total_time_remaining = 479
        self.time_divisor = row * col * INITIAL_TIME_DIVISOR_C
        self.timed_move_count = 2
        
    def get_move(self, move) -> Move:
        '''
        prune tree with opponent move
        MCTS
        '''
        # Start timer
        start_time = time()
        
        # Check if opponent gave a turn and execute it
        if len(move) != 0:
            self.play_move(move, OPPONENT[self.color])
        # If first move of game, change self.color and make random move
        else:
            self.color = 1
            self.mcts.root = TreeNode(self.board, self.color, None, None)

            moves = self.board.get_all_possible_moves(self.color)
            first_move = moves[0][1]
            self.play_move(first_move, self.color)
            return first_move
        
        # Check if only one move is possible
        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1 and len(moves[0]) == 1:
            self.play_move(moves[0][0], self.color)
            return moves[0][0]
        
        # set up time limit
        time_limit = self.total_time_remaining / self.time_divisor
        
        # MCTS
        move_chosen = self.mcts.search(time_limit)
        self.play_move(move_chosen, self.color)
        
        # change time divisor
        self.time_divisor -= 0.5 - 1/self.timed_move_count
        self.timed_move_count += 1
        
        # decrement time remaining and return
        self.total_time_remaining -= time() - start_time
        return move_chosen
    
    def play_move(self, move, color):
        """
        Updates board and tree root using Move given,
        either Move we just played or Move given by opponent.
        """
        self.board.make_move(move, color)
        
        for child in self.mcts.root.children.items():
            if str(move) == str(child[0]) and child[1] is not None:
                self.mcts.root = child[1]
                self.mcts.root.parent = None
                return

        self.mcts.root = TreeNode(self.board, OPPONENT[color], None, None)
    
class MCTS():
    def __init__(self, root):
        self.root = root
          
    def search(self, time_limit) -> Move:
        '''
        Performs Monte Carlo Tree Search until time runs out.
        Returns the best move.
        '''
        timeout = time() + time_limit
                
        while time() < timeout:
            # select node from the tree
            node = self.selection(self.root)
            # simulate outcome of the game
            temp_board = deepcopy(node.board)
            temp_color = node.color
            win_val = temp_board.is_win(OPPONENT[temp_color])
            depth_limit = SIMULATION_DEPTH
            
            while not win_val and depth_limit:
                temp_board.make_move(get_random_move(temp_board, temp_color), temp_color)
                win_val = temp_board.is_win(temp_color)
                temp_color = OPPONENT[temp_color]
                depth_limit -= 1
    
            # reorder these to short circuit most common
            if not win_val:
                win_for_parent = -self.get_heuristic(temp_board, node.color)
            elif win_val == OPPONENT[node.color]:
                win_for_parent = 1
            elif win_val == node.color:
                win_for_parent = -1
            elif win_val == -1:
                win_for_parent = 0
            # update values in tree
            node.backpropogate(win_for_parent)

        return self.best_child()
    
    def selection(self, node) -> 'TreeNode':
        '''
        Recursively traverses the tree to find a terminal node with the highest UCB value,
        then expands a new unexplored node.
        '''
        if len(node.children) == 0:
            return node
        if None not in node.children.values():
            sorted_children = sorted(node.children.values(), key=attrgetter('ucb_value'), reverse=True)
            return self.selection(sorted_children[0])
        for move, child in node.children.items():
            if child is None:
                node.children[move] = TreeNode(node.board, OPPONENT[node.color], move, node)
                return node.children[move]
                                
#     def simulate(self, node) -> None:
#         '''
#         Create a copy of the board and simulate a game with random moves.
#         Backpropogates the result at the end of the simulated game.
#         '''
#         temp_board = deepcopy(node.board)
#         temp_color = node.color
#         win_val = temp_board.is_win(OPPONENT[temp_color])
#         depth_limit = SIMULATION_DEPTH
#         
#         while not win_val and depth_limit:
#             temp_board.make_move(get_random_move(temp_board, temp_color), temp_color)
#             win_val = temp_board.is_win(temp_color)
#             temp_color = OPPONENT[temp_color]
#             depth_limit -= 1
# 
#         # reorder these to short circuit most common
#         if not win_val:
#             win_for_parent = -self.get_heuristic(temp_board, node.color)
#         elif win_val == OPPONENT[node.color]:
#             win_for_parent = 1
#         elif win_val == node.color:
#             win_for_parent = -1
#         elif win_val == -1:
#             win_for_parent = 0
#             
#         node.backpropogate(win_for_parent)
    
    def best_child(self) -> Move:
        '''
        Return the move with highest visit count.
        '''
#         if None in self.root.children.values():
#             return get_random_move(self.root.board, self.root.color)

        sorted_moves = sorted(self.root.children.items(), key=lambda x: x[1].visit_count, reverse=True)
        return sorted_moves[0][0]
    
    def get_heuristic(self, b, color):
        '''
        Evaluates a board and returns a value between 0-1.
        '''
        moves_self = b.get_all_possible_moves(color)
        moves_opp = b.get_all_possible_moves(OPPONENT[color])
        
        # There are 4 heuristics that are prioritized in the following order:

        # weighted_piece_score
        # pawn_position_score
        # base_piece_score
        # random

        # weighted_piece_score is the highest priority margin. It attempts to measure the amount of pieces self has vs the 
        # opponent accounting for kings. Because Board itself doesn't have an attribute for this we assume a piece is a king if it
        # can make more than 2 moves. This isn't entirely accurate but a piece is worth more if it has more options anyway.
        weighted_piece_score = 0

        # pawn_position_score is also measured in these for loops. A pawn is worth more if it's closer to the opposing end 
        # than near the beginning, so we calculate the distance between a pawn and the start of the board in our measurement.
        # This measurement is unfortunately flawed because a king on the side of the board only has 2 available moves, and
        # only pieces capable of moving can be accounted for, but there's not much to be done about that.
        pawn_position_score = 0

        for p in moves_self:
            if len(p) <= 2:
                weighted_piece_score += 3

                # An attempt to get the y coordinate of a piece by obtaining the first position on one of Move() objects
                # for the piece. In theory we are iterating through a list of lists of moves, so p[0] should be a Move(),
                # p[0].seq should be that Move()'s sequence of coordinates, p[0].seq[0] should be the first coordinate in
                # that sequence, and p[0].seq[0][1] should be the y coordinate.
                if len(p):
                    vertPos = p[0].seq[0][1]
                    if color == 1:
                        pawn_position_score += vertPos
                    else:
                        pawn_position_score += (b.row - vertPos)
            else:
                weighted_piece_score += 5

        for p in moves_opp:
            if len(p) <= 2:
                weighted_piece_score -= 3
                if len(p):
                    vertPos = p[0].seq[0][1]
                    if color == 2:
                        pawn_position_score -= vertPos
                    else:
                        pawn_position_score -= (b.row - vertPos)
            else:
                weighted_piece_score -= 5

        if weighted_piece_score < 0:
            weighted_piece_score = 0
        if pawn_position_score < 0:
            pawn_position_score = 0

        # base_piece_score is a low priority heuristic, measuring only the amount of pieces on the board without accounting
        # for weight or position, since trades are good for the player with more pieces.
        if color == 1:
            base_piece_score = b.black_count - b.white_count
        else:
            base_piece_score = b.white_count - b.black_count

        if base_piece_score < 0:
            base_piece_score = 0
        # At the end we multiply the numbers based on their priority and add them so we get a functioning heuristic:
        # Example score with weighted_score 17, pawn_position_score 25, and base_piece_score 5 would be 172505x, with the
        # last digit being random
        total_score = weighted_piece_score * 100000 + pawn_position_score * 1000 + base_piece_score * 10 + randint(0,9)
        # We then divide it by 10^7 so that it's less than 1, since an un-won board is worth less than a won board:
        return total_score / 10000000
    
class TreeNode():
    def __init__(self, board, color, move, parent):
        self.board = deepcopy(board)
        self.color = color
        self.parent = parent
        self.visit_count = 1 # change this to zero?
        self.wins_for_parent = 0
        self.ucb_value = 0
        
        # Execute nodes' first move
        if move is not None:
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
 
    def backpropogate(self, win_for_parent) -> None:
        '''
        REcursively updates statistics for this node and all parents,
        given an outcome of the game.
        (1 is win for the parent, -1 is loss for the parent, 0 is tie,
        decimal values are based on heuristic)
        '''
        if self.parent:
            self.parent.backpropogate(-win_for_parent)
            
            self.visit_count += 1
            
            if win_for_parent > 0:
                self.wins_for_parent += win_for_parent
            elif not win_for_parent:
                self.wins_for_parent += 0.5
                     
            # calculate UCB value
            self.ucb_value = self.wins_for_parent/self.visit_count + C_VAL * sqrt(log(self.parent.visit_count)/self.visit_count)
        
# REMOVE THIS BEFORE SUBMITTING #
# if __name__ == '__main__':
#     import os
#     os.system('python3 main.py 7 7 2 m main.py')
# REMOVE THIS BEFORE SUBMITTING #
