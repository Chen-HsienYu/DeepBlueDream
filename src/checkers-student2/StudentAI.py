from random import randint
from BoardClasses import Move
from BoardClasses import Board

class node:
    def __init__(self,value=None,parent=None,children=list()):
        self.value = value
        self.parent = parent
        self.children = list(children)
        
    def addChild(self,value):
        self.children.append(node(value=value,parent=self,children=list()))
        
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
    def __init__(self,value=None,children=list()):
        super().__init__(value,None,children)
        
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
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)
        index = randint(0,len(moves)-1)
        inner_index =  randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        self.board.make_move(move,self.color)
        return move
