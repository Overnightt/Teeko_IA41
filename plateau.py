"""
Interface graphique complète pour Teeko utilisant Pygame.
Il faut installer pygame via pip si ce n'est pas déjà fait:
    pip install pygame
"""
import pygame
import sys
import game
from ia import Minmax_facile, Minmax_Ultime, AlphaBeta,Revert_Minmax_Ultime

# plateau partagé
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

# Couleurs
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

# bouton
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
    for i in range(GRID+1):
        pygame.draw.line(surface, LINE, (MARGIN, MARGIN + i*CELL), (MARGIN + GRID*CELL, MARGIN + i*CELL), 2)
    for j in range(GRID+1):
        pygame.draw.line(surface, LINE, (MARGIN + j*CELL, MARGIN), (MARGIN + j*CELL, MARGIN + GRID*CELL), 2)
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
    diff_label = "Humain vs IA" if difficulty != 3 else "IA vs IA"
    dtext = bigfont.render(diff_label, True, TXT)
    surface.blit(dtext, (MARGIN, y0))
    pair_text = f" ({ia_vs_ia_pair[0]} vs {ia_vs_ia_pair[1]})" if ia_vs_ia_pair else ""
    dsmall = font.render(f"Difficulté: {difficulty}{pair_text}", True, TXT)
    surface.blit(dsmall, (MARGIN, y0 + 50))
    count_h = sum(1 for r in board for v in r if v == HUMAIN)
    count_ai = sum(1 for r in board for v in r if v == IA)
    phase = "Placement" if count_h < 4 else "Déplacement"
    t2 = font.render(f"Phase: {phase}    Vos pions: {count_h}    Pions IA: {count_ai}", True, TXT)
    surface.blit(t2, (MARGIN, y0 + 95))
    if game_over:
        if winner == HUMAIN: msg = "Vous avez gagné !"
        elif winner == IA: msg = "IA a gagné."
        else: msg = "Match nul"
        t3 = bigfont.render(msg + "   (Redémarrer depuis le menu)", True, TXT)
        surface.blit(t3, (MARGIN + 120, y0 + 50))

