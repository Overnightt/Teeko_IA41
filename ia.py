#ici on code la logique de l'IA
from game import place_pion
from game import check_W
from game import move_pion
from game import move_possible
import copy
from functools import lru_cache #trés important

#ici on etablie les recompense pour le controle d'un case centrale car celles ci sont plus importantes
#car plus de combinaison sont possible quand celles ci sont controlées
recompense_central =[
[1,2,3,2,1],
[2,4,6,4,2],
[3,6,10,6,2],
[2,4,6,4,2],
[1,2,3,2,1],
]
#fonction qui essaye d'evaluer qui gagne la partie, important pour la logique de l'ia

def evaluer(board,p):
    score=0
    directions=[(1,0),(0,1),(1,1),(1,-1)]
    for i in range(5):
        for j in range(5):
            if board[i][j] == p:
                score +=recompense_central[i][j]
                for di,dj in directions:
                    ni=i+di
                    nj=j+dj
                    compte=0
                    while 0<=ni<=4 and 0<=nj<=4:
                        if board[ni][nj]==p:
                            compte+=1
                            ni+=di
                            nj+=dj
                        else:
                            break
                    #en attribuant des mutiple de dix de plus en plus grand au score j'espere annuler le probleme de double comptage
                    if compte==1:
                        score+=10
                    if compte==2:
                        score+=100
                    if compte==3:
                        score+=1000
                #voici la partie qui gère les carré
            if i < 4 and j < 4:
                if board[i][j] == p and board[i+1][j] == p and board[i][j+1] == p and board[i+1][j+1] == p:
                    score+=1000
                elif  board[i][j] == p and board[i+1][j] == p and board[i][j+1] == p:
                    score+=100
                elif  board[i][j] == p and board[i+1][j] == p and board[i+1][j+1] == p:
                    score+=100
                elif  board[i][j+1] == p and board[i+1][j] == p and board[i+1][j+1] == p:
                    score+=100
                elif  board[i][j+1] == p and board[i][j] == p and board[i+1][j+1] == p:
                    score+=100
    return score


#fonction de minmax qui renvoit le plateau avec le meilleur mouvement appliqué sans se soucier des 
#mouvements possibles de l'adversaire
def Minmax_facile(board,p):
    score_max=-1000000
    meilleur_move=()
    l=move_possible(board,p)
    for i in l:
        if len(i)==2:
            new_board= copy.deepcopy(board)
            place_pion(new_board,i[0],i[1],p)
            move_actuel=evaluer(new_board,p)-evaluer(new_board,-p)
            if move_actuel>score_max:
                score_max=move_actuel
                meilleur_move=i
        elif len(i)==3:
            new_board= copy.deepcopy(board)
            move_pion(new_board,i[0],i[1],p,i[2])
            move_actuel=evaluer(new_board,p)-evaluer(new_board,-p)
            if move_actuel>score_max:
                score_max=move_actuel
                meilleur_move=i
    if len(meilleur_move)==2:
        place_pion(board,meilleur_move[0],meilleur_move[1],p)
        return board
    if len(meilleur_move)==3:
        move_pion(board,meilleur_move[0],meilleur_move[1],p,meilleur_move[2])
        return board

#fonction de minmax qui renvoit le plateau avec le meilleur mouvement appliqué mais qui cette fois ci
#après avoir effectuer un mouvement regarde le pire des cas , c'est a dire le meilleur mouvement que
#l'ennemi peut faire et note le score, le mouvement qui entraine le pire des cas avec le score le plus élevé
#c'est a dire celui qui entraine un plateau le plus a l'avantage de l'ia, sera choisi


#après avoir créer deux algorithme basique qui m'on permis de comprendre le concept du minmax j'ai eu l'idée
#j'avais envie de faire un algorithme capable de regarder le plus loin dans le futur (coups possible) possible
# dans les limites de ma machine bien sur. Afin de ne pas faire un programme avec trop de if, j'ai decidé de
#faire un programme recursif ou l'on peut choisir le nombre de coup dans le futur analysé par l'ia. Le programme
#est divisé en 2 partie, une qui s'occupe de la recursivité et l'autre de l'initialisation et de l'application
#des mouvements

