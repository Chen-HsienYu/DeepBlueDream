# DeepBlueDream
checkers bot for cs171
# StudentAI.py
print() will only work in manual mode\
\
TO LOAD CORRECT PYTHON VERSION IN OPENLAB:\
module load python/3.5.2\
\
TO MANUALLY PLAY AGAINST StudentAI:\
python3 src/checkers-python/main.py {col} {row} {p} m {start_player (0 or 1)}\
python3 src/checkers-python/main.py 7 7 2 m 0\
\
TO TEST StudentAI AGAINST Random_AI:\
python3 DeepBlueDream/src/checkers-python/main.py {row} {column} {rows occupied by pieces} l {AI_1_path} {AI_2_path}\
python3 src/checkers-python/main.py 7 7 2 l Tools/Sample_AIs/Random_AI/main.py src/checkers-python/main.py\

# statistics.py
Running statistics.py with no arguments will play one game with the default settings\
TO RUN WITH DIFFERENT SETTINGS:\
python3 DeepBlueDream/src/statistics/statistics.py {iterations}\
python3 DeepBlueDream/src/statistics/statistics.py {row} {column} {rows occupied by pieces} {iterations}\
python3 DeepBlueDream/src/statistics/statistics.py {row} {column} {rows occupied by pieces} {iterations} {AI_1_path} {AI_2_path}\

# TODO
remove moves that instantly lose the game\
add confidence level to speed up certain moves\
reuse tree after choosing move\
optimize simulation function\
time functions\
first move openings\
mix parallelization/exploitation constants\
update type annotations\
.
