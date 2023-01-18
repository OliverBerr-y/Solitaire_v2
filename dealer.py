from playing_cards import Deck, Card
from board import Tableau, Stock, Foundation, \
    T_COLS, T_ROWS

# Constants
CURRENT_STOCK = 'current_stock'
FOUNDATION = 'foundation'
TABLEAU = 'tableau'
STOCK = 'stock'


# Handles solitaire.py and board.py interactions
class Dealer:
    def __init__(self):
        self._deck = Deck()
        self._deck.shuffle()

        self.new_game = True
        self.auto = False
        self.moves = 0

        # Board positions
        self._foundation = Foundation()
        self._tableau = Tableau()
        self._stock = Stock(self._deck)

        # Contains initial face-down positions
        self.face_down = [(x, y)
                          for x in range(1, 7)
                          for y in range(x)]

        # Currently held card
        self.holding = None
        self.origin = None
        self.tail = []

    def deal(self):
        return self._tableau.deal(self._stock.draw(28))

    def new_card(self):
        if self.new_game:
            self.new_game = False
        self.moves += 1
        return self._stock.flip()

    def check_waste(self):
        return self._stock.waste.height >= 1

    def get_waste(self):
        return self._stock.waste.stack

    def stock_is_empty(self):
        return self._stock.is_empty()

    def get_stock(self):
        return self._stock.cards.cards

    def look_current_stock(self):
        return self._stock.current

    def get_current_stock(self):
        if self._stock.current:
            self.holding = self._stock.current
            self.origin = CURRENT_STOCK
        return self._stock.current

    def get_card_tableau(self, pos):
        cells = self._tableau.cells

        if pos and pos not in self.face_down:
            self.holding = cells[pos]
            self.origin = pos
            self.set_tail(pos[0], pos[1])
            return cells[pos]

        self.holding = None
        self.origin = None
        return False

    def in_cells(self, pos):
        if pos in self._tableau.cells:
            if self._tableau.cells[pos] != 0:
                return True
        return False

    def insert_tableau(self, origin, dest):
        if origin == FOUNDATION:
            success = self.move_from_alt(self.holding, dest)

        elif origin == CURRENT_STOCK:
            success = self.move_from_alt(self.holding, dest)
            if success:
                self._stock.current = self._stock.waste.get_last()

        else:  # origin == TABLEAU:
            success = self.move_from_tableau(origin, dest)
            if success:
                self.tail = []
                if (origin[0], origin[1] - 1) in self.face_down:
                    self.face_down.remove((origin[0], origin[1] - 1))

        if success:
            self.new_game = False
            self.moves += 1
            return True
        return False

    def move_from_tableau(self, origin: (int, int), drop_pos: (int, int)):
        t = self._tableau

        if drop_pos:
            dest = (drop_pos[0], drop_pos[1] + 1)

            if origin in t.cells:
                c = t.cells[origin]

                if drop_pos in t.cells:
                    if t.cells[drop_pos] and t.cells[dest] == 0:
                        if dest != origin:
                            if t.check_move(c, t.cells[drop_pos]):
                                t.cells[dest] = c
                                t.cells[origin] = 0
                                self.tail = self.move_tail(origin, dest)
                                return True
                            else:
                                return False

                elif c and dest in t.cells:
                    if c.rank == 13 and t.cells[drop_pos[0], 0] == 0:
                        t.cells[dest] = c
                        t.cells[origin] = 0
                        self.tail = self.move_tail(origin, dest)
                        return True
        return False

    def move_from_alt(self, c: Card, drop_pos: (int, int)):
        t = self._tableau

        if drop_pos:
            dest = (drop_pos[0], drop_pos[1] + 1)

            if drop_pos in t.cells:
                if t.cells[drop_pos] and t.cells[dest] == 0:
                    if t.check_move(c, t.cells[drop_pos]):
                        t.cells[dest] = c
                        return True
                    else:
                        return False

            elif dest in t.cells:
                if c.rank == 13 and t.cells[drop_pos[0], 0] == 0:
                    t.cells[dest] = c
                    return True
        return False

    def current_foundation(self):
        return self._foundation.look_top_cards()

    def get_card_foundation(self, idx: int):
        self.origin = FOUNDATION
        self.holding = self._foundation.pop(idx)
        return self.holding

    def insert_foundation(self, card, origin):
        self.holding = None
        self.origin = None

        if len(self.tail) < 1:
            if self._foundation.add(card):
                self.new_game = False
                self.moves += 1

                if origin == FOUNDATION:
                    pass

                elif origin == CURRENT_STOCK:
                    self._stock.current = self._stock.waste.get_last()

                else:
                    self._tableau.cells[origin] = 0
                    if (origin[0], origin[1] - 1) in self.face_down:
                        self.face_down.remove((origin[0], origin[1] - 1))
                return True
        return False

    def get_card_tail(self):
        arr = []
        if len(self.tail) > 0:
            for n in range(len(self.tail)):
                arr.append(self.tail[n][0])
            return arr
        return False

    def set_tail(self, x, y):  # **
        cells = self._tableau.cells
        self.tail = []

        for i in range(y, 20):
            if (x, i) in cells:
                if cells[(x, i)] and i != y:
                    self.tail.append((cells[(x, i)], (x, i)))
        return self.tail

    def move_tail(self, origin, dest):
        cells = self._tableau.cells

        arr = []
        for i, card in enumerate(self.tail, 1):
            cells[dest[0], dest[1] + i] = (card[0])
            cells[origin[0], origin[1] + i] = 0

            arr.append((dest[0], dest[1] + i))

        return arr

    def in_tail(self, pos):
        for card, p in self.tail:
            if p == pos:
                return True
        return False

    def check_auto_complete(self):
        if self.stock_is_empty() and \
                self._stock.waste.height == 0:
            for pos in [(x, 0) for x in range(1, 7)]:
                if pos in self.face_down:
                    return False
            return True

    def auto_complete(self, remaining):
        t = self._tableau

        for card, pos in remaining:

            if self.get_current_stock():
                self.insert_foundation(self.get_current_stock(), self.origin)

            if pos in t.cells and \
                    len(self.set_tail(pos[0], pos[1])) == 0:
                if self.insert_foundation(t.cells[pos], pos):
                    t.cells[pos] = 0
                    return card
                else:
                    continue
        return False

    def check_win(self):
        return self._foundation.check_win()

    @property
    def deck(self):
        return self._deck
