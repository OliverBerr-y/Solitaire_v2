from os import path

import pygame as pg
from pygame.locals import *

from dealer import Dealer, TABLEAU, STOCK, \
    FOUNDATION, CURRENT_STOCK, T_COLS, T_ROWS

# --------------------------------------------------- CONSTANTS ----------------------------------------------------
WINDOW_CAPTION = 'Solitaire'
COLOR_BG2 = '#007000'
COLOR_BG = '#008000'
T_COLOR = '#EEFFEE'
FONT = 'COURIER'

WIN_WIDTH = 543
WIN_HEIGHT = 470
CARD_WIDTH = 63
CARD_HEIGHT = 90
STACK_LIMIT = 5
TEXT_SIZE = 17
LEFT_MARGIN = 30
TOP_MARGIN = 40

pg.init()
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption(WINDOW_CAPTION)
LB = pg.font.SysFont(FONT, TEXT_SIZE)

# Board Areas
AREA_CURRENT_STOCK = pg.Rect(380, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
AREA_STOCK = pg.Rect(450, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
AREA_WASTE = pg.Rect(379, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
AREA_TABLEAU = pg.Rect(LEFT_MARGIN, 150, 483, 300)
AREA_FOUNDATION = pg.Rect(0, 0, 350, 150)
AREA_SOUND = pg.Rect(520, 448, 15, 15)
AREA_MOVES_LB = (150, 12, 50, 50)

# Foundation positions
T4 = pg.Rect(LEFT_MARGIN + (70 * 3), TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
T3 = pg.Rect(LEFT_MARGIN + (70 * 2), TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
T2 = pg.Rect(LEFT_MARGIN + 70, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
T1 = pg.Rect(LEFT_MARGIN, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)

# Button images
BTN_AUTO = pg.image.load(path.join('Assets', 'img_auto.png'))
BTN_INFO = pg.image.load(path.join('Assets', 'img_info.png'))
BTN_RESTOCK = pg.image.load(path.join('Assets', 'img_recycle.png'))
BTN_SOUND_ON = pg.image.load(path.join('Assets', 'img_sound_on.png'))
BTN_SOUND_OFF = pg.image.load(path.join('Assets', 'img_sound_off.png'))

# Button positions
BTN_AUTO_POS = (AREA_STOCK[0] + 4, AREA_STOCK[1] + 25)
BTN_RESTOCK_POS = (AREA_STOCK[0] + 16, AREA_STOCK[1] + 30)
BTN_SOUND_ON_POS = (520, 448)
BTN_SOUND_OFF_POS = (520, 448)

# Load Sound effects
SFX_MOVE = pg.mixer.Sound(path.join('Assets', 'sfx_move.wav'))
SFX_ERROR = pg.mixer.Sound(path.join('Assets', 'sfx_error.wav'))
SFX_INSERT = pg.mixer.Sound(path.join('Assets', 'sfx_insert.wav'))
SFX_RESTOCK = pg.mixer.Sound(path.join('Assets', 'sfx_recycle.wav'))
SFX_NEW_GAME = pg.mixer.Sound(path.join('Assets', 'sfx_new_game.wav'))

# Set sfx volume
SFX_MOVE.set_volume(0.5)
SFX_RESTOCK.set_volume(0.5)
SFX_INSERT.set_volume(1)
SFX_ERROR.set_volume(1)
SFX_NEW_GAME.set_volume(0.7)

# Tableau window pos
T_X = LEFT_MARGIN
T_Y = 150

# Tableau cell dimensions
CELL_HEIGHT = 11
CELL_WIDTH = 70

# Dict of Tableau positions
TABS = {(col, row): pg.Rect(i * CELL_WIDTH + T_X,
                            j * CELL_HEIGHT + T_Y,
                            CARD_WIDTH, CELL_HEIGHT)
        for i, col in enumerate(T_COLS)
        for j, row in enumerate(T_ROWS)}


# Returns the window's (x, y) position
def win_pos(t_pos: (int, int)):
    x, y = t_pos
    return (x * CELL_WIDTH) + T_X, \
           (y * CELL_HEIGHT) + T_Y


# ------------------------------------------------- DISPLAY LOOP ---------------------------------------------------
# Gets called inside game-loop
def display_win(dealer, hand, event, area, cell, timer, sfx):
    mx, my = pg.mouse.get_pos()
    loc = (mx, my)
    d = dealer

    card_back = d.deck.card_back_img
    card_faces = d.deck.card_img

    # Paint background/foundation slots
    WIN.fill(COLOR_BG)
    f_rect = [T1, T2, T3, T4]
    for r in f_rect:
        pg.draw.rect(WIN, COLOR_BG2, r)
    pg.draw.rect(WIN, COLOR_BG2, AREA_STOCK)

    # Sound button
    if sfx:
        WIN.blit(BTN_SOUND_ON, BTN_SOUND_ON_POS)
    else:
        WIN.blit(BTN_SOUND_OFF, BTN_SOUND_OFF_POS)

    # Timer and move count
    moves = LB.render('Moves ' + str(d.moves), True, T_COLOR)
    WIN.blit(moves, AREA_MOVES_LB)
    WIN.blit(timer, (LEFT_MARGIN, 12, 50, 50))

    # Load cards currently in play
    cards_tableau = [(card_faces[card], pos)
                     for pos, card in hand.items()
                     if card]

    # If all cards are in play and face-up
    # set auto complete button
    if d.check_auto_complete():
        WIN.blit(BTN_AUTO, BTN_AUTO_POS)

    elif d.stock_is_empty():
        WIN.blit(BTN_RESTOCK, BTN_RESTOCK_POS)

    else:
        for i, card in enumerate(d.get_stock()):
            if i <= STACK_LIMIT:
                WIN.blit(card_back, (AREA_STOCK[0] + i,
                                     AREA_STOCK[1] - i))

    # Display waste pile (top/current)
    x = 0
    if d.check_waste():
        for i, card in enumerate(d.get_waste()):
            WIN.blit(card_back, (AREA_WASTE[0] + i,
                                 AREA_WASTE[1] - i))
            x = i
            if i == STACK_LIMIT:
                break
    c = d.look_current_stock()

    if c:
        surf = card_faces[c]
        if c != d.holding:
            WIN.blit(surf, (AREA_CURRENT_STOCK[0] + x if x
                            else AREA_CURRENT_STOCK[0],
                            AREA_CURRENT_STOCK[1] - x if x
                            else AREA_CURRENT_STOCK[1]))

    # Display foundation
    step = 70
    for i, card in enumerate(d.current_foundation()):
        if card:
            surf = card_faces[card]
            WIN.blit(surf, (i * step + LEFT_MARGIN, TOP_MARGIN))

    # Draw cards in play onto tableau
    for card, pos in cards_tableau:
        if d.holding \
                and d.origin != CURRENT_STOCK \
                and d.origin != FOUNDATION:

            if d.origin != pos:
                if not d.in_tail(pos):
                    WIN.blit(card, win_pos(pos))

            # Face-down card display
            if pos in d.face_down:
                WIN.blit(card_back, win_pos(pos))

        else:
            WIN.blit(card, win_pos(pos))
            if pos in d.face_down:
                WIN.blit(card_back, win_pos(pos))

    if event == MOUSEBUTTONDOWN:  # ---------------------------------- MOUSE DOWN ----------------------------------

        # Picks up card from Tableau
        if area == TABLEAU:
            if not d.holding:

                # Find corresponding card
                for i in range(8):
                    pos = d.origin
                    if pos:
                        pos = (pos[0], pos[1] - i)
                        if d.in_cells(pos):  # ** put in func below?
                            c = d.get_card_tableau(pos)

                            # Pick up/drag card
                            if c in card_faces:
                                surf = card_faces[c]
                                WIN.blit(surf, loc)
                            break

            else:  # Card already in hand
                # Keep holding
                if d.holding in card_faces:
                    surf = card_faces[d.holding]
                    WIN.blit(surf, loc)

            # Check/set card tail
            tail = d.get_card_tail()
            if tail:
                for n, c in enumerate(tail):
                    surf = card_faces[c]
                    WIN.blit(surf, (loc[0], loc[1] + 11 * (n + 1)))

        # Clicks on Stock
        # (Stock does not include stock.current!)
        elif area == STOCK:
            # clicks auto-complete button
            if d.check_auto_complete():
                d.auto = True
            else:
                if d.stock_is_empty() and sfx:
                    SFX_RESTOCK.play()

                # Draws new card
                c = d.new_card()
                if c:
                    surf = card_faces[c]
                    WIN.blit(surf, (AREA_CURRENT_STOCK[0] + 30,
                                    AREA_CURRENT_STOCK[1] - 5))

        # Picks up card from top of stock pile
        elif area == CURRENT_STOCK:
            c = d.get_current_stock()
            if c:
                surf = card_faces[c]
                WIN.blit(surf, loc)

        # Picks up card from foundation
        elif area == FOUNDATION:
            if d.origin is None:
                c = None
                slots = len(d.current_foundation())
                if T1.collidepoint(loc):
                    if slots > 0:
                        c = d.get_card_foundation(0)
                elif T2.collidepoint(loc):
                    if slots > 1:
                        c = d.get_card_foundation(1)
                elif T3.collidepoint(loc):
                    if slots > 2:
                        c = d.get_card_foundation(2)
                elif T4.collidepoint(loc):
                    if slots > 3:
                        c = d.get_card_foundation(3)
                if c:
                    surf = card_faces[c]
                    WIN.blit(surf, loc)
            else:
                if d.holding:
                    surf = card_faces[d.holding]
                    WIN.blit(surf, loc)

    elif event == MOUSEBUTTONUP:  # ----------------------------------- MOUSE UP -----------------------------------

        #  Drops card in Foundation
        if area == FOUNDATION:
            if d.holding:
                success = d.insert_foundation(d.holding, d.origin)
                if success and sfx:
                    SFX_INSERT.play()
                elif sfx:
                    SFX_ERROR.play()

        # Drops card in Tableau
        elif area == TABLEAU:
            # Loop over previous cells in an attempt
            # to locate a valid card
            for i in range(8):
                if cell:
                    x = (cell[0], cell[1] - i)

                    # Attempt to insert card
                    success = d.insert_tableau(d.origin, x)
                    if success:
                        if sfx:
                            SFX_MOVE.play()
                            break

                    elif d.origin != FOUNDATION:
                        if d.in_cells(x):
                            break

                    elif i == 7:  # invalid and origin == foundation
                        # Return card to foundation
                        d.insert_foundation(d.holding, d.origin)
                        if sfx:
                            SFX_ERROR.play()

        # Return card to Foundation
        # if dropped in Waste/Stock area
        elif d.origin == FOUNDATION:
            d.insert_foundation(d.holding, d.origin)
            if sfx:
                SFX_INSERT.play()

        d.holding = None
        d.origin = None

    # Auto-complete
    if d.auto:
        d.auto_complete(cards_tableau)

    pg.display.update()


# -------------------------------------------------- GAME-LOOP -----------------------------------------------------

def play():
    clock = pg.time.Clock()
    playing = True
    sfx = True
    event = None
    cell = None
    area = None

    seconds = 0
    mins = 0
    time_delay = 1000
    timer_event = pg.USEREVENT + 1
    pg.time.set_timer(timer_event, time_delay)

    timer = LB.render('Time 00:00', True, T_COLOR)
    LB.render('Moves 0', True, T_COLOR)

    dealer = Dealer()
    hand = dealer.deal()

    # GAME-LOOP
    while playing:
        clock.tick(60)

        # Check for user input
        for e in pg.event.get():
            if e.type == pg.QUIT:
                playing = False

            # Mouse click
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    area = None
                    event = e.type

                    if AREA_TABLEAU.collidepoint(e.pos):
                        area = TABLEAU

                        for k, v in TABS.items():
                            if v.collidepoint(e.pos):
                                dealer.origin = k  # **

                    elif AREA_CURRENT_STOCK.collidepoint(e.pos):
                        area = CURRENT_STOCK

                    elif AREA_FOUNDATION.collidepoint(e.pos):
                        area = FOUNDATION

                    elif AREA_STOCK.collidepoint(e.pos):
                        area = STOCK

                    elif AREA_SOUND.collidepoint(e.pos):
                        sfx = not sfx

            # Mouse drop
            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    event = e.type
                    area = None
                    cell = None

                    if AREA_TABLEAU.collidepoint(e.pos):
                        area = TABLEAU
                        for k, v in TABS.items():
                            if v.collidepoint(e.pos):
                                cell = k

                    elif AREA_CURRENT_STOCK.collidepoint(e.pos):
                        area = CURRENT_STOCK

                    elif AREA_FOUNDATION.collidepoint(e.pos):
                        area = FOUNDATION

                    elif AREA_STOCK.collidepoint(e.pos):
                        area = STOCK

            # Key press
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_n:
                    if sfx:
                        SFX_NEW_GAME.play()
                    dealer = Dealer()
                    hand = dealer.deal()
                    dealer.new_game = True
                    seconds = 0
                    mins = 0
                if e.key == pg.K_z:
                    pass

            # Timer config
            elif e.type == timer_event:
                if dealer.check_win():
                    pass  # **
                elif dealer.new_game:
                    # Reset timer
                    timer = LB.render('Time 00:00', True, T_COLOR)
                else:  # Continue timer +1 seconds
                    seconds += 1
                    if seconds == 60:
                        seconds = 0
                        mins += 1

                    if mins >= 10:  # Time limit reached
                        timer = LB.render('Time +9:59', True, T_COLOR)
                    else:
                        timer = LB.render((
                            'Time 0' + str(mins) + ':' + '0' + str(seconds)
                            if seconds < 10
                            else 'Time 0' + str(mins) + ':' + str(seconds)
                        ), True, T_COLOR)

        # Refresh window display
        display_win(dealer, hand, event, area, cell, timer, sfx)

        # Single card flip/drop per mouse click
        if event == MOUSEBUTTONUP or area == STOCK:
            event = None

    pg.quit()


if __name__ == '__main__':
    play()
