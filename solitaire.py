from os import path

import pygame as pg
from pygame.locals import *

from dealer import Dealer, TABLEAU, STOCK, \
    FOUNDATION, CURRENT_STOCK

WIN_WIDTH = 543
WIN_HEIGHT = 470
MAX_STACK_HEIGHT = 5
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption('Solitaire')
pg.init()

# Label font/color/size
FONT = pg.font.SysFont('COURIER', 17)
T_COLOR = '#EEFFEE'

# Board divisions
CURRENT_STOCK_AREA = pg.Rect(380, 40, 63, 90)
FOUNDATION_AREA = pg.Rect(0, 0, 350, 150)
TABLEAU_AREA = pg.Rect(30, 150, 483, 300)
STOCK_AREA = pg.Rect(450, 40, 63, 90)
WASTE_AREA = pg.Rect(379, 40, 63, 90)
SOUND_AREA = pg.Rect(520, 448, 15, 15)

# Foundation card positions
T4 = pg.Rect(239, 40, 63, 90)
T3 = pg.Rect(169, 40, 63, 90)
T2 = pg.Rect(100, 40, 63, 90)
T1 = pg.Rect(30, 40, 63, 90)

# Card back img
CARD_BACK_IMG = pg.image.load(path.join('Assets', 'back.png'))
CARD_BACK = pg.transform.rotate(CARD_BACK_IMG, 0)

# Button img
BTN_AUTO = pg.image.load(path.join('Assets', 'auto-complete.png'))
BTN_RESTOCK = pg.image.load(path.join('Assets', 'recycle.png'))
BTN_SOUND_ON = pg.image.load(path.join('Assets', 'sound_on.png'))
BTN_SOUND_OFF = pg.image.load(path.join('Assets', 'sound_off.png'))
BTN_INFO = pg.image.load(path.join('Assets', 'info.png'))

BTN_AUTO_POS = (STOCK_AREA[0] + 4, STOCK_AREA[1] + 25)
BTN_RESTOCK_POS = (STOCK_AREA[0] + 16, STOCK_AREA[1] + 30)
BTN_SOUND_ON_POS = (520, 448)
BTN_SOUND_OFF_POS = (520, 448)

# Sound effects
SFX_MOVE = pg.mixer.Sound(path.join('Assets', 'click2.wav'))
SFX_RESTOCK = pg.mixer.Sound(path.join('Assets', 'sfx_recycle.wav'))
SFX_INSERT = pg.mixer.Sound(path.join('Assets', 'sfx_insert.wav'))
SFX_ERROR = pg.mixer.Sound(path.join('Assets', 'sfx_error.wav'))
SFX_NEW_GAME = pg.mixer.Sound(path.join('Assets', 'sfx_new_game.wav'))

# SFX volume
SFX_MOVE.set_volume(0.3)
SFX_RESTOCK.set_volume(0.2)
SFX_INSERT.set_volume(0.5)
SFX_ERROR.set_volume(0.6)
SFX_NEW_GAME.set_volume(0.5)

# Tableau card positions
TABS = {}
T_HEIGHT = 11
T_WIDTH = 70

count_x = 30
for i in range(7):  # max no. of cols
    if i != 0:
        count_x += T_WIDTH
    count_y = 150
    for j in range(28):  # max no. of rows
        # Generate rect for each Tableau position
        TABS[i, j] = pg.Rect(count_x, count_y, 63, T_HEIGHT)
        count_y += T_HEIGHT


# Returns the window's (x, y) position
def win_pos(t_coordinates: (int, int)):
    x, y = t_coordinates
    return (x * T_WIDTH) + 30, \
           (y * T_HEIGHT) + 150


