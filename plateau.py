"""
Interface graphique complète pour Teeko utilisant Pygame.
Il faut installer pygame via pip si ce n'est pas déjà fait:
    pip install pygame
"""
import pygame
import sys
import copy
import game
from ia import Minmax_facile, Minmax_moyen, Minmax_Ultime

# plateau partagé (main.py importe `board` depuis ici)
board = [[0 for _ in range(5)] for __ in range(5)]

# ----- Configuration graphique -----
CELL = 100
MARGIN = 24
GRID = 5
WIDTH = GRID * CELL + MARGIN * 2
HEIGHT = GRID * CELL + MARGIN * 2 + 140  
FPS = 30

HUMAIN = -1
IA = 1

# Couleurs
BG = (245,245,245)
LINE = (40,40,40)
HIGHLIGHT = (255,200,0)
TXT = (20,20,20)

# utilitaires
def coord_from_mouse(mx, my):
    if mx < MARGIN or my < MARGIN or mx > MARGIN + GRID*CELL or my > MARGIN + GRID*CELL:
        return None
    j = (mx - MARGIN) // CELL
    i = (my - MARGIN) // CELL
    return int(i), int(j)

def get_dir(from_i, from_j, to_i, to_j):
    if to_i == from_i - 1 and to_j == from_j:
        return 'z'
    if to_i == from_i + 1 and to_j == from_j:
        return 's'
    if to_i == from_i and to_j == from_j - 1:
        return 'q'
    if to_i == from_i and to_j == from_j + 1:
        return 'd'
    return None

