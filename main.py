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



def print_board(b):
    for row in b:
        print(row)
    print()

def jouer_partie():
    plat0=plateau.board
    while not check_W(plat0):





