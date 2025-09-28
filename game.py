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