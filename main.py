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
    plat0= board
    dif=int(input("veullez choisir votre dificulté (0:trés facile 1:moyen):"))
    while not check_W(plat0):
        humain=-1
        ia=1
        print_board(plat0)
        count=0
        for i in range(5):
            for j in range(5):
                if plat0[i][j]==-1:
                    count+=1
        if count < 4:
            x=5
            y=5
            while not(0<=x<=4 and 0<=y<=4):
                print("Ou voulez vous placer votre pion \n")
                x=int(input("Lignes (0-4) :"))
                y=int(input("Colonnes (0-4) :"))
                place_pion(plat0,x,y,humain)
                if dif == 0:
                    Minmax_facile(plat0,ia)
                if dif == 1:
                    Minmax_moyen(plat0,ia)



jouer_partie()






