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
[1,2,1,2,1],
[2,3,3,3,2],
[1,3,4,3,1],
[2,3,3,3,2],
[1,2,1,2,1],
]


#fonction qui evalue le score du joueur p dans la partie, important pour la logique de l'ia
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

                
            if i < 4 and j < 4: #voici la partie qui gère les carré
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

#------MinMax--------#

#après avoir créer un algorithme basique qui m'a permis de comprendre le concept du minmax 
#j'avais envie de faire un algorithme capable de regarder le plus loin dans le futur (coups possible) possible
# dans les limites de ma machine bien sur. Afin de ne pas faire un programme avec trop de if, j'ai decidé de
#faire un programme recursif ou l'on peut choisir le nombre de coup dans le futur analysé par l'ia. Le programme
#est divisé en 2 partie, une qui s'occupe de la recursivité et l'autre de l'initialisation et de l'application
#des mouvements. J'ai utilisé Memoize afin de rendre l'algorithme encore plus performant et le permettre de passer de 4
# à 5 appel recursif maximum

@lru_cache(maxsize=None)
def Minmax_Ultime_Algo(board,p,predi):
    if predi==0 or check_W(board)!=0:     #si on arrive a la fin de la recursion ou sur un plateau entrainant la victoire on s'arrete
        return p*(evaluer(board,p)-evaluer(board,-p))
    else:
        score_max=-1000000   #equivalent a -inf
        pire_cas=1000000     #equivalent a +inf
        l=move_possible(board,p)

        for i in l:               #on parcours la liste des mouvements possible 
            n=len(i)
            
            if n==2:                            #si on est dans la phase de placement on procède ainsi
                new_board= [list(row) for row in board]
                place_pion(new_board,i[0],i[1],p)
                usable_board=tuple(tuple(row) for row in new_board)
                score= Minmax_Ultime_Algo(usable_board,-p,predi-1)
           
            if n==3:                              #si on est dans la phase de mouvement on procède ainsi
                new_board= [list(row) for row in board]
                move_pion(new_board,i[0],i[1],p,i[2])
                usable_board=tuple(tuple(row) for row in new_board)
                score= Minmax_Ultime_Algo(usable_board,-p,predi-1)
            
            if score > score_max and p==1:         #on choisi le meilleur score a renvoyer si on maximise (si l'ia joue)
                score_max=score    
            if pire_cas > score and p==-1:         #on choisi le meilleur score que l'adversaire peu faire si on minimise
                pire_cas=score
        
        if p==1:                                   #on renvoi les scores
            return score_max
        if p==-1:
            return pire_cas


def Minmax_Ultime(board,p,predi):
    score_max=-1000000  #equivalent a -inf, on utilise uniquement score max car on apelle cette fonction uniquement pour maximiser le score
    meilleur_move=()
    l=move_possible(board,p)

    for i in l:        #on parcours la liste des mouvements possible 
        n=len(i)

        if n==2:                            #si on est dans la phase de placement on procède ainsi
            new_board= copy.deepcopy(board)
            place_pion(new_board,i[0],i[1],p)
            if check_W(new_board):          #Si le coup entraine la victoire, on l'applique immédiatement
                meilleur_move=i
                place_pion(board,i[0],i[1],p)
                return board
            usable_board=tuple(tuple(row) for row in new_board)
            score = Minmax_Ultime_Algo(usable_board,-p,predi-1)

        if n==3:                            #si on est dans la phase de mouvement on procède ainsi
            new_board= copy.deepcopy(board)
            move_pion(new_board,i[0],i[1],p,i[2])
            if check_W(new_board):          #Si le coup entraine la victoire, on l'applique immédiatement
                meilleur_move=i
                move_pion(board,i[0],i[1],p,i[2])
                return board
            usable_board=tuple(tuple(row) for row in new_board)
            score = Minmax_Ultime_Algo(usable_board,-p,predi-1)

        if score > score_max:        #on selection le meilleur coup
            score_max=score
            meilleur_move=i

    if len(meilleur_move)==2:                     #Applique le meilleur coup
        place_pion(board,meilleur_move[0],meilleur_move[1],p)
        return board
    if len(meilleur_move)==3:
        move_pion(board,meilleur_move[0],meilleur_move[1],p,meilleur_move[2])
        return board

