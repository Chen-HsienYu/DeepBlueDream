from random import randint
from BoardClasses import Move, Board
from time import time
from copy import deepcopy
from math import sqrt, log
from operator import attrgetter

OPPONENT = {1: 2, 2: 1}

def get_random_move(board, color) -> Move:
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
        # Default color; if our AI moves first we switch below.
        self.color = 2  
        # Initialize the MCTS tree with the current board state and our color.
        self.mcts = MCTS(TreeNode(self.board, self.color, None, None))
        self.total_time_remaining = 479
        self.time_divisor = row * col * 0.5
        self.timed_move_count = 2
        
    def get_move(self, move) -> Move:
        start_time = time()
        # If opponent has moved, update our board
        if len(move) != 0:
            self.play_move(move, OPPONENT[self.color])
        else:
            # If this is the first move, we assume we are playing white (player 1)
            self.color = 1
            self.mcts.root = TreeNode(self.board, self.color, None, None)
            moves = self.board.get_all_possible_moves(self.color)
            # Choose a predetermined first move (here, second move in list of first piece's moves)
            first_move = moves[0][1]
            self.play_move(first_move, self.color)
            return first_move
        
        # If only one move is possible, take it.
        moves = self.board.get_all_possible_moves(self.color)
        if len(moves) == 1 and len(moves[0]) == 1:
            self.play_move(moves[0][0], self.color)
            return moves[0][0]
        
        # Set up a time limit for this move (adjustable)
        time_limit = self.total_time_remaining / self.time_divisor
        
        # Use MCTS with our modified simulation
        move_chosen = self.mcts.search(time_limit)
        self.play_move(move_chosen, self.color)
        
        # Update time management parameters
        self.time_divisor -= 0.5 - 1 / self.timed_move_count
        self.timed_move_count += 1
        self.total_time_remaining -= time() - start_time
        return move_chosen
    
    def play_move(self, move, color):
        self.board.make_move(move, color)
        # Try to find the corresponding child in our MCTS tree to reuse the subtree.
        for child_move, child_node in self.mcts.root.children.items():
            if str(move) == str(child_move) and child_node is not None:
                self.mcts.root = child_node
                self.mcts.root.parent = None
                return
        # Otherwise, rebuild the tree with the new board state.
        self.mcts.root = TreeNode(self.board, OPPONENT[color], None, None)

class MCTS():
    def __init__(self, root):
        self.root = root
        # Set a cutoff depth for simulation rollouts
        self.depth_cutoff = 5

    def search(self, time_limit) -> Move:
        timeout = time() + time_limit
        # Run iterations until time is up.
        while time() < timeout:
            # Select a node from the tree.
            node = self.selection(self.root)
            # Run a simulation from that node with a depth cutoff.
            simulation_score = self.simulate(deepcopy(node.board), node.color, self.depth_cutoff)
            # Here, positive score means win for the parent of the node.
            # We reverse the sign to update the node’s parent appropriately.
            win_for_parent = simulation_score  
            node.backpropogate(win_for_parent)
        return self.best_child()
    
    def selection(self, node) -> 'TreeNode':
        if len(node.children) == 0:
            return node
        if None not in node.children.values():
            sorted_children = sorted(node.children.values(), key=attrgetter('ucb_value'), reverse=True)
            return self.selection(sorted_children[0])
        for move, child in node.children.items():
            if child is None:
                node.children[move] = TreeNode(node.board, OPPONENT[node.color], move, node)
                return node.children[move]
    
    def best_child(self) -> Move:
        # Choose the move whose child has the highest visit count.
        sorted_moves = sorted(self.root.children.items(), key=lambda x: x[1].visit_count, reverse=True)
        return sorted_moves[0][0]
    
    def simulate(self, board, color, depth) -> float:
        """
        Recursively simulates a playout from the given board state.
        If the depth cutoff is reached, returns a heuristic evaluation.
        Uses a negamax style recursion.
        """
        # Check if game is over.
        win_val = board.is_win(OPPONENT[color])
        if win_val != 0:
            # Assign high scores for win/loss outcomes.
            if win_val == OPPONENT[self.root.color]:
                return 1.0
            elif win_val == self.root.color:
                return -1.0
            else:
                return 0.0
        # At cutoff depth, use heuristic evaluation.
        if depth == 0:
            return self.heuristic(board)
        # Otherwise, select a random move and simulate recursively.
        move = get_random_move(board, color)
        board.make_move(move, color)
        score = -self.simulate(board, OPPONENT[color], depth - 1)
        board.undo()
        return score

    def heuristic(self, board) -> float:
        """
        A simple heuristic: difference in weighted piece counts.
        For this example, we count each regular piece as 1 and each king as 6.
        The heuristic is normalized to fall roughly between -1 and 1.
        """
        if self.root.color == 1:
            our_piece, opp_piece = 'B', 'W'
        else:
            our_piece, opp_piece = 'W', 'B'
        our_count = 0
        opp_count = 0
        for row in board.board:
            for checker in row:
                if checker.color == our_piece:
                    our_count += 1 + (5 if checker.is_king else 0)
                elif checker.color == opp_piece:
                    opp_count += 1 + (5 if checker.is_king else 0)
        return (our_count - opp_count) / 100.0  # scaling factor

class TreeNode():
    def __init__(self, board, color, move, parent):
        self.board = deepcopy(board)
        self.color = color
        self.parent = parent
        self.visit_count = 1
        self.wins_for_parent = 0.0
        self.ucb_value = 0.0
        
        # If a move was taken to reach this node, update board.
        if move is not None:
            self.board.make_move(move, OPPONENT[self.color])
        self.children = dict()
        # Only expand if game is not over.
        if self.board.is_win(OPPONENT[self.color]) == 0:
            moves_list = self.board.get_all_possible_moves(self.color)
            for i in range(len(moves_list)):
                for j in range(len(moves_list[i])):
                    self.children[moves_list[i][j]] = None
 
    def backpropogate(self, win_for_parent) -> None:
        self.visit_count += 1
        # Propagate the simulation outcome up the tree (negating at each level).
        if self.parent:
            self.parent.backpropogate(-win_for_parent)
        # Update wins for parent; here ties can count as half-win.
        if win_for_parent > 0:
            self.wins_for_parent += win_for_parent
        elif win_for_parent == 0:
            self.wins_for_parent += 0.5
        # Update UCB value (using exploration constant sqrt(2)).
        if self.parent:
            self.ucb_value = (self.wins_for_parent / self.visit_count +
                              sqrt(2) * sqrt(log(self.parent.visit_count) / self.visit_count))
