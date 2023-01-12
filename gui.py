from os import path

import pygame as pg
from pygame.locals import *

from dealer import Dealer, TABLEAU, STOCK, \
    FOUNDATION, CURRENT_STOCK

# Setting window
pg.init()
pg.display.set_caption('Solitaire')

WIN_WIDTH = 543
WIN_HEIGHT = 470
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

# Loading card back image
CARD_BACK_IMG = pg.image.load(path.join('Assets', 'back.png'))
CARD_BACK = pg.transform.rotate(CARD_BACK_IMG, 0)

# Button configurations
BUTTON_AUTO_COMPLETE = pg.image.load(path.join('Assets', 'auto-complete.png'))
BUTTON_RECYCLE = pg.image.load(path.join('Assets', 'recycle.png'))
BUTTON_INFO = pg.image.load(path.join('Assets', 'info.png'))

# Text font/color/size
FONT = pg.font.SysFont('COURIER', 17)
T_COLOR = '#EFFFEF'

# Board divisions
CURRENT_STOCK_AREA = pg.Rect(380, 40, 63, 90)
FOUNDATION_AREA = pg.Rect(0, 0, 350, 150)
TABLEAU_AREA = pg.Rect(30, 150, 483, 300)
STOCK_AREA = pg.Rect(450, 40, 63, 90)
WASTE_AREA = pg.Rect(355, 40, 63, 90)

# Foundation card positions
T4 = pg.Rect(239, 40, 63, 90)
T3 = pg.Rect(169, 40, 63, 90)
T2 = pg.Rect(100, 40, 63, 90)
T1 = pg.Rect(30, 40, 63, 90)

# Foundation card positions
TABS = {}
x = 30
for i in range(7):  # max no. of cols
    if i > 0:
        x += 70
    y = 150
    for j in range(28):  # max no. of rows
        TABS[i, j] = pg.Rect(x, y, 63, 11)
        y += 11


# Given tableau coordinates as a parameter
# Returns the window's (x, y) position
def win_pos(pos: (int, int)):
    return (pos[0] * 70) + 30, \
           (pos[1] * 11) + 150


