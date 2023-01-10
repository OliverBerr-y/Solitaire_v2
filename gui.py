from os import path

import pygame as pg
from pygame.locals import *

from dealer import Dealer, TABLEAU, STOCK, \
    FOUNDATION, CURRENT_STOCK

WIDTH = 543
HEIGHT = 470
FPS = 60
ROT = 0

# Setting window
pg.display.set_caption('Solitaire')
WIN = pg.display.set_mode((WIDTH, HEIGHT))

# Loading card back image
CARD_BACK_IMG = pg.image.load(path.join('Assets', 'back.png'))
CARD_BACK = pg.transform.rotate(CARD_BACK_IMG, ROT)

# Button configurations
BUTTON_AUTO_COMPLETE = pg.image.load(path.join('Assets', 'button_auto-complete.png'))
BUTTON_RECYCLE = pg.image.load(path.join('Assets', 'recycle.png'))

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


def win_pos(pos: (int, int)):
    return (pos[0] * 70) + 30, \
           (pos[1] * 11) + 150


def display_win(d, click, drop, drop_pos, area, hand):
    mx, my = pg.mouse.get_pos()
    loc = (mx, my)

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

    if d.auto:
        if STOCK_AREA.collidepoint(loc):
            d.auto_complete(cards_tableau)

    # Drawing card movements
    elif click:
        if area == TABLEAU:
            c = d.get_card_from_tableau(d.current_pos)
            if c in d.deck.card_img:
                surf = d.deck.card_img[c]
                WIN.blit(surf, loc)

                tail = d.get_cards_tail()
                if tail:
                    count = 0
                    for c in tail:
                        count += 1
                        surf = d.deck.card_img[c]
                        WIN.blit(surf, (loc[0], loc[1] + 11 * count))

        elif area == STOCK:
            if d.check_winnable():
                d.auto = True
            else:
                c = d.new_card()
                if c:
                    surf = d.deck.card_img[c]
                    WIN.blit(surf, (CURRENT_STOCK_AREA[0] + 30, CURRENT_STOCK_AREA[1]))

        elif area == CURRENT_STOCK:
            c = d.get_current_stock()
            if c:
                surf = d.deck.card_img[c]
                WIN.blit(surf, loc)

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

    elif drop:
        if area == FOUNDATION:
            if d.current:
                if d.current_pos == FOUNDATION:
                    d.return_to_foundation(d.current)
                else:
                    d.insert_into_foundation(d.current, d.current_pos)

        elif area == TABLEAU:
            success = d.move_to_tableau(d.current_pos, drop_pos)
            if d.current_pos == FOUNDATION and not success:
                d.return_to_foundation(d.current)

        elif d.current_pos == FOUNDATION:
            d.return_to_foundation(d.current)

        d.current = None
        d.current_pos = None

    pg.display.update()


def main():
    clock = pg.time.Clock()
    playing = True
    click = False
    drop = False
    drop_pos = None
    area = None

    d = Dealer()
    hand = d.deal()

    while playing:
        clock.tick(FPS)

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
                                d.current_pos = k

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    click = False
                    area = None
                    drop = True
                    drop_pos = None

                    if FOUNDATION_AREA.collidepoint(event.pos):
                        area = FOUNDATION
                    elif TABLEAU_AREA.collidepoint(event.pos):
                        area = TABLEAU
                        for k, v in TABS.items():
                            if v.collidepoint(event.pos):
                                drop_pos = k
                    elif CURRENT_STOCK_AREA.collidepoint(event.pos):
                        area = CURRENT_STOCK
                    elif STOCK_AREA.collidepoint(event.pos):
                        area = STOCK

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_n:
                    d = Dealer()
                    hand = d.deal()
                if event.key == pg.K_z:
                    pass

        # Refresh window display
        display_win(d, click, drop, drop_pos, area, hand)

        if area == STOCK:
            click = False
        drop = False

    pg.quit()


if __name__ == '__main__':
    main()
