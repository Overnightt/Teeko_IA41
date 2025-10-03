#ici on lance le programme
from game import place_pion
from game import check_W
from plateau import board
from game import move_pion
from game import move_possible
from ia import evaluer
from ia import Minmax_facile
import copy


board = [
    [ 0,  0,  0,  0,  -1],
    [ 0,  0,  0,  1,  0],
    [ 0,  -1,  0,  1,  0],
    [ 0, -1,  0,  1,  0],
    [ 0,  -1,  0,  0,  1]
]

# Print the board nicely
def print_board(b):
    for row in b:
        print(row)
    print()

# Test evaluation
print("Evaluation for player 1:", evaluer(board, 1))
print("Evaluation for player -1:", evaluer(board, -1))

# Test Minmax_facile
print("Board before Minmax_facile:")
print_board(board)

Minmax_facile(board, 1)  # directly modifies 'board'

print("Board after Minmax_facile (player 1):")
print_board(board)