# bouton simple
class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
    def draw(self, surface):
        pygame.draw.rect(surface, (220,220,220), self.rect)
        pygame.draw.rect(surface, LINE, self.rect, 2)
        txt = self.font.render(self.text, True, TXT)
        tw, th = txt.get_size()
        surface.blit(txt, (self.rect.x + (self.rect.w - tw)//2, self.rect.y + (self.rect.h - th)//2))
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# dessin du plateau
def draw_board(surface, selected):
    surface.fill(BG)
    # lignes de la grille
    for i in range(GRID+1):
        start = (MARGIN, MARGIN + i*CELL)
        end = (MARGIN + GRID*CELL, MARGIN + i*CELL)
        pygame.draw.line(surface, LINE, start, end, 2)
    for j in range(GRID+1):
        start = (MARGIN + j*CELL, MARGIN)
        end = (MARGIN + j*CELL, MARGIN + GRID*CELL)
        pygame.draw.line(surface, LINE, start, end, 2)

    # Les pions
    for i in range(GRID):
        for j in range(GRID):
            x = MARGIN + j*CELL + CELL//2
            y = MARGIN + i*CELL + CELL//2
            if board[i][j] == IA:
                pygame.draw.circle(surface, (60,120,200), (x,y), CELL//3)
            elif board[i][j] == HUMAIN:
                pygame.draw.circle(surface, (200,60,60), (x,y), CELL//3)

    # La sélection
    if selected is not None:
        i,j = selected
        rect = pygame.Rect(MARGIN + j*CELL+2, MARGIN + i*CELL+2, CELL-4, CELL-4)
        pygame.draw.rect(surface, HIGHLIGHT, rect, 4)

#La Zone UI avec boutons et informations
def draw_ui(surface, difficulty, game_over, winner, font, bigfont):
    y0 = MARGIN + GRID*CELL + 12
    # difficulté
    dtext = bigfont.render(f"Difficulté: {difficulty}  (changer depuis le menu)", True, TXT)
    surface.blit(dtext, (MARGIN, y0))
    # compteurs et phase
    count_h = sum(1 for r in board for v in r if v == HUMAIN)
    count_ai = sum(1 for r in board for v in r if v == IA)
    phase = "Placement" if count_h < 4 else "Déplacement"
    t2 = font.render(f"Phase: {phase}    Vos pions: {count_h}    Pions IA: {count_ai}", True, TXT)
    surface.blit(t2, (MARGIN, y0 + 30))

    if game_over:
        if winner == HUMAIN:
            res = "Vous avez gagné !"
        elif winner == IA:
            res = "IA a gagné."
        else:
            res = "Match nul"
        t3 = bigfont.render(res + "   (Redémarrer depuis le menu)", True, TXT)
        surface.blit(t3, (MARGIN, y0 + 60))

# Le menu pour choisir la difficulté

def menu_loop(screen, clock, font, bigfont):
    title = bigfont.render("Teeko - Choisir la difficulté", True, TXT)
    b_easy = Button((MARGIN, 150, 160, 40), "Facile (0)", font)
    b_med = Button((MARGIN+180, 150, 160, 40), "Moyen (1)", font)
    b_ult = Button((MARGIN+360, 150, 160, 40), "Ultime (2)", font)
    b_quit = Button((MARGIN+180, 220, 160, 40), "Quitter", font)

    # sélection de la profondeur pour Ultime
    depth = 3
    input_active = False
    input_text = str(depth)
    input_box = pygame.Rect(MARGIN, 330, 120, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if b_easy.is_clicked(pos):
                    return 0, 3
                if b_med.is_clicked(pos):
                    return 1, 3
                if b_ult.is_clicked(pos):
                    # lire la profondeur courante depuis input_text (sinon utiliser 3)
                    try:
                        dd = int(input_text) if input_text.strip() != "" else depth
                    except:
                        dd = depth
                    return 2, dd
                if b_quit.is_clicked(pos):
                    pygame.quit(); sys.exit()
                # cliquer sur la zone d'entrée active/désactive input_active
                if input_box.collidepoint(pos):
                    input_active = True
                else:
                    input_active = False


        screen.fill(BG)
        screen.blit(title, (MARGIN, 40))
        b_easy.draw(screen); b_med.draw(screen); b_ult.draw(screen); b_quit.draw(screen)

        info = font.render("Choisissez le profondeur pour Ultime (3-4 sinon crash): ", True, TXT) 
        screen.blit(info, (MARGIN, 300)) 
        box = pygame.Rect(MARGIN, 330, 120, 32) 
        pygame.draw.rect(screen, (255,255,255), box) 
        pygame.draw.rect(screen, LINE, box, 2) 
        txt = font.render(input_text, True, TXT) 
        screen.blit(txt, (box.x+6, box.y+6))
        
        pygame.display.flip()
        clock.tick(FPS)


# fonction principale exposée pour lancer le plateau
def lancer_plateau(start_board=None, start_difficulty=None, start_depth=3):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Teeko - Graphique")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    bigfont = pygame.font.SysFont(None, 30)

    global board
    if start_board is not None:
        board = start_board
    else:
        # réinitialiser le plateau global
        board = [[0 for _ in range(5)] for __ in range(5)]

    # sélection du menu si aucune difficulté fournie
    if start_difficulty is None:
        difficulty, depth = menu_loop(screen, clock, font, bigfont)
    else:
        difficulty = start_difficulty
        depth = start_depth

    selected = None
    game_over = False
    winner = 0

    # petits boutons en haut de l'écran
    b_restart = Button((WIDTH-200, MARGIN, 90, 32), "Restart", font)
    b_menu = Button((WIDTH-100, MARGIN, 90, 32), "Menu", font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                # clics sur les boutons
                if b_restart.is_clicked(pos):
                    board = [[0 for _ in range(5)] for __ in range(5)]
                    selected = None
                    game_over = False
                    winner = 0
                    continue
                if b_menu.is_clicked(pos):
                    # retour au menu
                    difficulty, depth = menu_loop(screen, clock, font, bigfont)
                    board = [[0 for _ in range(5)] for __ in range(5)]
                    selected = None
                    game_over = False
                    winner = 0
                    continue

                if game_over:
                    continue

                cell = coord_from_mouse(*pos)
                if cell is None:
                    continue
                ci, cj = cell

                # compter les pions humains pour déterminer la phase
                count_h = sum(1 for r in board for v in r if v == HUMAIN)

                if count_h < 4:
                    # phase de placement
                    if board[ci][cj] == 0:
                        res = game.place_pion(board, ci, cj, HUMAIN)
                        if res == 0:
                            # placement invalide (ne devrait pas arriver)
                            pass
                        else:
                            if game.check_W(board):
                                game_over = True
                                winner = HUMAIN
                            else:
                                # coup de l'IA
                                if difficulty == 0:
                                    Minmax_facile(board, IA)
                                elif difficulty == 1:
                                    Minmax_moyen(board, IA)
                                else:
                                    Minmax_Ultime(board, IA, depth)
                                if game.check_W(board):
                                    game_over = True
                                    winner = IA
                else:
                    # phase de déplacement
                    if selected is None:
                        if board[ci][cj] == HUMAIN:
                            selected = (ci,cj)
                    else:
                        si,sj = selected
                        if (si,sj) == (ci,cj):
                            selected = None
                        elif board[ci][cj] == 0:
                            dirc = get_dir(si,sj,ci,cj)
                            if dirc is not None:
                                game.move_pion(board, si, sj, HUMAIN, dirc)
                                selected = None
                                if game.check_W(board):
                                    game_over = True
                                    winner = HUMAIN
                                else:
                                    if difficulty == 0:
                                        Minmax_facile(board, IA)
                                    elif difficulty == 1:
                                        Minmax_moyen(board, IA)
                                    else:
                                        Minmax_Ultime(board, IA, depth)
                                    if game.check_W(board):
                                        game_over = True
                                        winner = IA
                            else:
                                # coup invalide (non adjacent)
                                selected = None

        draw_board(screen, selected)
        draw_ui(screen, difficulty, game_over, winner, font, bigfont)
        b_restart.draw(screen); b_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()