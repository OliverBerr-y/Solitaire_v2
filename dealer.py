from playing_cards import Deck, Card
from board import Tableau, Stock, Foundation

# String Constants
CURRENT_STOCK = 'current_stock'
FOUNDATION = 'foundation'
TABLEAU = 'tableau'
STOCK = 'stock'

AUTO_FLIP_CHECK = [(1, 0), (2, 0), (3, 0),
                   (4, 0), (5, 0), (6, 0)]


# Handles gui.py and board.py interactions
class Dealer:
    def __init__(self):
        self._deck = Deck()
        self._deck.shuffle()

        self._foundation = Foundation()
        self._tableau = Tableau()
        self._stock = Stock(self._deck)

        self.current = None
        self.current_pos = None
        self.tail = []
        self.face_down = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
                          (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
                          (3, 2), (4, 2), (5, 2), (6, 2),
                          (4, 3), (5, 3), (6, 3),
                          (5, 4), (6, 4),
                          (6, 5)]

        self.auto = False

    def deal(self):
        return self._tableau.deal(self._stock.draw())

    def new_card(self):
        return self._stock.flip()

    def check_waste(self):
        return self._stock.waste.height >= 1

    def stock_is_empty(self):
        return self._stock.is_empty()

    def look_current_stock(self):
        return self._stock.current

    def get_current_stock(self):
        if self._stock.current:
            self.current = self._stock.current
            self.current_pos = CURRENT_STOCK
        return self._stock.current

    def get_card_from_tableau(self, pos):
        if self.current:
            return self.current

        cells = self._tableau.cells

        if pos:
            if pos not in self.face_down:
                if cells[pos] != 0:
                    self.current = cells[pos]
                    self.current_pos = pos
                    self.set_tail(pos[0], pos[1])
                    return cells[pos]
            if cells[pos] == 0:
                for i in range(8):
                    (x, y) = (pos[0], pos[1] - i)
                    if (x, y) in cells:
                        if (x, y) not in self.face_down:
                            if cells[(x, y)]:
                                self.current = cells[(x, y)]
                                self.current_pos = (x, y)
                                self.set_tail(x, y)
                                return cells[(x, y)]
        self.current = None
        self.current_pos = None
        return False

    def move_to_tableau(self, origin, dest):
        if origin == CURRENT_STOCK:
            success = self.misc_to_tableau(self.current, dest)
            if success:
                self._stock.current = self._stock.waste.get_last()
                return True

        elif origin == FOUNDATION:
            success = self.misc_to_tableau(self.current, dest)
            if success:
                return True

        else:
            success = self.tableau_to_tableau(origin, dest)
            self.tail = []
            if success:
                if (origin[0], origin[1] - 1) in self.face_down:
                    self.face_down.remove((origin[0], origin[1] - 1))
                self.current = None
                self.current_pos = None
                return True
        return False

    def tableau_to_tableau(self, origin: (int, int), dest: (int, int)):
        t = self._tableau

        if dest:
            x = dest[0]
            y = dest[1]

            if origin in t.cells.keys():
                c = t.cells[origin]

                if dest in t.cells.keys() and t.cells[x, y + 1] == 0:
                    for i in range(8):
                        if (x, y - i) in t.cells.keys() and (x, y - i + 1) != origin:
                            if t.cells[(x, y - i)] != 0 and (x, y - i) not in self.face_down:
                                if t.check_move(c, t.cells[(x, y - i)]):
                                    t.cells[(x, y - i + 1)] = c
                                    self.tail = self.move_tail(origin, (x, y - i + 2))
                                    return True, i
                                else:
                                    return False

                if c and dest in t.cells.keys():
                    if c.rank == 13 and t.cells[x, 0] == 0:
                        for i in range(8):
                            if (x, y - i) not in t.cells.keys():
                                t.cells[(x, y - i + 1)] = c
                                t.cells[origin] = 0
                                self.tail = self.move_tail(origin, (x, y - i + 2))
                                return True, i
        return False

    def misc_to_tableau(self, c: Card, dest: (int, int)):
        t = self._tableau

        if dest:
            x = dest[0]
            y = dest[1]

            if dest in t.cells.keys() and t.cells[x, y + 1] == 0:
                for i in range(8):
                    if (x, y - i) in t.cells:
                        if t.cells[(x, y - i)] != 0:
                            if t.check_move(c, t.cells[(x, y - i)]):
                                t.cells[(x, y - i + 1)] = c
                                return True, i
                            else:
                                return False

            if dest in t.cells.keys():
                if c.rank == 13 and t.cells[x, 0] == 0:
                    for i in range(8):
                        if (x, y - i) not in t.cells.keys():
                            t.cells[x, y - i + 1] = c
                            return True, i
        return False

    def get_current_foundation(self):
        return self._foundation.look_top_cards()

    def get_card_from_foundation(self, idx: int):
        self.current_pos = FOUNDATION
        self.current = self._foundation.pop(idx)
        return self.current

    def return_to_foundation(self, card):
        self._foundation.add(card)

    def insert_into_foundation(self, card, origin):
        if len(self.tail) < 1:
            if self._foundation.check_insert(card):
                if origin == CURRENT_STOCK:
                    self._stock.current = self._stock.waste.get_last()
                else:
                    self._tableau.cells[origin] = 0
                    if (origin[0], origin[1] - 1) in self.face_down:
                        self.face_down.remove((origin[0], origin[1] - 1))
                return True
        return False

    def get_cards_tail(self):
        arr = []
        if len(self.tail) > 0:
            for n in range(len(self.tail)):
                arr.append(self.tail[n][0])
            return arr
        return False

    def set_tail(self, x, y):
        cells = self._tableau.cells
        self.tail = []

        for i in range(y, 20):
            if (x, i) in cells.keys():
                if cells[(x, i)] and i != y:
                    self.tail.append((cells[(x, i)], (x, i)))
        return self.tail

    def move_tail(self, pos, dest):
        cells = self._tableau.cells
        arr = []

        count = 0
        for card in self.tail:
            x = dest[0], dest[1] + count
            y = pos[0], pos[1] + count
            cells[x] = (card[0])
            cells[y] = 0
            arr.append(x)
            count += 1

        y = pos[0], pos[1] + count
        cells[y] = 0
        return arr

    def in_tail(self, pos):
        for card, p in self.tail:
            if p == pos:
                return True
        return False

    def check_winnable(self):
        if self.stock_is_empty() and \
                self._stock.waste.height == 0:
            for pos in AUTO_FLIP_CHECK:
                if pos in self.face_down:
                    return False
            return True

    def auto_complete(self, remaining):
        t = self._tableau

        for card, pos in remaining:

            if self.get_current_stock():
                self.insert_into_foundation(self.get_current_stock(), self.current_pos)

            if pos in t.cells.keys() and \
                    len(self.set_tail(pos[0], pos[1])) == 0:
                if self.insert_into_foundation(t.cells[pos], pos):
                    t.cells[pos] = 0
                    return card
                else:
                    continue
        return False

    @property
    def deck(self):
        return self._deck
