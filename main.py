#ici on lance le programme
from game import place_pion
from game import check_W
from plateau import board
from game import move_pion
from game import move_possible
from ia import evaluer
from ia import Minmax_facile
from ia import Minmax_moyen
import copy


board = [
    [ 0,   0,  1,  0,  0],
    [ 0,   0,  1,  0,  0],
    [ 0,  -1,  0,  0,  0],
    [ 0,  -1,  0,  0,  0],
    [ 0,  -1,  0,  0,  0]
]

def print_board(b):
    for row in b:
        print(row)
    print()


# Test Minmax_facile
print("Plato avant ia")
print_board(board)

Minmax_moyen(board, 1) 

print("Plato après ia:")
print_board(board)


