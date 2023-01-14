import random as r
from os import path
import pygame as pg


class Card:
    def __init__(self, suit, rank):
        self._suit = suit
        self._rank = rank
        self._color = 'black' if suit == 'spades' \
                      or suit == 'clubs' \
                      else 'red'

    @property
    def color(self):
        return self._color

    @property
    def suit(self):
        return self._suit

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        self._rank = value


class Deck:
    def __init__(self):
        self._suits = ['diamonds', 'hearts', 'clubs', 'spades']
        self.card_img = {}

        # Generates a standard deck of 52 playing cards
        self._cards = [Card(suit, rank)
                       for suit in self._suits
                       for rank in range(1, 13)]

        # Loads and stores the front side images of each card
        # in a dict as a pygame surface.
        for card in self._cards:
            c = self.load_card(card)
            if c:
                self.card_img[c[1]] = c[0]

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

    def shuffle(self):
        r.shuffle(self.cards)

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, value):
        self._cards = value
