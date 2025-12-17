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
from ia import Minmax_facile, Minmax_Ultime, AlphaBeta, Revert_Minmax_Ultime, Revert_AlphaBeta


# plateau partagé (main.py importe `board` depuis ici)
board = [[0 for _ in range(5)] for __ in range(5)]

# ----- Configuration graphique -----
CELL = 130
MARGIN = 40
GRID = 5
WIDTH = GRID * CELL + MARGIN * 2
HEIGHT = GRID * CELL + MARGIN * 2 + 180
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
def draw_ui(surface, difficulty, game_over, winner, font, bigfont, ia_config):
    y0 = MARGIN + GRID*CELL + 24

    info_rect = pygame.Rect(MARGIN-8, y0-8, GRID*CELL+16, HEIGHT - (y0-8) - 8)
    pygame.draw.rect(surface, PANEL, info_rect, border_radius=12)
    pygame.draw.rect(surface, LINE, info_rect, 2, border_radius=12)

    diff_label = "Humain vs IA"
    if difficulty == 3:
        diff_label = "IA vs IA"

    dtext = bigfont.render(f"{diff_label}", True, TXT)
    surface.blit(dtext, (MARGIN, y0))

    config_text = ""
    if difficulty == 3 and ia_config is not None:
        config_text = f" (IA1: {ia_config['ia1_algo']} p{ia_config['ia1_depth']} vs IA2: {ia_config['ia2_algo']} p{ia_config['ia2_depth']})"
    elif difficulty == 0:
        config_text = " (Entrainement)"
    elif difficulty == 1:
        config_text = f" (AlphaBeta p{ia_config.get('depth', 3) if ia_config else 3})"
    elif difficulty == 2:
        config_text = f" (Minmax p{ia_config.get('depth', 3) if ia_config else 3})"

    dsmall = font.render(f"Mode: {diff_label}{config_text}", True, TXT)
    surface.blit(dsmall, (MARGIN, y0 + 50))

    count_h = sum(1 for r in board for v in r if v == HUMAIN)
    count_ai = sum(1 for r in board for v in r if v == IA)
    phase = "Placement" if count_h < 4 else "Déplacement"
    t2 = font.render(f"Phase: {phase}    Vos pions: {count_h}    Pions IA: {count_ai}", True, TXT)
    surface.blit(t2, (MARGIN, y0 + 95))

    if game_over:
        if winner == HUMAIN:
            msg = "Vous avez gagné !"
        elif winner == IA:
            msg = "IA a gagné."
        else:
            msg = "Match nul"
        t3 = bigfont.render(msg + "   (Redémarrer depuis le menu)", True, TXT)
        surface.blit(t3, (MARGIN + 120, y0 + 50))

