"""
Interface graphique complète pour Teeko utilisant Pygame.
Il faut installer pygame via pip si ce n'est pas déjà fait:
    pip install pygame
"""
import pygame
import sys
import copy
import time
import game
from ia import Minmax_facile, Minmax_Ultime, AlphaBeta,Revert_Minmax_Ultime,Revert_AlphaBeta

# plateau partagé (main.py importe `board` depuis ici)
board = [[0 for _ in range(5)] for __ in range(5)]

# ----- Configuration graphique -----
CELL = 130      # ← agrandi
MARGIN = 40     # ← agrandi
GRID = 5
WIDTH = GRID * CELL + MARGIN * 2
HEIGHT = GRID * CELL + MARGIN * 2 + 180   # ← espace UI plus grand
FPS = 30

HUMAIN = -1
IA = 1

# Couleurs (style jeu vidéo : ombres, contrastes)
BG = (28, 30, 34)
PANEL = (38, 41, 46)
LINE = (70, 75, 82)
HIGHLIGHT = (255, 200, 60)
TXT = (230, 230, 230)
BTN_BASE = (60, 65, 75)
BTN_ACCENT = (90, 160, 255)

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

# bouton simple (amélioré visuellement)
class Button:
    def __init__(self, rect, text, font, accent=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.accent = accent
    def draw(self, surface):
        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        shadow.fill((0,0,0,100))
        surface.blit(shadow, (self.rect.x+4, self.rect.y+4))

        color = BTN_ACCENT if self.accent else BTN_BASE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, LINE, self.rect, 2, border_radius=8)

        txt = self.font.render(self.text, True, TXT)
        tw, th = txt.get_size()
        surface.blit(txt, (self.rect.x + (self.rect.w - tw)//2, self.rect.y + (self.rect.h - th)//2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# dessin du plateau
def draw_board(surface, selected):
    surface.fill(BG)
    panel_rect = pygame.Rect(MARGIN-8, MARGIN-8, GRID*CELL+16, GRID*CELL+16)
    pygame.draw.rect(surface, PANEL, panel_rect, border_radius=12)

    # lignes de la grille
    for i in range(GRID+1):
        pygame.draw.line(surface, LINE,
                         (MARGIN, MARGIN + i*CELL),
                         (MARGIN + GRID*CELL, MARGIN + i*CELL),
                         2)
    for j in range(GRID+1):
        pygame.draw.line(surface, LINE,
                         (MARGIN + j*CELL, MARGIN),
                         (MARGIN + j*CELL, MARGIN + GRID*CELL),
                         2)

    # pions
    for i in range(GRID):
        for j in range(GRID):
            x = MARGIN + j*CELL + CELL//2
            y = MARGIN + i*CELL + CELL//2
            if board[i][j] == IA:
                pygame.draw.circle(surface, (0,0,0,60), (x+4,y+6), CELL//3)
                pygame.draw.circle(surface, (60,120,200), (x,y), CELL//3)
                pygame.draw.circle(surface, (20,40,60), (x,y), CELL//3, 4)
            elif board[i][j] == HUMAIN:
                pygame.draw.circle(surface, (0,0,0,60), (x+4,y+6), CELL//3)
                pygame.draw.circle(surface, (220,80,90), (x,y), CELL//3)
                pygame.draw.circle(surface, (60,20,20), (x,y), CELL//3, 4)

    # surbrillance
    if selected is not None:
        i,j = selected
        rect = pygame.Rect(MARGIN + j*CELL+10, MARGIN + i*CELL+10, CELL-20, CELL-20)
        pygame.draw.rect(surface, HIGHLIGHT, rect, 5, border_radius=10)

# UI
def draw_ui(surface, difficulty, game_over, winner, font, bigfont, ia_vs_ia_pair):
    y0 = MARGIN + GRID*CELL + 24

    info_rect = pygame.Rect(MARGIN-8, y0-8, GRID*CELL+16, HEIGHT - (y0-8) - 8)
    pygame.draw.rect(surface, PANEL, info_rect, border_radius=12)
    pygame.draw.rect(surface, LINE, info_rect, 2, border_radius=12)

    diff_label = "Humain vs IA"
    if difficulty == 3:
        diff_label = "IA vs IA"

    dtext = bigfont.render(f"{diff_label}", True, TXT)
    surface.blit(dtext, (MARGIN, y0))

    pair_text = ""
    if difficulty == 3 and ia_vs_ia_pair is not None:
        pair_text = f" ({ia_vs_ia_pair[0]} vs {ia_vs_ia_pair[1]})"

    dsmall = font.render(f"Difficulté: {difficulty}{pair_text}", True, TXT)
    surface.blit(dsmall, (MARGIN, y0 + 50))  # ← espacement augmenté

    count_h = sum(1 for r in board for v in r if v == HUMAIN)
    count_ai = sum(1 for r in board for v in r if v == IA)
    phase = "Placement" if count_h < 4 else "Déplacement"
    t2 = font.render(f"Phase: {phase}    Vos pions: {count_h}    Pions IA: {count_ai}", True, TXT)
    surface.blit(t2, (MARGIN, y0 + 95))  # ← espacement augmenté

    if game_over:
        if winner == HUMAIN:
            msg = "Vous avez gagné !"
        elif winner == IA:
            msg = "IA a gagné."
        else:
            msg = "Match nul"
        t3 = bigfont.render(msg + "   (Redémarrer depuis le menu)", True, TXT)
        surface.blit(t3, (MARGIN + 120, y0 + 50))

# Le menu pour choisir la difficulté (maintenant avec IA vs IA)
def menu_loop(screen, clock, font, bigfont):
    title = bigfont.render("Teeko - Choisir le mode", True, TXT)
    # Boutons principaux 
    b_hvai = Button((MARGIN, 180, 240, 50), "Humain vs IA", font, accent=True)
    b_ia_vs_ia = Button((MARGIN+260, 180, 260, 50), "IA vs IA (changer)", font)
    # Nouveau : bouton pour LANCER IA vs IA
    b_start_ia_vs_ia = Button((MARGIN+260, 240, 260, 50), "Lancer IA vs IA", font, accent=True)

    # Ligne suivante 
    b_easy = Button((MARGIN, 320, 180, 46), "Entrainement", font)
    b_med = Button((MARGIN+200, 320, 180, 46), "Alpha Beta", font)
    b_ult = Button((MARGIN+400, 320, 180, 46), "Minmax", font)

    # Bouton quitter 
    b_quit = Button((MARGIN+200, 440, 180, 46), "Quitter", font)


    # sélection de la profondeur pour Ultime
    depth = 4
    input_active = False
    input_text = str(depth)
    input_box = pygame.Rect(MARGIN, 360, 120, 32)

    # liste de paires pour IA vs IA (cycle)
    ia_pairs = [
        ("Facile","Facile"),
        ("AlphaBeta_","AlphaBeta"),
        ("Minmax_","Minmax"),
        ("AlphaBeta_","Minmax"),
        ("Minmax_","AlphaBeta"),
    ]
    ia_pair_index = 0

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
                if b_quit.is_clicked(pos):
                    pygame.quit(); sys.exit()
                # mode Humain vs IA
                if b_hvai.is_clicked(pos):
                    # on laisse choisir l'algorithme ensuite (0,1,2)
                    # ouvrir sous-menu permettant de choisir l'algorithme
                    # pour simplifier on retourne difficulty 0/1/2 et depth
                    # on affiche donc les 3 boutons dessous et attend click
                    sub_running = True
                    while sub_running:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit(); sys.exit()
                            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                p = pygame.mouse.get_pos()
                                if b_easy.is_clicked(p):
                                    return 0, 3, None  # Entrainement
                                if b_med.is_clicked(p):
                                    try:               # AlphaBeta
                                        dd = int(input_text) if input_text.strip() != "" else depth
                                    except:
                                        dd = depth
                                    return 2, dd, None   
                                if b_ult.is_clicked(p):
                                    try:
                                        dd = int(input_text) if input_text.strip() != "" else depth
                                    except:
                                        dd = depth
                                    return 2, dd, None  # Minmax ultime
                                if input_box.collidepoint(p):
                                    input_active = True
                                else:
                                    input_active = False
                        screen.fill(BG)
                        screen.blit(title, (MARGIN, 40))
                        b_easy.draw(screen); b_med.draw(screen); b_ult.draw(screen)
                        info = font.render("Choisissez la profondeur pour Minmax si nécessaire (3-4 sinon crash): ", True, TXT)
                        screen.blit(info, (MARGIN, 300))
                        box = pygame.Rect(MARGIN, 360, 120, 32)
                        pygame.draw.rect(screen, (255,255,255), box)
                        pygame.draw.rect(screen, LINE, box, 2)
                        txt = font.render(input_text, True, (0,0,0))
                        screen.blit(txt, (box.x+6, box.y+6))
                        pygame.display.flip()
                        clock.tick(FPS)
                # mode IA vs IA : changer la paire
                if b_ia_vs_ia.is_clicked(pos):
                    ia_pair_index = (ia_pair_index + 1) % len(ia_pairs)
                # mode IA vs IA : lancer la paire courante
                if b_start_ia_vs_ia.is_clicked(pos):
                    # renvoyer difficulty=3 (IA vs IA), depth restant (3), et la paire choisie
                    return 3, 3, ia_pairs[ia_pair_index]
                # clics sur sous-boutons (faciles affichés en dessous)
                if b_easy.is_clicked(pos):
                    return 0, 3, None
                if b_med.is_clicked(pos):
                    try:
                        dd = int(input_text) if input_text.strip() != "" else depth
                    except:
                        dd = depth
                    return 2, dd, None
                if b_ult.is_clicked(pos):
                    try:
                        dd = int(input_text) if input_text.strip() != "" else depth
                    except:
                        dd = depth
                    return 2, dd, None

                # clic sur la zone d'entrée active/désactive input_active
                if input_box.collidepoint(pos):
                    input_active = True
                else:
                    input_active = False

            # autre events

        # rendu menu principal
        screen.fill(BG)
        screen.blit(title, (MARGIN, 40))
        # afficher le bouton principal et les boutons IA vs IA
        b_hvai.draw(screen)
        b_ia_vs_ia.draw(screen)
        b_start_ia_vs_ia.draw(screen)
        # montrer la paire courante
        pair_display = f"{ia_pairs[ia_pair_index][0]} vs {ia_pairs[ia_pair_index][1]}"
        pair_txt = font.render(pair_display, True, TXT)
        screen.blit(pair_txt, (MARGIN+ 70 , 260))
        # boutons secondaires (choix d'algo pour Humain vs IA)
        b_easy.draw(screen); b_med.draw(screen); b_ult.draw(screen); b_quit.draw(screen)

        info = font.render("Choisissez la profondeur pour l'IA (3-4 sinon crash): ", True, TXT)
        screen.blit(info, (MARGIN, 380))
        box = pygame.Rect(MARGIN, 400, 120, 32)
        pygame.draw.rect(screen, (255,255,255), box)
        pygame.draw.rect(screen, LINE, box, 2)
        txt = font.render(input_text, True, (0,0,0))
        screen.blit(txt, (box.x+6, box.y+6))

        pygame.display.flip()
        clock.tick(FPS)

# helper pour exécuter un coup d'une IA selon son nom
def apply_ai_move_by_name(name, board_ref, player, depth):
    # name: "Facile", "AlphaBeta", "Minmax"
    if name == "Facile":
        Minmax_facile(board_ref, player)
    elif name == "AlphaBeta":
        # AlphaBeta prend (board, p, predi)
        AlphaBeta(board_ref, player, depth)
    elif name == "AlphaBeta_":
        # AlphaBeta prend (board, p, predi)
        Revert_AlphaBeta(board_ref, player, depth)
    elif name == "Minmax":
        Minmax_Ultime(board_ref, player, depth)
    elif name == "Minmax_":
        Revert_Minmax_Ultime(board_ref, player, depth)
    else:
        # fallback
        Minmax_facile(board_ref, player)

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
    # MENU RETURNS: (difficulty, depth, ia_pair) where ia_pair is None unless IA vs IA chosen
    if start_difficulty is None:
        difficulty, depth, ia_pair = menu_loop(screen, clock, font, bigfont)
    else:
        difficulty = start_difficulty
        depth = start_depth
        ia_pair = None

    # default IA vs IA pair index (0 => Facile vs Facile)
    ia_pairs = [
        ("Facile","Facile"),
        ("AlphaBeta","AlphaBeta_"),
        ("Minmax","Minmax_"),
        ("AlphaBeta","Minmax_"),
        ("Minmax","AlphaBeta_"),
    ]
    # if menu provided an ia_pair, set the index accordingly
    try:
        ia_pair_index = ia_pairs.index(ia_pair) if ia_pair is not None else 0
    except ValueError:
        ia_pair_index = 0

    selected = None
    game_over = False
    winner = 0

    # petits boutons en haut de l'écran
    b_restart = Button((WIDTH-320, MARGIN, 90, 32), "Restart", font)
    b_menu = Button((WIDTH-210, MARGIN, 90, 32), "Menu", font)
    b_toggle_auto = Button((WIDTH-100, MARGIN, 90, 32), "Auto", font)  # pour futur usage

    # helper timing pour IA vs IA (petit délai visible)
    last_ai_time = 0
    ai_delay = 400  # ms entre coups IA (visible)

    running = True
    # si le jeu est lancé directement en IA vs IA (difficulty == 3), activer auto mode
    auto_mode = True if difficulty == 3 else False

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
                    auto_mode = (difficulty == 3)
                    continue
                if b_menu.is_clicked(pos):
                    # retour au menu
                    difficulty, depth, ia_pair = menu_loop(screen, clock, font, bigfont)
                    board = [[0 for _ in range(5)] for __ in range(5)]
                    selected = None
                    game_over = False
                    winner = 0
                    auto_mode = (difficulty == 3)
                    # update chosen ia_pair index if any
                    try:
                        ia_pair_index = ia_pairs.index(ia_pair) if ia_pair is not None else 0
                    except ValueError:
                        ia_pair_index = 0
                    continue
                # toggle auto (non critique)
                if b_toggle_auto.is_clicked(pos):
                    auto_mode = not auto_mode

                if game_over:
                    continue

                # si mode IA vs IA actif, on ignore clics sur plateau pour éviter perturbation
                if auto_mode:
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
                                # coup de l'IA (humain vs IA)
                                if difficulty == 0:
                                    Minmax_facile(board, IA)
                                elif difficulty == 1:
                                    AlphaBeta(board, IA, depth)
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
                                        AlphaBeta(board, IA, depth)
                                    else:
                                        Minmax_Ultime(board, IA, depth)
                                    if game.check_W(board):
                                        game_over = True
                                        winner = IA
                            else:
                                # coup invalide (non adjacent)
                                selected = None

        # IA vs IA automatic play
        if not game_over and auto_mode:
            now = pygame.time.get_ticks()
            # on impose un délai pour que l'utilisateur voie les coups
            if now - last_ai_time > ai_delay:
                occupied = sum(1 for r in board for v in r if v != 0)
                
                if occupied % 2 == 0:
                    current_player = IA  
                    ai_name = ia_pairs[ia_pair_index][0]
                else:
                    current_player = -1  
                    ai_name = ia_pairs[ia_pair_index][1]

                if ai_name == "Facile":
                    Minmax_facile(board, current_player)
                elif ai_name == "AlphaBeta":
                    AlphaBeta(board, current_player, depth)
                elif ai_name == "AlphaBeta_":
                    Revert_AlphaBeta(board, current_player, depth)
                elif ai_name == "Minmax":
                    Minmax_Ultime(board, current_player, depth)
                elif ai_name == "Minmax_":
                    Revert_Minmax_Ultime(board, current_player, depth)
                else:
                    Minmax_facile(board, current_player)

                # vérifier victoire
                if game.check_W(board):
                    game_over = True
                    # déterminer gagnant dernier joué = current_player
                    winner = current_player
                last_ai_time = now

        draw_board(screen, selected)
        
        draw_ui(screen, difficulty, game_over, winner, font, bigfont,
                ia_pairs[ia_pair_index] if difficulty == 3 else None)
        b_restart.draw(screen); b_menu.draw(screen); b_toggle_auto.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()