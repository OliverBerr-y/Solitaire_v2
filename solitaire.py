from os import path
import pygame as pg

from control import Dealer
from constants import *

# Area/Rect positions
AREA_FACE_UP_STOCK = pg.Rect(FACE_UP_STOCK_DIM)
AREA_FOUNDATION = pg.Rect(FOUNDATION_DIM)
AREA_TABLEAU = pg.Rect(TABLEAU_DIM)
AREA_STOCK = pg.Rect(STOCK_DIM)
AREA_WASTE = pg.Rect(WASTE_DIM)
AREA_SOUND = pg.Rect(BTN_SFX_DIM)
AREA_MOVES = (150, 12, 50, 50)

# Foundation positions
T4 = pg.Rect(LEFT_MARGIN + (70 * 3), TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
T3 = pg.Rect(LEFT_MARGIN + (70 * 2), TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
T2 = pg.Rect(LEFT_MARGIN + 70, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
T1 = pg.Rect(LEFT_MARGIN, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)

# Button positions
BTN_RESTOCK_POS = (AREA_STOCK[0] + 16, AREA_STOCK[1] + 30)
BTN_AUTO_POS = (AREA_STOCK[0] + 4, AREA_STOCK[1] + 25)
BTN_SOUND_OFF_POS = (520, 448)
BTN_SOUND_ON_POS = (520, 448)

# Dict of Tableau positions
TABS = {(col, row): pg.Rect(i * CELL_WIDTH + T_X,
                            j * CELL_HEIGHT + T_Y,
                            CARD_WIDTH, CELL_HEIGHT)
        for i, col in enumerate(T_COLS)
        for j, row in enumerate(T_ROWS)}

# Initialize window
pg.init()
pg.display.set_caption(WINDOW_CAPTION)
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
LB = pg.font.SysFont(FONT, TEXT_SIZE)

# Sound effects
SFX_NEW_GAME = pg.mixer.Sound(path.join('Assets', WAV_NEW_GAME))
SFX_NEW_GAME.set_volume(VOL_NEW_GAME)
SFX_RESTOCK = pg.mixer.Sound(path.join('Assets', WAV_RESTOCK))
SFX_RESTOCK.set_volume(VOL_RESTOCK)
SFX_INSERT = pg.mixer.Sound(path.join('Assets', WAV_INSERT))
SFX_INSERT.set_volume(VOL_INSERT)
SFX_ERROR = pg.mixer.Sound(path.join('Assets', WAV_ERROR))
SFX_ERROR.set_volume(VOL_ERROR)
SFX_MOVE = pg.mixer.Sound(path.join('Assets', WAV_MOVE))
SFX_MOVE.set_volume(VOL_MOVE)

# Button images
BTN_SOUND_OFF = pg.image.load(path.join('Assets', SOUND_OFF_IMG))
BTN_SOUND_ON = pg.image.load(path.join('Assets', SOUND_ON_IMG))
BTN_RESTOCK = pg.image.load(path.join('Assets', RESTOCK_IMG))
BTN_AUTO = pg.image.load(path.join('Assets', AUTO_IMG))
BTN_INFO = pg.image.load(path.join('Assets', INFO_IMG))


# Returns the window's (x, y) position
def win_pos(t_pos: (int, int)):
    x, y = t_pos
    return (x * CELL_WIDTH) + T_X, \
           (y * CELL_HEIGHT) + T_Y


class Solitaire:
    def __init__(self):
        self.dealer = Dealer()
        self.event = None
        self.area = None
        self.cell = None
        self.sound = True
        self._loc = None

        self.lb_timer = LB.render('Time 00:00', True, T_COLOR)
        self.lb_moves = LB.render('Moves 0', True, T_COLOR)

        self.hand = self.dealer.deal()

    @property
    def loc(self):
        return pg.mouse.get_pos()

    def play(self):
        clock = pg.time.Clock()
        timer_event = pg.USEREVENT + 1
        time_delay = 1000
        seconds = 0
        mins = 0

        pg.time.set_timer(timer_event, time_delay)

        playing = True
        while playing:
            clock.tick(FPS)

            # Check for user input
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    playing = False

                if e.type == pg.MOUSEBUTTONDOWN:  # <----------- MOUSE DOWN
                    if e.button == 1:
                        self.area = None
                        self.event = e.type

                        if AREA_TABLEAU.collidepoint(e.pos):
                            self.area = TABLEAU

                            for k, v in TABS.items():
                                if v.collidepoint(e.pos):
                                    self.dealer.origin = k  # **

                        elif AREA_FACE_UP_STOCK.collidepoint(e.pos):
                            self.area = FACE_UP_STOCK

                        elif AREA_FOUNDATION.collidepoint(e.pos):
                            self.area = FOUNDATION

                        elif AREA_STOCK.collidepoint(e.pos):
                            self.area = STOCK

                        elif AREA_SOUND.collidepoint(e.pos):
                            self.sound = not self.sound

                if e.type == pg.MOUSEBUTTONUP:  # <----------- MOUSE UP
                    if e.button == 1:
                        self.event = e.type
                        self.area = None
                        self.cell = None

                        if AREA_TABLEAU.collidepoint(e.pos):
                            self.area = TABLEAU
                            for k, v in TABS.items():
                                if v.collidepoint(e.pos):
                                    self.cell = k

                        elif AREA_FACE_UP_STOCK.collidepoint(e.pos):
                            self.area = FACE_UP_STOCK

                        elif AREA_FOUNDATION.collidepoint(e.pos):
                            self.area = FOUNDATION

                        elif AREA_STOCK.collidepoint(e.pos):
                            self.area = STOCK

                # Key press
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_n:
                        if self.sound:
                            SFX_NEW_GAME.play()
                        self.dealer = Dealer()
                        self.hand = self.dealer.deal()
                        self.dealer.new_game = True
                        seconds = 0
                        mins = 0
                    if e.key == pg.K_z:
                        pass

                # Update timer
                elif e.type == timer_event:
                    if self.dealer.check_win():
                        pass  # **
                    elif self.dealer.new_game:
                        # Reset timer
                        self.lb_timer = LB.render('Time 00:00', True, T_COLOR)
                    else:  # Continue timer +1 seconds
                        seconds += 1
                        if seconds == 60:
                            seconds = 0
                            mins += 1

                        if mins >= 10:  # Time limit reached
                            self.lb_timer = LB.render('Time +9:59', True, T_COLOR)
                        else:
                            self.lb_timer = LB.render((
                                'Time 0' + str(mins) + ':' + '0' + str(seconds)
                                if seconds < 10
                                else 'Time 0' + str(mins) + ':' + str(seconds)
                            ), True, T_COLOR)

            # Refresh window display
            self.set_display()

            # Single card flip/drop per mouse click
            if self.event == pg.MOUSEBUTTONUP or self.area == STOCK:
                self.event = None

        pg.quit()  # Exit window

    # FPS value (60) dictates the rate
    # at which set_display is called
    def set_display(self):
        d = self.dealer
        loc = self.loc

        # Card graphics
        card_back = d.deck.card_back_img
        card_faces: dict = d.deck.card_img

        # Paint background/foundation positions
        WIN.fill(COLOR_BG)
        f_rect = [T1, T2, T3, T4]
        for r in f_rect:
            pg.draw.rect(WIN, COLOR_BG2, r)
        pg.draw.rect(WIN, COLOR_BG2, AREA_STOCK)

        # Sound button
        if self.sound:
            WIN.blit(BTN_SOUND_ON, BTN_SOUND_ON_POS)
        else:
            WIN.blit(BTN_SOUND_OFF, BTN_SOUND_OFF_POS)

        # Timer and move count
        self.lb_moves = LB.render('Moves ' + str(d.moves), True, T_COLOR)
        WIN.blit(self.lb_moves, AREA_MOVES)
        WIN.blit(self.lb_timer, (LEFT_MARGIN, 12, 50, 50))

        # Load cards currently in play
        cards_tableau = [(card_faces[card], pos)
                         for pos, card in self.hand.items()
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
        c = d.current_stock()

        if c:
            surf = card_faces[c]
            if c != d.holding:
                WIN.blit(surf, (AREA_FACE_UP_STOCK[0] + x if x
                                else AREA_FACE_UP_STOCK[0],
                                AREA_FACE_UP_STOCK[1] - x if x
                                else AREA_FACE_UP_STOCK[1]))

        # Display foundation
        step = 70
        for i, card in enumerate(d.current_foundation()):
            if card:
                surf = card_faces[card]
                WIN.blit(surf, (i * step + LEFT_MARGIN, TOP_MARGIN))

        # Draw cards in play onto tableau
        for card, pos in cards_tableau:
            if d.holding \
                    and d.origin != FACE_UP_STOCK \
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

        if self.event == pg.MOUSEBUTTONDOWN:  # <----------- MOUSE DOWN

            # Picks up card from Tableau
            if self.area == TABLEAU:
                if not d.holding:

                    # Find corresponding card
                    for i in range(8):
                        pos = d.origin
                        if pos:
                            pos = (pos[0], pos[1] - i)
                            if d.in_cells(pos):  # ** put in func below?
                                c = d.pick_up_tableau(pos)

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
            elif self.area == STOCK:
                # clicks auto-complete button
                if d.check_auto_complete():
                    d.auto = True
                else:
                    if d.stock_is_empty() and self.sound:
                        SFX_RESTOCK.play()

                    # Draws new card
                    c = d.new_card()
                    if c:
                        surf = card_faces[c]
                        WIN.blit(surf, (AREA_FACE_UP_STOCK[0] + 30,
                                        AREA_FACE_UP_STOCK[1] - 5))

            # Picks up card from top of stock pile
            elif self.area == FACE_UP_STOCK:
                c = d.pick_up_current_stock()
                if c:
                    surf = card_faces[c]
                    WIN.blit(surf, loc)

            # Picks up card from foundation
            elif self.area == FOUNDATION:
                if d.origin is None:
                    c = None
                    slots = len(d.current_foundation())
                    if T1.collidepoint(loc):
                        if slots > 0:
                            c = d.pick_up_foundation(0)
                    elif T2.collidepoint(loc):
                        if slots > 1:
                            c = d.pick_up_foundation(1)
                    elif T3.collidepoint(loc):
                        if slots > 2:
                            c = d.pick_up_foundation(2)
                    elif T4.collidepoint(loc):
                        if slots > 3:
                            c = d.pick_up_foundation(3)
                    if c:
                        surf = card_faces[c]
                        WIN.blit(surf, loc)
                else:
                    if d.holding:
                        surf = card_faces[d.holding]
                        WIN.blit(surf, loc)

        elif self.event == pg.MOUSEBUTTONUP:  # <----------- MOUSE UP

            #  Drops card in Foundation
            if self.area == FOUNDATION:
                if d.holding:
                    success = d.drop_foundation(d.holding, d.origin)
                    if success and self.sound:
                        SFX_INSERT.play()
                    elif self.sound:
                        SFX_ERROR.play()

            # Drops card in Tableau
            elif self.area == TABLEAU:
                # Loop over previous cells in an attempt
                # to locate a valid card
                for i in range(8):
                    if self.cell:
                        x = (self.cell[0], self.cell[1] - i)

                        # Attempt to insert card
                        success = d.drop_tableau(d.origin, x)
                        if success:
                            if self.sound:
                                SFX_MOVE.play()
                                break

                        elif d.origin != FOUNDATION:
                            if d.in_cells(x):
                                break

                        elif i == 7:  # invalid and origin == foundation
                            # Return card to foundation
                            d.drop_foundation(d.holding, d.origin)
                            if self.sound:
                                SFX_ERROR.play()

            # Return card to Foundation
            # if dropped in Waste/Stock area
            elif d.origin == FOUNDATION:
                d.drop_foundation(d.holding, d.origin)
                if self.sound:
                    SFX_INSERT.play()

            d.holding = None
            d.origin = None

        # Auto-complete
        if d.auto:
            d.auto_complete(cards_tableau)

        pg.display.update()