# menu
def menu_loop(screen, clock, font, bigfont):
    title = bigfont.render("Teeko - Choisir le mode", True, TXT)
    b_hvai = Button((MARGIN, 180, 240, 50), "Humain vs IA", font, accent=True)
    b_ia_vs_ia = Button((MARGIN+260, 180, 260, 50), "IA vs IA (changer)", font)
    b_start_ia_vs_ia = Button((MARGIN+260, 240, 260, 50), "Lancer IA vs IA", font, accent=True)
    b_easy = Button((MARGIN, 320, 180, 46), "Entrainement", font)
    b_med = Button((MARGIN+200, 320, 180, 46), "Alpha Beta", font)
    b_ult = Button((MARGIN+400, 320, 180, 46), "Minmax", font)
    b_quit = Button((MARGIN+200, 440, 180, 46), "Quitter", font)

    depth = 3
    input_active = False
    input_text = str(depth)
    input_box = pygame.Rect(MARGIN, 400, 120, 32)

    ia_pairs = [("Facile","Facile"), ("AlphaBeta","AlphaBeta"), ("Minmax","Minmax"),
                ("AlphaBeta","Minmax"), ("Minmax","AlphaBeta")]
    ia_pair_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN: input_active=False
                elif event.key == pygame.K_BACKSPACE: input_text=input_text[:-1]
                elif event.unicode.isdigit(): input_text+=event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if b_quit.is_clicked(pos): pygame.quit(); sys.exit()
                if b_hvai.is_clicked(pos):
                    sub_running = True
                    while sub_running:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button ==1:
                                p = pygame.mouse.get_pos()
                                if b_easy.is_clicked(p): return 0,3,None
                                if b_med.is_clicked(p): return 1,3,None
                                if b_ult.is_clicked(p):
                                    try: dd=int(input_text) if input_text.strip()!="" else depth
                                    except: dd=depth
                                    return 2,dd,None
                                input_active = input_box.collidepoint(p)
                        screen.fill(BG)
                        screen.blit(title, (MARGIN,40))
                        b_easy.draw(screen); b_med.draw(screen); b_ult.draw(screen)
                        info = font.render("Profondeur Minmax: ", True, TXT)
                        screen.blit(info, (MARGIN, 300))
                        pygame.draw.rect(screen, (255,255,255), input_box)
                        pygame.draw.rect(screen, LINE, input_box,2)
                        screen.blit(font.render(input_text, True,(0,0,0)), (input_box.x+6,input_box.y+6))
                        pygame.display.flip()
                        clock.tick(FPS)
                if b_ia_vs_ia.is_clicked(pos):
                    ia_pair_index = (ia_pair_index+1)%len(ia_pairs)
                if b_start_ia_vs_ia.is_clicked(pos):
                    return 3,3,ia_pairs[ia_pair_index]
                if b_easy.is_clicked(pos): return 0,3,None
                if b_med.is_clicked(pos): return 1,3,None
                if b_ult.is_clicked(pos):
                    try: dd=int(input_text) if input_text.strip()!="" else depth
                    except: dd=depth
                    return 2,dd,None
                input_active = input_box.collidepoint(pos)

        screen.fill(BG)
        screen.blit(title,(MARGIN,40))
        b_hvai.draw(screen); b_ia_vs_ia.draw(screen); b_start_ia_vs_ia.draw(screen)
        pair_display = f"{ia_pairs[ia_pair_index][0]} vs {ia_pairs[ia_pair_index][1]}"
        screen.blit(font.render(pair_display,True,TXT),(MARGIN+70,260))
        b_easy.draw(screen); b_med.draw(screen); b_ult.draw(screen); b_quit.draw(screen)
        info = font.render("Profondeur Minmax: ", True, TXT)
        screen.blit(info,(MARGIN,380))
        pygame.draw.rect(screen,(255,255,255), input_box)
        pygame.draw.rect(screen,LINE,input_box,2)
        screen.blit(font.render(input_text,True,(0,0,0)), (input_box.x+6,input_box.y+6))
        pygame.display.flip()
        clock.tick(FPS)

# helper IA
def apply_ai_move_by_name(name, board_ref, player, depth):
<<<<<<< HEAD
    # name: "Facile", "AlphaBeta", "Minmax"
    if name == "Facile":
        Minmax_facile(board_ref, player)
    elif name == "AlphaBeta":
        # AlphaBeta prend (board, p, predi)
        AlphaBeta(board_ref, player, depth)
    elif name == "Minmax":
        Minmax_Ultime(board_ref, player, depth)
    elif name == "Minmax_":
        Revert_Minmax_Ultime(board_ref, player, depth)
    else:
        # fallback
        Minmax_facile(board_ref, player)
=======
    if name=="Facile": Minmax_facile(board_ref,player)
    elif name=="AlphaBeta": AlphaBeta(board_ref,player,depth)
    elif name=="Minmax": Minmax_Ultime(board_ref,player,depth)
    else: Minmax_facile(board_ref,player)
>>>>>>> 05362ae (On peut changer la profondeur normalement)

# fonction principale
def lancer_plateau(start_board=None,start_difficulty=None,start_depth=3):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Teeko - Graphique")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None,22)
    bigfont = pygame.font.SysFont(None,30)

    global board
    board = start_board if start_board else [[0 for _ in range(5)] for __ in range(5)]

    if start_difficulty is None:
        difficulty, depth, ia_pair = menu_loop(screen, clock, font, bigfont)
    else:
        difficulty = start_difficulty
        depth = start_depth
        ia_pair = None

<<<<<<< HEAD
    # default IA vs IA pair index (0 => Facile vs Facile)
    ia_pairs = [
        ("Facile","Facile"),
        ("AlphaBeta","AlphaBeta"),
        ("Minmax","Minmax_"),
        ("AlphaBeta","Minmax_"),
        ("Minmax","AlphaBeta"),
    ]
    # if menu provided an ia_pair, set the index accordingly
    try:
        ia_pair_index = ia_pairs.index(ia_pair) if ia_pair is not None else 0
    except ValueError:
        ia_pair_index = 0