# Main window display function. Called within game-loop
def display_win(dealer, hand, event, area, cell, timer, sfx):
    mx, my = pg.mouse.get_pos()
    loc = (mx, my)
    d = dealer

    # Paint background/foundation slots
    WIN.fill('#008000')
    f_rect = [T1, T2, T3, T4]
    for rect in f_rect:
        pg.draw.rect(WIN, '#007000', rect)
    pg.draw.rect(WIN, '#007000', STOCK_AREA)

    # Sound button
    if sfx:
        WIN.blit(BTN_SOUND_ON, BTN_SOUND_ON_POS)
    else:
        WIN.blit(BTN_SOUND_OFF, BTN_SOUND_OFF_POS)

    # Timer and move count
    moves = FONT.render('Moves ' + str(d.moves), True, T_COLOR)
    WIN.blit(moves, (150, 12, 50, 50))
    WIN.blit(timer, (30, 12, 50, 50))

    # Load cards currently in play
    cards_tableau = [(d.deck.card_img[card], pos)
                     for pos, card in hand.items()
                     if card]

    # If all cards are in play and face-up
    # set auto complete button
    if d.check_auto_complete():
        WIN.blit(BTN_AUTO, BTN_AUTO_POS)

    elif d.stock_is_empty():
        WIN.blit(BTN_RESTOCK, BTN_RESTOCK_POS)

    else:
        for n, card in enumerate(d.get_stock()):
            if n <= MAX_STACK_HEIGHT:
                WIN.blit(CARD_BACK, (STOCK_AREA[0] + n,
                                     STOCK_AREA[1] - n))

    # Display waste pile (top/current)
    pos = 0
    if d.check_waste():
        for n, card in enumerate(d.get_waste()):
            WIN.blit(CARD_BACK, (WASTE_AREA[0] + n, WASTE_AREA[1] - n))
            pos = n
            if n == MAX_STACK_HEIGHT:
                break
    c = d.look_current_stock()

    if c:
        surf = d.deck.card_img[c]
        if c != d.current:
            WIN.blit(surf, (CURRENT_STOCK_AREA[0] + pos if pos else CURRENT_STOCK_AREA[0],
                            CURRENT_STOCK_AREA[1] - pos if pos else CURRENT_STOCK_AREA[1]))

    # Display foundation
    x_pos = 30
    for n, card in enumerate(d.current_foundation()):
        if n != 0:
            x_pos += 70

        if card:
            surf = d.deck.card_img[card]
            WIN.blit(surf, (x_pos, 40))

    # Draw cards in play onto tableau
    for card, pos in cards_tableau:
        if d.current \
                and d.current_pos != CURRENT_STOCK \
                and d.current_pos != FOUNDATION:

            if d.current_pos != pos:
                if not d.in_tail(pos):
                    WIN.blit(card, win_pos(pos))

            # Face-down card display
            if pos in d.face_down:
                WIN.blit(CARD_BACK, win_pos(pos))

        else:
            WIN.blit(card, win_pos(pos))
            if pos in d.face_down:
                WIN.blit(CARD_BACK, win_pos(pos))

    # Drawing card movements
    if event == MOUSEBUTTONDOWN:
        if area == TABLEAU:
            c = d.get_card_from_tableau(d.current_pos)
            if c in d.deck.card_img:
                surf = d.deck.card_img[c]
                WIN.blit(surf, loc)

                # Set card tail if applicable
                tail = d.get_cards_tail()
                if tail:
                    for n, c in enumerate(tail):
                        surf = d.deck.card_img[c]
                        WIN.blit(surf, (loc[0], loc[1] + 11 * (n + 1)))

        elif area == STOCK:
            if d.check_auto_complete():
                d.auto = True

            else:
                if d.stock_is_empty() and sfx:
                    SFX_RESTOCK.play()

                # Draws new card
                c = d.new_card()
                if c:
                    surf = d.deck.card_img[c]
                    WIN.blit(surf, (CURRENT_STOCK_AREA[0] + 30,
                                    CURRENT_STOCK_AREA[1] - 5))

        # Picks up card from top of stock pile
        elif area == CURRENT_STOCK:
            c = d.get_current_stock()
            if c:
                surf = d.deck.card_img[c]
                WIN.blit(surf, loc)

        # Picks up card from foundation
        elif area == FOUNDATION:
            if d.current_pos is None:
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
                    surf = d.deck.card_img[c]
                    WIN.blit(surf, loc)
            else:
                if d.current:
                    surf = d.deck.card_img[d.current]
                    WIN.blit(surf, loc)

    # If a card is currently being held, an attempt will be made
    # to insert the card into the area defined
    elif event == MOUSEBUTTONUP:
        if area == FOUNDATION:
            if d.current:
                success = d.insert_into_foundation(d.current, d.current_pos)
                if success and sfx:
                    SFX_INSERT.play()
                elif sfx:
                    SFX_ERROR.play()

        elif area == TABLEAU:
            success = d.move_to_tableau(d.current_pos, cell)
            if success and sfx:
                SFX_MOVE.play()
                pass
            elif d.current_pos == FOUNDATION and sfx:
                d.insert_into_foundation(d.current, d.current_pos)
                SFX_ERROR.play()

        elif d.current_pos == FOUNDATION:
            d.insert_into_foundation(d.current, d.current_pos)
            if sfx:
                SFX_INSERT.play()

        d.current = None
        d.current_pos = None

    if d.auto:
        # Activate auto complete function
        d.auto_complete(cards_tableau)

    pg.display.update()


