import sys
from pip._vendor.pyparsing import col
sys.path.append("./AI_Extensions/")
from AI_Extensions import *
from collections import defaultdict
#import time

# Running this file with no arguments will play one game with the default settings
# TO RUN WITH DIFFERENT SETTINGS:
# python3 DeepBlueDream/src/statistics/statistics.py {iterations}
# python3 DeepBlueDream/src/statistics/statistics.py {row} {column} {rows occupied by pieces} {iterations}
# python3 DeepBlueDream/src/statistics/statistics.py {row} {column} {rows occupied by pieces} {iterations} {AI_1_path} {AI_2_path}
        
class GameLogic:
    def __init__(self,col=7,row=7,p=2,ai1='../checkers-python/main.py',ai2='../../Tools/Sample_AIs/Random_AI/main.py'):
        self.col = col
        self.row = row
        self.p = p
        self.ai = (ai1, ai2)
        self.timeout = 60*8
        self.win_stats = defaultdict(int)
        self.color_name = {1:'(black)', 2:'(white)'}   
        #self.time_stats = dict()

    def run(self,iterations, fh=None):
        '''
        Simulates {iterations} numbers of games between the two AI's.
        Switches players halfway through.
        Prints the results of all games at the end.
        '''
        if iterations == 1:
            self._run(1, 0)
        else:
            iterations = self.check_even(iterations)
        
            self._run(iterations//2, 0)
            game._switch_player_order()
            self._run(iterations//2, iterations//2)        
                
        #open file with unique name here
        print('**********************', file=fh)
        print('columns   :', self.col, file=fh)
        print('rows      :', self.row, file=fh)
        print('p         :', self.p, file=fh)
        print('iterations:', iterations, file=fh)
        print('AI #1     :', self.ai[0], file=fh)
        print('AI #2     :', self.ai[1], file=fh)
        print('**********************', file=fh)
        for name, wins in self.win_stats.items():
            if name == -1:
                name = 'TIE GAME'
            print(name, file=fh)
            print('total wins:', wins, file=fh)
            print('win %     :', round(wins*100.0/iterations, 2), file=fh)
            print(file=fh)
        print('**********************', file=fh)

    def _run(self, iterations, previous_games, fh=None):
        for i in range(iterations):
            print('**********************', file=fh)        
            print('Game #', i+previous_games+1,file=fh)
            print('**********************', file=fh)
            self.ai_list = []
            self.ai_list.append(IOAI(self.col, self.row, self.p, ai_path=self.ai[0], time=self.timeout))
            self.ai_list.append(IOAI(self.col, self.row, self.p, ai_path=self.ai[1], time=self.timeout))
            self.win_stats[self.gameloop(fh)] += 1         

    def gameloop(self,fh=None):
        player = 1
        winPlayer = 0
        move = Move([])
        board = Board(self.col,self.row,self.p)
        board.initialize_game()
        board.show_board(fh)
        while True:
            print(self.ai[player-1],self.color_name[player],'is thinking...',file=fh)
            try:
                move = self.ai_list[player-1].get_move(move)
            except:
                import traceback
                print(self.ai[player-1],"crashed!",file=fh)
                traceback.print_exc(file=fh)
                if player == 1:
                    winPlayer = 2
                else:
                    winPlayer = 1
                break
            
            try:
                board.make_move(move,player)
            except InvalidMoveError:
                print("Invalid Move!",file=fh)
                if player == 1:
                    winPlayer = 2
                else:
                    winPlayer = 1
                break
            
            winPlayer = board.is_win(player)
            board.show_board(fh)
            if(winPlayer != 0):
                break
            if player == 1:
                player = 2
            else:
                player = 1
        if winPlayer == -1:
            print("Tie", file=fh)
        else:
            print(self.ai[winPlayer-1],'WINS',file=fh)

        for AI in self.ai_list:
            if type(AI) is IOAI:
                AI.close()
        return self.ai[winPlayer-1]
    
    def _switch_player_order(self):
        self.ai = (self.ai[1], self.ai[0])
              
    @staticmethod       
    def check_even(num):
        '''
        Returns num+1 if num is odd
        '''
        if num % 2 == 1:
            num += 1
        return num

if __name__ == "__main__":
    iterations = 1
    
    if len(sys.argv) == 1:
        game = GameLogic()      
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
        game = GameLogic()
    if len(sys.argv) == 5:
        col = int(sys.argv[1])
        row = int(sys.argv[2])
        p = int(sys.argv[3])
        iterations = int(sys.argv[4])
        game = GameLogic(row, col, p)
    if len(sys.argv) == 7:
        col = int(sys.argv[1])
        row = int(sys.argv[2])
        p = int(sys.argv[3])
        iterations = int(sys.argv[4])
        ai1_filepath = sys.argv[5]
        ai2_filepath = sys.argv[6]
        game = GameLogic(row, col, p, ai1_filepath, ai2_filepath)

    game.run(iterations)