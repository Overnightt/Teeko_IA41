#ici on lance le programme
from game import check_W
from plateau import board



board1 = [
    [-1, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0],
    [-1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

print(check_W(board1))  