# Nouveau sous-menu pour IA vs IA
def ia_vs_ia_config_menu(screen, clock, font, bigfont):
    """Menu de configuration pour IA vs IA avec choix d'algorithme et profondeur pour chaque IA"""
    
    algo_options = ["Facile", "AlphaBeta", "Minmax", "AlphaBeta_", "Minmax_"]
    
    # Configuration par défaut
    ia1_algo_index = 1  # AlphaBeta
    ia2_algo_index = 2  # Minmax
    ia1_depth = 4
    ia2_depth = 4
    
    # Input boxes pour les profondeurs
    ia1_depth_input_box = pygame.Rect(MARGIN + 200, 220, 80, 32)
    ia2_depth_input_box = pygame.Rect(MARGIN + 200, 320, 80, 32)
    ia1_depth_text = str(ia1_depth)
    ia2_depth_text = str(ia2_depth)
    
    active_input = None  # 'ia1' ou 'ia2' ou None
    
    # Boutons pour changer les algos
    b_ia1_prev = Button((MARGIN, 180, 60, 32), "<", font)
    b_ia1_next = Button((MARGIN + 300, 180, 60, 32), ">", font)
    b_ia2_prev = Button((MARGIN, 280, 60, 32), "<", font)
    b_ia2_next = Button((MARGIN + 300, 280, 60, 32), ">", font)
    
    # Boutons d'action
    b_start = Button((MARGIN + 100, 400, 180, 46), "Lancer", font, accent=True)
    b_back = Button((MARGIN + 300, 400, 180, 46), "Retour", font)
    
    title = bigfont.render("Configuration IA vs IA", True, TXT)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if active_input == 'ia1':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        active_input = None
                    elif event.key == pygame.K_BACKSPACE:
                        ia1_depth_text = ia1_depth_text[:-1]
                    elif event.unicode.isdigit():
                        ia1_depth_text += event.unicode
                elif active_input == 'ia2':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        active_input = None
                    elif event.key == pygame.K_BACKSPACE:
                        ia2_depth_text = ia2_depth_text[:-1]
                    elif event.unicode.isdigit():
                        ia2_depth_text += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                # Gestion des input boxes
                if ia1_depth_input_box.collidepoint(pos):
                    active_input = 'ia1'
                elif ia2_depth_input_box.collidepoint(pos):
                    active_input = 'ia2'
                else:
                    active_input = None
                
                # Navigation des algos
                if b_ia1_prev.is_clicked(pos):
                    ia1_algo_index = (ia1_algo_index - 1) % len(algo_options)
                if b_ia1_next.is_clicked(pos):
                    ia1_algo_index = (ia1_algo_index + 1) % len(algo_options)
                if b_ia2_prev.is_clicked(pos):
                    ia2_algo_index = (ia2_algo_index - 1) % len(algo_options)
                if b_ia2_next.is_clicked(pos):
                    ia2_algo_index = (ia2_algo_index + 1) % len(algo_options)
                
                # Boutons d'action
                if b_start.is_clicked(pos):
                    # Valider et retourner la configuration
                    try:
                        d1 = int(ia1_depth_text) if ia1_depth_text.strip() else 3
                    except:
                        d1 = 3
                    try:
                        d2 = int(ia2_depth_text) if ia2_depth_text.strip() else 3
                    except:
                        d2 = 3
                    
                    return {
                        'ia1_algo': algo_options[ia1_algo_index],
                        'ia1_depth': d1,
                        'ia2_algo': algo_options[ia2_algo_index],
                        'ia2_depth': d2
                    }
                
                if b_back.is_clicked(pos):
                    return None  # Retour au menu principal
        
        # Rendu
        screen.fill(BG)
        screen.blit(title, (MARGIN, 40))
        
        # IA 1
        ia1_label = bigfont.render("IA 1 (commence)", True, TXT)
        screen.blit(ia1_label, (MARGIN, 120))
        
        algo1_text = font.render(f"Algorithme: {algo_options[ia1_algo_index]}", True, TXT)
        screen.blit(algo1_text, (MARGIN + 70, 188))
        b_ia1_prev.draw(screen)
        b_ia1_next.draw(screen)
        
        depth1_label = font.render("Profondeur:", True, TXT)
        screen.blit(depth1_label, (MARGIN, 228))
        color1 = (180, 220, 255) if active_input == 'ia1' else (255, 255, 255)
        pygame.draw.rect(screen, color1, ia1_depth_input_box)
        pygame.draw.rect(screen, LINE, ia1_depth_input_box, 2)
        depth1_txt = font.render(ia1_depth_text, True, (0, 0, 0))
        screen.blit(depth1_txt, (ia1_depth_input_box.x + 6, ia1_depth_input_box.y + 6))
        
        # IA 2
        ia2_label = bigfont.render("IA 2 (joue en second)", True, TXT)
        screen.blit(ia2_label, (MARGIN, 240))
        
        algo2_text = font.render(f"Algorithme: {algo_options[ia2_algo_index]}", True, TXT)
        screen.blit(algo2_text, (MARGIN + 70, 288))
        b_ia2_prev.draw(screen)
        b_ia2_next.draw(screen)
        
        depth2_label = font.render("Profondeur:", True, TXT)
        screen.blit(depth2_label, (MARGIN, 328))
        color2 = (180, 220, 255) if active_input == 'ia2' else (255, 255, 255)
        pygame.draw.rect(screen, color2, ia2_depth_input_box)
        pygame.draw.rect(screen, LINE, ia2_depth_input_box, 2)
        depth2_txt = font.render(ia2_depth_text, True, (0, 0, 0))
        screen.blit(depth2_txt, (ia2_depth_input_box.x + 6, ia2_depth_input_box.y + 6))
        
        # Note
        note = font.render("Note: Profondeur de 4 recommandées", True, (200, 180, 100))
        screen.blit(note, (MARGIN, 360))
        
        # Boutons
        b_start.draw(screen)
        b_back.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

