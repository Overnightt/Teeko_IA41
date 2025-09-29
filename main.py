#ici on lance le programme
from game import place_pion
from game import check_W
from plateau import board



board1 = [
    [-1, 0, 0, 0, 0],
    [-1, 0, 1, 0, 0],
    [-1, 0, 1, 0, 0],
    [-1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

place_pion(board1,4,4,1)
for row in board1:
    print(row)
