import random as r
from os import path
import pygame as pg


class Card:
    def __init__(self):
        self._color = ''
        self._suit = ''
        self._rank = 0

    @property
    def color(self):
        return self._color

    @property
    def suit(self):
        return self._suit

    @property
    def rank(self):
        return self._rank

    @suit.setter
    def suit(self, value):
        self._suit = value
        if value == 'diamonds' or value == 'hearts':
            self._color = 'red'
        elif value == 'clubs' or value == 'spades':
            self._color = 'black'

    @rank.setter
    def rank(self, value):
        self._rank = value


class Deck:
    def __init__(self):
        self.__count = 52
        self.__suits = ['diamonds', 'hearts', 'clubs', 'spades']
        self.__colors = ['black', 'red']
        self._cards = []
        self.card_img = {}

        # Generates a standard deck of 52 playing cards
        for suit in range(4):
            for rank in range(1, int(self.__count / 4) + 1):
                c = Card()
                c.suit = self.__suits[suit]
                c.rank = rank

                self._cards.append(c)

        # Loads and stores the front side images of each card
        # in a dict as a pygame surface.
        for card in self._cards:
            c = self.load_card(card)
            if c:
                surface, card = c
                self.card_img[card] = surface

    def shuffle(self):
        r.shuffle(self.cards)

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, value):
        self._cards = value

    @staticmethod
    def load_hand(cards: dict):
        loaded = []

        for pos, card in cards.items():
            if card != 0:
                p = path.join('Assets', str(card.rank) + '_' + card.suit + '.png')
                loaded.append(((pg.transform.rotate(pg.image.load(p), 0)), pos))
        return loaded

    @staticmethod
    def load_card(card: Card):
        if card:
            p = path.join('Assets', str(card.rank) + '_' + card.suit + '.png')
            return pg.transform.rotate(pg.image.load(p), 0), card
        return False