#------Done--------#
@lru_cache(maxsize=None)
def Minmax_Ultime_Algo(board,p,predi):
    if predi==0 or check_W(board):
        return p*(evaluer(board,p)-evaluer(board,-p))
    else:
        score_max=-1000000
        pire_cas=1000000
        l=move_possible(board,p)
        for i in l:
            if len(i)==2:
                new_board= [list(row) for row in board]
                place_pion(new_board,i[0],i[1],p)
                usable_board=tuple(tuple(row) for row in new_board)
                score= Minmax_Ultime_Algo(usable_board,-p,predi-1)
                if score > score_max and p==1:
                    score_max=score
                if pire_cas > score and p==-1:
                    pire_cas=score
            if len(i)==3:
                new_board= [list(row) for row in board]
                move_pion(new_board,i[0],i[1],p,i[2])
                usable_board=tuple(tuple(row) for row in new_board)
                score= Minmax_Ultime_Algo(usable_board,-p,predi-1)
                if score > score_max and p==1:
                    score_max=score
                if pire_cas > score and p==-1:
                    pire_cas=score
        if p==1:
            return score_max
        if p==-1:
            return pire_cas


def Minmax_Ultime(board,p,predi):
    score_max=-1000000
    meilleur_move=()
    l=move_possible(board,p)
    for i in l:
        if len(i)==2:
            new_board= copy.deepcopy(board)
            place_pion(new_board,i[0],i[1],p)
            if check_W(new_board):  
                meilleur_move=i
                place_pion(board,i[0],i[1],p)
                return board
            usable_board=tuple(tuple(row) for row in new_board)
            score = Minmax_Ultime_Algo(usable_board,-p,predi-1)
            if score > score_max:
                score_max=score
                meilleur_move=i
        if len(i)==3:
            new_board= copy.deepcopy(board)
            move_pion(new_board,i[0],i[1],p,i[2])
            if check_W(new_board):
                meilleur_move=i
                move_pion(board,i[0],i[1],p,i[2])
                return board
            usable_board=tuple(tuple(row) for row in new_board)
            score = Minmax_Ultime_Algo(usable_board,-p,predi-1)
            if score > score_max:
                score_max=score
                meilleur_move=i
    if len(meilleur_move)==2:
        place_pion(board,meilleur_move[0],meilleur_move[1],p)
        return board
    if len(meilleur_move)==3:
        move_pion(board,meilleur_move[0],meilleur_move[1],p,meilleur_move[2])
        return board

#------WORK IN PROGRESS !--------#
def AlphaBeta(board,p,predi):
    alpha=-100000000 #equivalent a -inf
    beta=1000000000  #equivalent a +inf
    best_score= -100000000 #equivalent a -inf
    meilleur_move=() 
    l=move_possible(board,p)
    for i in l:
        n=len(i)
        if n==2:
            new_board= [list(row) for row in board]
            place_pion(new_board,i[0],i[1],p)
            usable_board=tuple(tuple(row) for row in new_board)
            score = AlphaBeta_Algo(usable_board,-p,predi-1,alpha,beta)
            if score > best_score:
                best_score = score
                meilleur_move=i
        if n==3:
            new_board= [list(row) for row in board]
            move_pion(new_board,i[0],i[1],p,i[2])
            usable_board=tuple(tuple(row) for row in new_board)
            score = AlphaBeta_Algo(usable_board,-p,predi-1,alpha,beta)
            if score > best_score:
                best_score = score
                meilleur_move=i
    if n==2:
        place_pion(board,meilleur_move[0],meilleur_move[1],p)
    if n==3:
        move_pion(board,meilleur_move[0],meilleur_move[1],p,meilleur_move[2])
    return board



def AlphaBeta_Algo(board, p, predi, alpha, beta):
    if predi == 0 or check_W(board)!=0 :
        eval_score =p*(evaluer(board,p)-evaluer(board,-p))
        return eval_score
    l = move_possible(board, p)
    if p == 1:  
        val = -100000000
        for i in l:
            n=len(i)
            if n == 2:
                new_board = [list(row) for row in board]
                place_pion(new_board, i[0], i[1], p)
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=max(score,val)
                alpha=max(alpha,val)
                if alpha >= beta:
                    return alpha    
            elif n == 3:
                new_board = [list(row) for row in board]
                move_pion(new_board, i[0], i[1], p, i[2])
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=max(score,val)
                alpha=max(alpha,val)
                if alpha >= beta:
                    return alpha
        return val
    else:  
        val = 100000000
        for i in l:
            n=len(i)
            if n == 2:
                new_board = [list(row) for row in board]
                place_pion(new_board, i[0], i[1], p)
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=min(score,val)
                beta=min(beta,val)
                if alpha >= beta:
                    return beta
            elif n == 3:
                new_board = [list(row) for row in board]
                move_pion(new_board, i[0], i[1], p, i[2])
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=min(score,val)
                beta=min(beta,val)
                if alpha >= beta:
                    return beta
        return val
