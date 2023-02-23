from constants import T_COLS, T_ROWS
from playing_cards import Card


class Tableau:
    def __init__(self):
        self._cells: dict = {}

        # Generate tableau coordinates
        self._cells = {(col, row): 0
                       for col in T_COLS
                       for row in T_ROWS}

    def deal(self, cards: list):
        for col in T_COLS:
            for row in range(col + 1):
                self._cells[(col, row)] = (cards.pop())

        # Return hand when all cards have been dealt
        if len(cards) != 0:
            return False
        return self._cells

    # Compares first card against destination card
    # returning true if move is valid
    @staticmethod
    def check_move(card_1: Card, card_2: Card):
        if card_1.color == card_2.color:
            return False
        if card_1.rank != card_2.rank - 1:
            return False
        else:
            return True

    @property
    def cells(self):
        return self._cells


# The Foundation contains four stacks of cards (each starting empty).
# The order in which card suits sit in the Foundation is tethered to
# the order in which they were originally placed into it.
class Foundation:
    def __init__(self):
        self._stacks = {'diamonds': CardStack(), 'hearts': CardStack(),
                        'clubs': CardStack(), 'spades': CardStack()}
        self._order = []

    # Removes and returns the top card
    # from the selected foundation stack
    def pop(self, idx: int):
        stack = self._stacks[self._order[idx]]
        card = stack.get_top()
        return card

    # Returns a list of all visible Foundation cards.
    # Does not remove cards from Foundation
    def look_top_cards(self):
        x = []
        for suit in self._order:
            x.append(self.stacks[suit].look_top())
        return x

    # Adds card to the appropriate stack
    # based on its suit
    def _add(self, card):
        self._stacks[card.suit].add(card)

    def add(self, card):
        if card:
            if card.rank == 1:
                self._add(card)
                if card.suit not in self._order:
                    self._order.append(card.suit)
                return True
            else:
                top = self._stacks[card.suit].look_top()
                if top:
                    if card.rank == top.rank + 1:
                        self._add(card)
                        return True
        return False

    def check_win(self):
        for suit in self._stacks.values():
            if suit.height < suit.max_height:
                return False
        return True

    @property
    def stacks(self):
        return self._stacks

    @property
    def order(self):
        return self._order


class CardStack:
    def __init__(self):
        self._max_height = 13
        self._height = None
        self._stack = []

    def look_top(self):
        if self.height > 0:
            return self._stack[self.height - 1]
        else:
            return False

    def get_top(self):
        if self.height > 0:
            return self._stack.pop()

    def add(self, card):
        self._stack.append(card)

    @property
    def height(self):
        return len(self._stack)

    @property
    def max_height(self):
        return self._max_height


# The Stock is the starting position of the deck upon starting a game
# it has a waste pile that can be recycled back into the stock pile
# only one card from the stock/waste is ever showing at any given time.
class Stock:
    def __init__(self, deck):
        self._cards = deck
        self._waste = Waste()
        self._current = None

    # Draw a starting hand of 28 cards
    # this hand is then used to set the tableau
    def draw(self, n):
        hand = []

        for i in range(n):
            c = self._cards.cards.pop()
            hand.append(c)

        return hand

    # Flips a new card from the top of the Stock pile
    # sending any currently face up card into the Waste pile
    def flip(self):
        if len(self._cards.cards) != 0:
            if self._current:
                self.toss()
            self._current = self._cards.cards.pop()
            return self._current
        self.reset()

    # Used by the flip() function once the Stock pile has been depleted
    # recycles the Waste pile into a new Stock pile
    def reset(self):
        self._waste.stack.append(self._current)
        self._cards.cards = self._waste.recycle()
        self._waste = Waste()
        self._current = None

    # Sends any currently face up card into the Waste pile
    def toss(self):
        self._waste.add(self._current)

    # Returns the current card count
    def is_empty(self):
        for c in self._cards.cards:
            if c:
                return False
        return True

    @property
    def current(self):
        return self._current

    @property
    def cards(self):
        return self._cards

    @property
    def waste(self):
        return self._waste

    @current.setter
    def current(self, value):
        self._current = value

    @cards.setter
    def cards(self, value):
        self._cards = value

    @waste.setter
    def waste(self, value):
        self._waste = value


# The Waste pile is held by the stock pile and contains all the
# cards that the player has previously flipped and not played.
# Cards are recycled into a new Stock pile once stock is empty.
class Waste:
    def __init__(self):
        self._height = 0
        self._stack = []

    def add(self, card):
        self._stack.append(card)
        self._height += 1

    def get_last(self):
        if self._height > 0:
            self._height -= 1
            return self._stack.pop()

    def recycle(self):
        self._stack.reverse()
        return self._stack

    @property
    def height(self):
        return self._height

    @property
    def stack(self):
        return self._stack

    @height.setter
    def height(self, value):
        self._height = value
