#ici on lance le programme
from game import place_pion
from game import check_W
from plateau import board
from game import move_pion



board1 = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

move_pion(board1,1,4,1,"d")
for row in board1:
    print(row)