def main():
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

    timer = FONT.render('Time 00:00', True, T_COLOR)
    FONT.render('Moves 0', True, T_COLOR)

    dealer = Dealer()
    hand = dealer.deal()

    # Game loop
    while playing:
        clock.tick(60)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                playing = False

            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    area = None
                    event = e.type

                    if STOCK_AREA.collidepoint(e.pos):
                        area = STOCK
                    elif CURRENT_STOCK_AREA.collidepoint(e.pos):
                        area = CURRENT_STOCK
                    elif FOUNDATION_AREA.collidepoint(e.pos):
                        area = FOUNDATION
                    elif TABLEAU_AREA.collidepoint(e.pos):
                        area = TABLEAU
                        for k, v in TABS.items():
                            if v.collidepoint(e.pos):
                                dealer.current_pos = k
                    elif SOUND_AREA.collidepoint(e.pos):
                        sfx = not sfx

            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    event = e.type
                    area = None
                    cell = None

                    if FOUNDATION_AREA.collidepoint(e.pos):
                        area = FOUNDATION
                    elif TABLEAU_AREA.collidepoint(e.pos):
                        area = TABLEAU
                        for k, v in TABS.items():
                            if v.collidepoint(e.pos):
                                cell = k
                    elif CURRENT_STOCK_AREA.collidepoint(e.pos):
                        area = CURRENT_STOCK
                    elif STOCK_AREA.collidepoint(e.pos):
                        area = STOCK

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

            elif e.type == timer_event:
                if dealer.check_win():
                    pass
                elif dealer.new_game:
                    timer = FONT.render('Time 00:00', True, T_COLOR)
                else:
                    seconds += 1
                    if seconds == 60:
                        seconds = 0
                        mins += 1

                    if mins >= 10:
                        timer = FONT.render('Time +9:59', True, T_COLOR)
                    else:
                        timer = FONT.render((
                            'Time 0' + str(mins) + ':' + '0' + str(seconds)
                            if seconds < 10
                            else 'Time 0' + str(mins) + ':' + str(seconds)
                        ),
                            True, T_COLOR)

        # Refresh window display
        display_win(dealer, hand, event, area, cell, timer, sfx)

        if event == MOUSEBUTTONUP or area == STOCK:
            event = None

    pg.quit()


if __name__ == '__main__':
    main()


# <a href="https://www.flaticon.com/free-icons/solitaire" title="solitaire icons">Solitaire icons created by Febrian Hidayat - Flaticon</a>