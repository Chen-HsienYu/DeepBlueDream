import sys
from pip._vendor.pyparsing import col
sys.path.append("./AI_Extensions/")
from AI_Extensions import *
from collections import defaultdict
#import time
        
student = '../checkers-python/main.py'
no_heuristic = '../no-heuristic/main.py'
better_timer = '../better-timer/main.py'
rave = '../rave/main.py'

random = '../../Tools/Sample_AIs/Random_AI/main.py'
average = '../../Tools/Sample_AIs/Average_AI/main.py'
good = '../../Tools/Sample_AIs/Good_AI/main.py'

class GameLogic:
    def __init__(self, col=7, row=7, p=2, ai1=rave, ai2=student):
        self.col = col
        self.row = row
        self.p = p
        self.ai = (ai1, ai2)
        self.timeout = 60*8
        self.win_stats = defaultdict(int)
        self.timeout_stats = defaultdict(int)
        self.color_name = {1:'(B)', 2:'(W)'}
        self.move_counts = list()
        self.games_played = 0
        
    def print_summary(self, fh=None):
        for name in self.ai:
            print(name[3:-8], file=fh)
            print('total wins:', self.win_stats[name], file=fh)
            print('win %     :', round(self.win_stats[name]*100.0/self.games_played, 2), file=fh)
            print('timeouts  :', self.timeout_stats[name])
            print(file=fh)
        print('Tie Game', file=fh)
        print('total wins:', self.win_stats['Tie Game'], file=fh)
        print('win %     :', round(self.win_stats['Tie Game']*100.0/self.games_played, 2), file=fh)
        print(file=fh)
        print('avg moves :', sum(self.move_counts)/len(self.move_counts), file=fh)

    def run(self, iterations, fh=None):
        '''
        Simulates {iterations} numbers of games between the two AI's.
        Switches players every game.
        Prints the results of all games at the end.
        '''
        if iterations <= 1:
            iterations = 1
        elif iterations % 2 == 1:
            iterations += 1            
        
        for i in range(iterations):
            if self.games_played != 0:
                print('\n****************************************************************************************', file=fh)
                self.print_summary(fh)

            print('****************************************************************************************', file=fh)
            print('Game #', i+1, '/', iterations, file=fh)
            print('****************************************************************************************\n', file=fh)
            self.ai_list = []
            self.ai_list.append(IOAI(self.col, self.row, self.p, ai_path=self.ai[0], time=self.timeout))
            self.ai_list.append(IOAI(self.col, self.row, self.p, ai_path=self.ai[1], time=self.timeout))
            self.win_stats[self.gameloop(fh)] += 1 
            self.games_played += 1
            self.ai = (self.ai[1], self.ai[0])

        print('**********************', file=fh)
        print('columns   :', self.col, file=fh)
        print('rows      :', self.row, file=fh)
        print('p         :', self.p, file=fh)
        print('iterations:', self.games_played, file=fh)
        print('AI #1     :', self.ai[0], file=fh)
        print('AI #2     :', self.ai[1], file=fh)
        print('**********************', file=fh)
        self.print_summary(fh)
        print('**********************', file=fh)   

    def gameloop(self,fh=None):
        player = 1
        winPlayer = 0
        move = Move([])
        board = Board(self.col,self.row,self.p)
        board.initialize_game()
        board.show_board(fh)
        
        move_count = 0
        while True:
            move_count += 1
            print(move_count, self.color_name[player], self.ai[player-1][3:-8],'is thinking...',file=fh)
            
            try:
                move = self.ai_list[player-1].get_move(move)
            except TimeoutError:
                print(self.ai[player-1][3:-8],"timed out!",file=fh)
                self.timeout_stats[self.ai[player-1]] += 1
                if player == 1:
                    winPlayer = 2
                else:
                    winPlayer = 1
                break
            except:
                import traceback
                print(self.ai[player-1][3:-8],"crashed!",file=fh)
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
            print(self.ai[winPlayer-1][3:-8],'WINS',file=fh)

        for AI in self.ai_list:
            if type(AI) is IOAI:
                AI.close()
                
        print('move count:', move_count, file=fh)
        self.move_counts.append(move_count)
        
        if winPlayer == -1:
            return 'Tie Game'
        return self.ai[winPlayer-1]        

if __name__ == "__main__":
    # Create txt file with unique name (based on date/time) for storing results
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
    
    if len(sys.argv) == 3:      
        iterations = int(sys.argv[1])      
        filename = sys.argv[2]
        
        game = GameLogic()
        with open('data/'+filename, 'w') as f:
            game.run(iterations, f)
    else:
        game.run(iterations)
        