# Main window display function. Called within game-loop
def display_win(dealer, hand, click, drop, area, cell, timer):
    mx, my = pg.mouse.get_pos()
    loc = (mx, my)
    d = dealer

    # Paint background/foundation slots
    WIN.fill('#008000')
    f_rect = [T1, T2, T3, T4]
    for rect in f_rect:
        pg.draw.rect(WIN, '#007000', rect)
    pg.draw.rect(WIN, '#007000', STOCK_AREA)

    # Load cards currently in play
    cards_tableau = []
    for pos, card in hand.items():
        if card:
            cards_tableau.append((d.deck.card_img[card], pos))

    # If all cards are in play and face-up
    # set auto complete button
    if d.check_winnable():
        WIN.blit(BUTTON_AUTO_COMPLETE, (STOCK_AREA[0] + 4, STOCK_AREA[1] + 25))

    # Display remaining stock
    elif d.stock_is_empty():
        WIN.blit(BUTTON_RECYCLE, (STOCK_AREA[0] + 16, STOCK_AREA[1] + 30))
    else:
        WIN.blit(CARD_BACK, STOCK_AREA)

    # Display waste pile (top/current)
    if d.check_waste():
        WIN.blit(CARD_BACK, WASTE_AREA)
    c = d.look_current_stock()
    if c:
        surf = d.deck.card_img[c]
        if c != d.current:
            WIN.blit(surf, CURRENT_STOCK_AREA)

    # Display foundation
    x_pos = 30
    count = 0
    for card in d.get_current_foundation():
        if count != 0:
            x_pos += 70
        count += 1
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

    if d.auto:  # Activate auto complete function
        if STOCK_AREA.collidepoint(loc):
            d.auto_complete(cards_tableau)

    # Drawing card movements
    elif click:
        if area == TABLEAU:
            c = d.get_card_from_tableau(d.current_pos)
            if c in d.deck.card_img:
                surf = d.deck.card_img[c]
                WIN.blit(surf, loc)

                # Set card tail if applicable
                tail = d.get_cards_tail()
                if tail:
                    count = 0
                    for c in tail:
                        count += 1
                        surf = d.deck.card_img[c]
                        WIN.blit(surf, (loc[0], loc[1] + 11 * count))

        elif area == STOCK:
            if d.check_winnable():
                # Will activated auto complete function
                d.auto = True
            else:
                # Draws new card
                c = d.new_card()
                if c:
                    surf = d.deck.card_img[c]
                    WIN.blit(surf, (CURRENT_STOCK_AREA[0] + 30, CURRENT_STOCK_AREA[1]))

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
                slots = len(d.get_current_foundation())
                if T1.collidepoint(loc):
                    if slots > 0:
                        c = d.get_card_from_foundation(0)
                elif T2.collidepoint(loc):
                    if slots > 1:
                        c = d.get_card_from_foundation(1)
                elif T3.collidepoint(loc):
                    if slots > 2:
                        c = d.get_card_from_foundation(2)
                elif T4.collidepoint(loc):
                    if slots > 3:
                        c = d.get_card_from_foundation(3)
                if c:
                    surf = d.deck.card_img[c]
                    WIN.blit(surf, loc)
            else:
                surf = d.deck.card_img[d.current]
                WIN.blit(surf, loc)

    # If a card is currently being held, an attempt will be made
    # to insert the card into the area defined
    elif drop:
        if area == FOUNDATION:
            if d.current:
                d.insert_into_foundation(d.current, d.current_pos)

        elif area == TABLEAU:
            success = d.move_to_tableau(d.current_pos, cell)
            if d.current_pos == FOUNDATION and not success:
                d.insert_into_foundation(d.current, d.current_pos)

        elif d.current_pos == FOUNDATION:
            d.insert_into_foundation(d.current, d.current_pos)

        d.current = None
        d.current_pos = None

    # One screen info (Timer, Moves, Info)
    moves = FONT.render('Moves ' + str(d.moves), True, T_COLOR)
    WIN.blit(moves, (150, 12, 50, 50))
    WIN.blit(timer, (30, 12, 50, 50))
    WIN.blit(BUTTON_INFO, (520, 447))

    pg.display.update()


def main():
    clock = pg.time.Clock()
    playing = True
    click = False
    drop = False
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

    while playing:
        clock.tick(60)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                playing = False

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    area = None
                    click = True

                    if STOCK_AREA.collidepoint(event.pos):
                        area = STOCK
                    elif CURRENT_STOCK_AREA.collidepoint(event.pos):
                        area = CURRENT_STOCK
                    elif FOUNDATION_AREA.collidepoint(event.pos):
                        area = FOUNDATION
                    elif TABLEAU_AREA.collidepoint(event.pos):
                        area = TABLEAU
                        for k, v in TABS.items():
                            if v.collidepoint(event.pos):
                                dealer.current_pos = k

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    click = False
                    area = None
                    drop = True
                    cell = None

                    if FOUNDATION_AREA.collidepoint(event.pos):
                        area = FOUNDATION
                    elif TABLEAU_AREA.collidepoint(event.pos):
                        area = TABLEAU
                        for k, v in TABS.items():
                            if v.collidepoint(event.pos):
                                cell = k
                    elif CURRENT_STOCK_AREA.collidepoint(event.pos):
                        area = CURRENT_STOCK
                    elif STOCK_AREA.collidepoint(event.pos):
                        area = STOCK

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_n:
                    dealer = Dealer()
                    hand = dealer.deal()
                    dealer.new_game = True
                    seconds = 0
                    mins = 0
                if event.key == pg.K_z:
                    pass

            elif event.type == timer_event:
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
        display_win(dealer, hand, click, drop, area, cell, timer)

        if area == STOCK:
            click = False
        drop = False

    pg.quit()


if __name__ == '__main__':
    main()