# Le menu pour choisir la difficulté
def menu_loop(screen, clock, font, bigfont):
    title = bigfont.render("Teeko - Choisir le mode", True, TXT)
    
    # Boutons principaux 
    b_hvai = Button((MARGIN, 180, 240, 50), "Humain vs IA", font, accent=True)
    b_ia_vs_ia = Button((MARGIN+260, 180, 260, 50), "IA vs IA (configurer)", font, accent=True)

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
    input_box = pygame.Rect(MARGIN, 400, 120, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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
                
                # Gérer le clic sur l'input box en premier
                if input_box.collidepoint(pos):
                    input_active = True
                else:
                    input_active = False
                
                if b_quit.is_clicked(pos):
                    pygame.quit()
                    sys.exit()
                
                # Mode IA vs IA - ouvrir le sous-menu de configuration
                if b_ia_vs_ia.is_clicked(pos):
                    ia_config = ia_vs_ia_config_menu(screen, clock, font, bigfont)
                    if ia_config is not None:
                        # Retourner la config IA vs IA
                        return 3, ia_config, ia_config
                    # Si None, on continue dans le menu principal
                    continue
                
                # mode Humain vs IA
                if b_hvai.is_clicked(pos):
                    sub_running = True
                    sub_input_active = False
                    sub_input_text = input_text
                    sub_input_box = pygame.Rect(MARGIN, 360, 120, 32)
                    while sub_running:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if ev.type == pygame.KEYDOWN:
                                if sub_input_active:
                                    if ev.key == pygame.K_RETURN:
                                        sub_input_active = False
                                    elif ev.key == pygame.K_BACKSPACE:
                                        sub_input_text = sub_input_text[:-1]
                                    elif ev.unicode.isdigit():
                                        sub_input_text += ev.unicode
                            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                                p = pygame.mouse.get_pos()
                                
                                if sub_input_box.collidepoint(p):
                                    sub_input_active = True
                                else:
                                    sub_input_active = False
                                
                                if b_easy.is_clicked(p):
                                    return 0, 3, {'depth': 3}
                                if b_med.is_clicked(p):
                                    try:
                                        dd = int(sub_input_text) if sub_input_text.strip() != "" else depth
                                    except:
                                        dd = depth
                                    return 1, dd, {'depth': dd}
                                if b_ult.is_clicked(p):
                                    try:
                                        dd = int(sub_input_text) if sub_input_text.strip() != "" else depth
                                    except:
                                        dd = depth
                                    return 2, dd, {'depth': dd}
                        screen.fill(BG)
                        screen.blit(title, (MARGIN, 40))
                        b_easy.draw(screen)
                        b_med.draw(screen)
                        b_ult.draw(screen)
                        info = font.render("Choisissez la profondeur pour Minmax si nécessaire (3-4 sinon crash): ", True, TXT)
                        screen.blit(info, (MARGIN, 300))
                        color = (180, 220, 255) if sub_input_active else (255, 255, 255)
                        pygame.draw.rect(screen, color, sub_input_box)
                        pygame.draw.rect(screen, LINE, sub_input_box, 2)
                        txt = font.render(sub_input_text, True, (0,0,0))
                        screen.blit(txt, (sub_input_box.x+6, sub_input_box.y+6))
                        pygame.display.flip()
                        clock.tick(FPS)
                
                # clics sur sous-boutons (accessibles directement)
                if b_easy.is_clicked(pos):
                    return 0, 3, {'depth': 3}
                if b_med.is_clicked(pos):
                    try:
                        dd = int(input_text) if input_text.strip() != "" else depth
                    except:
                        dd = depth
                    return 1, dd, {'depth': dd}
                if b_ult.is_clicked(pos):
                    try:
                        dd = int(input_text) if input_text.strip() != "" else depth
                    except:
                        dd = depth
                    return 2, dd, {'depth': dd}

        # rendu menu principal
        screen.fill(BG)
        screen.blit(title, (MARGIN, 40))
        
        b_hvai.draw(screen)
        b_ia_vs_ia.draw(screen)
        
        # boutons secondaires (choix d'algo pour Humain vs IA)
        b_easy.draw(screen)
        b_med.draw(screen)
        b_ult.draw(screen)
        b_quit.draw(screen)

        info = font.render("Choisissez la profondeur pour l'IA (3-4 sinon crash): ", True, TXT)
        screen.blit(info, (MARGIN, 380))
        color = (180, 220, 255) if input_active else (255, 255, 255)
        pygame.draw.rect(screen, color, input_box)
        pygame.draw.rect(screen, LINE, input_box, 2)
        txt = font.render(input_text, True, (0,0,0))
        screen.blit(txt, (input_box.x+6, input_box.y+6))

        pygame.display.flip()
        clock.tick(FPS)

# helper pour exécuter un coup d'une IA selon son nom et profondeur
def apply_ai_move_by_name(name, board_ref, player, depth):
    if name == "Facile":
        Minmax_facile(board_ref, player)
    elif name == "AlphaBeta":
        AlphaBeta(board_ref, player, depth)
    elif name == "AlphaBeta_":
        Revert_AlphaBeta(board_ref, player, depth)
    elif name == "Minmax":
        Minmax_Ultime(board_ref, player, depth)
    elif name == "Minmax_":
        Revert_Minmax_Ultime(board_ref, player, depth)
    else:
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
        board = [[0 for _ in range(5)] for __ in range(5)]

    # sélection du menu si aucune difficulté fournie
    # MENU RETURNS: (difficulty, depth, ia_pair) where ia_pair is None unless IA vs IA chosen
    if start_difficulty is None:
        difficulty, depth_or_config, ia_config = menu_loop(screen, clock, font, bigfont)
    else:
        difficulty = start_difficulty
        depth_or_config = start_depth
        ia_config = None

    selected = None
    game_over = False
    winner = 0

    # petits boutons en haut de l'écran
    b_restart = Button((WIDTH-320, MARGIN, 90, 32), "Restart", font)
    b_menu = Button((WIDTH-210, MARGIN, 90, 32), "Menu", font)
    b_toggle_auto = Button((WIDTH-100, MARGIN, 90, 32), "Auto", font)

    # helper timing pour IA vs IA
    last_ai_time = 0
    ai_delay = 400  # ms entre coups IA

    running = True
    auto_mode = True if difficulty == 3 else False
    current_player = IA


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                if b_restart.is_clicked(pos):
                    board = [[0 for _ in range(5)] for __ in range(5)]
                    selected = None
                    game_over = False
                    winner = 0
                    auto_mode = (difficulty == 3)
                    continue
                if b_menu.is_clicked(pos):
                    difficulty, depth_or_config, ia_config = menu_loop(screen, clock, font, bigfont)
                    board = [[0 for _ in range(5)] for __ in range(5)]
                    selected = None
                    game_over = False
                    winner = 0
                    auto_mode = (difficulty == 3)
                    continue
                if b_toggle_auto.is_clicked(pos):
                    auto_mode = not auto_mode

                if game_over or auto_mode:
                    continue

                # si mode IA vs IA actif, on ignore clics sur plateau pour éviter perturbation
                if auto_mode:
                    continue

                cell = coord_from_mouse(*pos)
                if cell is None:
                    continue
                ci, cj = cell

                count_h = sum(1 for r in board for v in r if v == HUMAIN)

                if count_h < 4:
                    # phase de placement
                    if board[ci][cj] == 0:
                        res = game.place_pion(board, ci, cj, HUMAIN)
                        if res != 0:
                            if game.check_W(board):
                                game_over = True
                                winner = HUMAIN
                            else:
                                # coup de l'IA (humain vs IA)
                                if difficulty == 0:
                                    Minmax_facile(board, IA)
                                elif difficulty == 1:
                                    AlphaBeta(board, IA, depth_or_config)
                                else:
                                    Minmax_Ultime(board, IA, depth_or_config)
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
                                        AlphaBeta(board, IA, depth_or_config)
                                    else:
                                        Minmax_Ultime(board, IA, depth_or_config)
                                    if game.check_W(board):
                                        game_over = True
                                        winner = IA
                            else:
                                selected = None

        # IA vs IA automatic play
        
        if not game_over and auto_mode and difficulty == 3:
            now = pygame.time.get_ticks()
            if now - last_ai_time > ai_delay:

                if current_player == IA:
                    ai_name = ia_config['ia1_algo']
                    ai_depth = ia_config['ia1_depth']
                else:
                    ai_name = ia_config['ia2_algo']
                    ai_depth = ia_config['ia2_depth']

                apply_ai_move_by_name(ai_name, board, current_player, ai_depth)

                if game.check_W(board):
                    game_over = True
                    winner = current_player
                    print(current_player)
                else:
                    current_player *= -1   # switch turn

                last_ai_time = now


        draw_board(screen, selected)
        
        draw_ui(screen, difficulty, game_over, winner, font, bigfont, ia_config)
        b_restart.draw(screen)
        b_menu.draw(screen)
        b_toggle_auto.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
