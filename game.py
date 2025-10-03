#ici on code les règles du jeu et l'interaction avec le joueur
from plateau import board

#cette fonction detecte si une condition de victoire est remplie et par quel joueur elle a été remplie
def check_W(board):
    for i in range(5): 
        for j in range(5):
            if board[i][j]==1:
                if i<2:
                    if(board[i+1][j]==1 and board[i+2][j]==1 and board[i+3][j]==1):
                        return 1
                if j<2:
                    if (board[i][j+1]==1 and board[i][j+2]==1 and board[i][j+3]==1):
                        return 1
                if j<2 and i<2:
                    if (board[i+1][j+1]==1 and board[i+2][j+2]==1 and board[i+3][j+3]==1):
                        return 1
                if j<4 and i<4:
                    if (board[i+1][j]==1 and board[i+1][j+1]==1 and board[i][j+1]==1):
                        return 1
            if board[i][j]==-1:
                if i<2:
                    if(board[i+1][j]==-1 and board[i+2][j]==-1 and board[i+3][j]==-1):
                        return -1
                if j<2:
                    if (board[i][j+1]==-1 and board[i][j+2]==-1 and board[i][j+3]==-1):
                        return -1
                if j<2 and i<2:
                    if (board[i+1][j+1]==-1 and board[i+2][j+2]==-1 and board[i+3][j+3]==-1):
                        return -1
                if j<4 and i<4:
                    if (board[i+1][j]==-1 and board[i+1][j+1]==-1 and board[i][j+1]==-1):
                        return -1
    return 0

#cette fonction permet au joueur p (1 ou -1) de placer un pion a la position i, j sur le plateau
def place_pion(board,i,j,p):
    if board[i][j]==0:
        board[i][j]=p
        return board
    else:
        print("mouvement non autorisé")
        return 0

#cette fonction permet au joueur p (1 ou -1) de déplacer un pion qui est a la position i,j dans une direction dir (z=haut, q=gauche,s=bas,d=droite j'avais pas de meilleure idée)
def move_pion(board,i,j,p,dir):
    if board[i][j]==p:
        if dir=="z" and i !=0:
            board[i][j]=0
            board[i-1][j]=p
        if dir=="q" and j !=0:
            board[i][j]=0
            board[i][j-1]=p
        if dir=="s" and i !=4:
            board[i][j]=0
            board[i+1][j]=p
        if dir=="d" and j !=4:
            board[i][j]=0
            board[i][j+1]=p

#etabli une liste de mouvement possible ce sera important pour l'ia
def move_possible(board,p):
    move = []
    count = 0
    for i in range (5):
        for j in range (5):
            if board[i][j]==p:
                count+=1
    if count < 4:
        for i in range (5):
            for j in range (5):
                if board[i][j]==0:
                    move.append((i,j))
        return move
    else:
        for i in range(5):
            for j in range(5):
                if board[i][j]==p:
                    if i==0 and j==0:
                        if board[i+1][j]==0:
                            move.append((i,j,"s"))
                        if board[i][j+1]==0:
                            move.append((i,j,"d"))
                    if i==0 and j==4:
                        if board[i+1][j]==0:
                            move.append((i,j,"s"))
                        if board[i][j-1]==0:
                            move.append((i,j,"q"))
                    if i==4 and j==0:
                        if board[i-1][j]==0:
                            move.append((i,j,"z"))
                        if board[i][j+1]==0:
                            move.append((i,j,"d"))
                    if i==4 and j==4:
                        if board[i-1][j]==0:
                            move.append((i,j,"z"))
                        if board[i][j-1]==0:
                            move.append((i,j,"q"))
                    if i==0 and 4>j>0:
                        if board[i+1][j]==0:
                            move.append((i,j,"s"))
                        if board[i][j+1]==0:
                            move.append((i,j,"d"))
                        if board[i][j-1]==0:
                            move.append((i,j,"q"))
                    if i==4 and 4>j>0:
                        if board[i-1][j]==0:
                            move.append((i,j,"z"))
                        if board[i][j+1]==0:
                            move.append((i,j,"d"))
                        if board[i][j-1]==0:
                            move.append((i,j,"q"))
                    if 4>i>0 and j==0:
                        if board[i+1][j]==0:
                            move.append((i,j,"s"))
                        if board[i][j+1]==0:
                            move.append((i,j,"d"))
                        if board[i-1][j]==0:
                            move.append((i,j,"z"))
                    if 4>i>0 and j==4:
                        if board[i+1][j]==0:
                            move.append((i,j,"s"))
                        if board[i-1][j]==0:
                            move.append((i,j,"z"))
                        if board[i][j-1]==0:
                            move.append((i,j,"q"))
                    if 4>i>0 and 4>j>0:
                        if board[i+1][j]==0:
                            move.append((i,j,"s"))
                        if board[i][j+1]==0:
                            move.append((i,j,"d"))
                        if board[i][j-1]==0:
                            move.append((i,j,"q"))
                        if board[i-1][j]==0:
                            move.append((i,j,"z"))
        return move

                    
                    
            


