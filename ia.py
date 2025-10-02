#ici on code la logique de l'IA

#fonction qui essayer d'evaluer qui gagne la partie, important pour la logique de l'ia
def evaluer(board,p):
    #Pénalités pour les menaces de l'adversaire (blocage)
    score=0
    #a partir de ce moment je me suis rendu compte que les if alait etre ineficace et allait entrainé des problèmes de double comptage, je suis donc passé au vecteur
    directions=[(1,0),(0,1),(1,1),(1,-1)]
    for i in range(5):
        for j in range(5):
            if board[i][j] == p:
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