=======
    ia_pairs = [("Facile","Facile"), ("AlphaBeta","AlphaBeta"), ("Minmax","Minmax"),
                ("AlphaBeta","Minmax"), ("Minmax","AlphaBeta")]
    try: ia_pair_index = ia_pairs.index(ia_pair) if ia_pair else 0
    except ValueError: ia_pair_index=0
>>>>>>> 05362ae (On peut changer la profondeur normalement)

    selected = None
    game_over=False
    winner=0

    b_restart = Button((WIDTH-320,MARGIN,90,32),"Restart",font)
    b_menu = Button((WIDTH-210,MARGIN,90,32),"Menu",font)
    b_toggle_auto = Button((WIDTH-100,MARGIN,90,32),"Auto",font)

    last_ai_time=0
    ai_delay=400

    auto_mode = True if difficulty==3 else False

    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); return
            elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                pos=pygame.mouse.get_pos()
                if b_restart.is_clicked(pos):
                    board=[[0]*5 for _ in range(5)]
                    selected=None
                    game_over=False
                    winner=0
                    auto_mode=(difficulty==3)
                    continue
                if b_menu.is_clicked(pos):
                    difficulty, depth, ia_pair = menu_loop(screen, clock, font, bigfont)
                    board=[[0]*5 for _ in range(5)]
                    selected=None
                    game_over=False
                    winner=0
                    auto_mode=(difficulty==3)
                    try: ia_pair_index = ia_pairs.index(ia_pair) if ia_pair else 0
                    except ValueError: ia_pair_index=0
                    continue
                if b_toggle_auto.is_clicked(pos): auto_mode=not auto_mode
                if game_over: continue
                if auto_mode: continue
                cell=coord_from_mouse(*pos)
                if cell is None: continue
                ci,cj=cell
                count_h = sum(1 for r in board for v in r if v==HUMAIN)
                if count_h<4:
                    if board[ci][cj]==0:
                        game.place_pion(board,ci,cj,HUMAIN)
                        if game.check_W(board): game_over=True; winner=HUMAIN
                        else:
                            if difficulty==0: Minmax_facile(board,IA)
                            elif difficulty==1: AlphaBeta(board,IA,depth)
                            else: Minmax_Ultime(board,IA,depth)
                            if game.check_W(board): game_over=True; winner=IA
                else:
                    if selected is None and board[ci][cj]==HUMAIN: selected=(ci,cj)
                    elif selected:
                        si,sj=selected
                        if (si,sj)==(ci,cj): selected=None
                        elif board[ci][cj]==0:
                            dirc=get_dir(si,sj,ci,cj)
                            if dirc:
                                game.move_pion(board,si,sj,HUMAIN,dirc)
                                selected=None
                                if game.check_W(board): game_over=True; winner=HUMAIN
                                else:
                                    if difficulty==0: Minmax_facile(board,IA)
                                    elif difficulty==1: AlphaBeta(board,IA,depth)
                                    else: Minmax_Ultime(board,IA,depth)
                                    if game.check_W(board): game_over=True; winner=IA
                            else: selected=None

        # IA vs IA auto
        if not game_over and auto_mode:
<<<<<<< HEAD
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
=======
            now=pygame.time.get_ticks()
            if now-last_ai_time>ai_delay:
                occupied=sum(1 for r in board for v in r if v!=0)
                if occupied%2==0: current_player=IA; ai_name=ia_pairs[ia_pair_index][0]
                else: current_player=HUMAIN; ai_name=ia_pairs[ia_pair_index][1]
                apply_ai_move_by_name(ai_name, board, current_player, depth)
                if game.check_W(board): game_over=True; winner=current_player
                last_ai_time=now
>>>>>>> 05362ae (On peut changer la profondeur normalement)

        draw_board(screen, selected)
        draw_ui(screen,difficulty,game_over,winner,font,bigfont,ia_pairs[ia_pair_index] if difficulty==3 else None)
        b_restart.draw(screen); b_menu.draw(screen); b_toggle_auto.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
