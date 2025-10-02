#ici on lance le programme
from game import place_pion
from game import check_W
from plateau import board
from game import move_pion
from game import move_possible
from ia import evaluer

board = [
    [ 0,  0,  0,  0,  0],
    [ 0,  0,  1,  0,  0],
    [ 0,  0,  1,  1,  0],
    [ 0, -1,  0,  0,  1],
    [ 0,  0,  0,  0,  0]
]

print(evaluer(board, 1))


