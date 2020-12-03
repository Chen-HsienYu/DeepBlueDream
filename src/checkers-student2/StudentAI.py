from random import randint
from BoardClasses import Move
from BoardClasses import Board
from copy import deepcopy
import time 

class node:
    def __init__(self,value=None,sv=0,parent=None,children=list()):
        self.value = value
        self.secondValue = sv
        self.parent = parent
        self.children = list(children)
        
    def addChild(self,value,sv):
        self.children.append(node(value=value,sv=0,parent=self,children=list()))
        
    def setChildren(self,nodes):
        self.children = list(nodes)
        for n in self.children:
            n.parent = self

    def clearChildren(self):
        del self.children
        self.children = list()

    def isHeadNode(self):
        return False

class headNode(node):
    def __init__(self,value=None,sv=0,children=list()):
        super().__init__(value,sv,None,children)
        
    def isHeadNode(self):
        return True

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        
        self.rootNode = None
        
    def get_move(self,move):
        moves = self.board.get_all_possible_moves(self.color)
        
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
            self.rootNode = headNode(value = [self.board, self.color])
            i = randint(0, len(moves) - 1)
            returnMove = moves[i][randint(0,len(moves[i]) - 1))]
            
                                  
        
        #Random AI
        '''
        index = randint(0,len(moves)-1)
        inner_index =  randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        '''
        
        if len(moves) == 1 and len(moves[0]) == 1:
            self.board.make_move(moves[0][0], self.color)
            return moves[0][0]
        
        returnMove = self.mcts(self.rootNode)
        
        self.board.make_move(returnMove,self.color)
        return returnMove
    
    def mcts(self, root):
        timeLimit = time.time() + 9.8
        while (time.time() < timeLimit):
            leaf = self.traverse(root)
            backpropagate(leaf, rollout(leaf))
        
        return best_child(root)
    
    def traverse(n):
        if len(n.children) == 0:
            moves = n.value[0].get_all_possible_moves(n.value[1])
            for i in moves:
                tempBoard = deepcopy(n.value[0])
                tempBoard.make_move(i,n.value[1])
                n.addChild([tempBoard,self.opponent[tempBoard.color]])
        
        if len(n.children) == 0:
            return n
        return self.traverse(self.best_ucb(n))
        
    
    def rollout(n):
        pass
    
    def rollout_policy(n):
        pass
    
    def backpropagate(n, result):
        pass
    
    def best_child(n):
        pass
    
    def best_ucb(n):
        pass
    
    '''
# main function for the Monte Carlo Tree Search 
def monte_carlo_tree_search(root): 
      
    while resources_left(time, computational power): 
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
  
# function for backpropagation 
def backpropagate(node, result): 
    if is_root(node) return
    node.stats = update_stats(node, result)  
    backpropagate(node.parent) 
  
# function for selecting the best child 
# node with highest number of visits 
def best_child(node): 
    pick child with highest number of visits 
'''