#------Alpha Beta--------#

#Algorithme basé sur Minmax. L'élegage AlphaBeta permet de faire monter la profondeur à 6 (pas raport a 5 pour MinMax)

def AlphaBeta(board,p,predi):
    alpha=-100000000 #equivalent a -inf
    beta=1000000000  #equivalent a +inf
    best_score= -100000000 #equivalent a -inf
    meilleur_move=() 
    l=move_possible(board,p)

    for i in l:        #on parcours la liste des mouvements possible 
        n=len(i)

        if n==2:                       #si on est dans la phase de placement on procède ainsi
            new_board= [list(row) for row in board]
            place_pion(new_board,i[0],i[1],p)
            usable_board=tuple(tuple(row) for row in new_board)
            score = AlphaBeta_Algo(usable_board,-p,predi-1,alpha,beta)

        if n==3:                      #si on est dans la phase de mouvement on procède ainsi
            new_board= [list(row) for row in board]
            move_pion(new_board,i[0],i[1],p,i[2])
            usable_board=tuple(tuple(row) for row in new_board)
            score = AlphaBeta_Algo(usable_board,-p,predi-1,alpha,beta)

        if score > best_score:      #on selection le meilleur coup
            best_score = score
            meilleur_move=i

    if n==2:                        #Applique le meilleur coup#                          
        place_pion(board,meilleur_move[0],meilleur_move[1],p)
    if n==3:
        move_pion(board,meilleur_move[0],meilleur_move[1],p,meilleur_move[2])
    return board


@lru_cache(maxsize=None)
def AlphaBeta_Algo(board, p, predi, alpha, beta):
    if predi == 0 or check_W(board)!=0 :       #si on arrive a la fin de la recursion ou sur un plateau entrainant la victoire on s'arrete
        eval_score =p*(evaluer(board,p)-evaluer(board,-p))
        return eval_score
    
    l = move_possible(board, p)

    if p == 1:                      #Cas ou on maximise
        val = -100000000            #equivalent a -inf
        for i in l:                 #on parcours la liste des mouvements possible
            n=len(i)

            if n == 2:              #si on est dans la phase de placement on procède ainsi
                new_board = [list(row) for row in board]
                place_pion(new_board, i[0], i[1], p)
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=max(score,val)

            elif n == 3:            #si on est dans la phase de mouvement on procède ainsi
                new_board = [list(row) for row in board]
                move_pion(new_board, i[0], i[1], p, i[2])
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=max(score,val)
                
            if val >= beta:         #elagage alphabeta
                return val
            alpha=max(alpha,val)    #on redefinit la valeur de alpha si besoin

        return val                  #on renvoit le score

    else:                           #Cas ou on minimise
        val = 100000000             #equivalent a +inf
        for i in l:                 #on parcours la liste des mouvements possible
            n=len(i)

            if n == 2:              #si on est dans la phase de placement on procède ainsi
                new_board = [list(row) for row in board]
                place_pion(new_board, i[0], i[1], p)
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=min(score,val)

            elif n == 3:            #si on est dans la phase de mouvement on procède ainsi
                new_board = [list(row) for row in board]
                move_pion(new_board, i[0], i[1], p, i[2])
                usable_board = tuple(tuple(row) for row in new_board)
                score = AlphaBeta_Algo(usable_board, -p, predi-1, alpha, beta)
                val=min(score,val)
                
            if val <= alpha:        #elagage alphabeta
                return val
            beta=min(beta,val)      #on redefinit la valeur de beta si besoin
        
        return val            #on renvoit le score
