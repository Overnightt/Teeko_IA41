#ici on code la logique de l'IA

#fonction qui essayer d'evaluer qui gagne la partie, important pour la logique de l'ia
def evaluer(board,p):
    #Récompenses pour alignements partiels et carrés
    #Pénalités pour les menaces de l'adversaire (blocage)
    #Bonus/malus pour la mobilité et liberté des pions
    score=0
    return score