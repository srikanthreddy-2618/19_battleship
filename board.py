class Board:
    """Battleship board. All coordinates are 0-based (row, col) tuples."""

    SIZE = 6

    MISS = "miss"
    HIT = "hit"
    SUNK = "sunk"

    def __init__(self):
        self.fleet = []        # list of frozensets, one per ship
        self.shots = set()     # every (row, col) fired at this board

    # ---- helpers -------------------------------------------------------
    @classmethod
    def in_bounds(cls, pos):
        return (
            isinstance(pos, tuple) and len(pos) == 2
            and all(isinstance(v, int) for v in pos)
            and 0 <= pos[0] < cls.SIZE and 0 <= pos[1] < cls.SIZE
        )

    @property
    def ships(self):
        """All occupied cells (union of every ship)."""
        return set().union(*self.fleet) if self.fleet else set()

    # ---- setup ---------------------------------------------------------
    def place_ship(self, cells):
        cells = frozenset(cells)
        if not cells:
            raise ValueError("A ship needs at least one cell.")
        if not all(self.in_bounds(c) for c in cells):
            raise ValueError("Ship cell outside the board.")
        if cells & self.ships:
            raise ValueError("Ships may not overlap.")
        self.fleet.append(cells)

    # ---- shooting ------------------------------------------------------
    def ship_at(self, pos):
        for ship in self.fleet:
            if pos in ship:
                return ship
        return None

    def is_sunk(self, ship):
        return ship <= self.shots

    def fire(self, pos):
        """Fire at pos. Returns Board.MISS, Board.HIT or Board.SUNK.

        Raises ValueError for out-of-bounds or repeated shots.
        """
        if not self.in_bounds(pos):
            raise ValueError("Outside board.")
        if pos in self.shots:
            raise ValueError("Already fired there.")
        self.shots.add(pos)
        ship = self.ship_at(pos)
        if ship is None:
            return self.MISS
        return self.SUNK if self.is_sunk(ship) else self.HIT

    def sunk_ship_at(self, pos):
        """The sunk ship containing pos, or None."""
        ship = self.ship_at(pos)
        return ship if ship is not None and self.is_sunk(ship) else None

    def ships_remaining(self):
        return sum(1 for s in self.fleet if not self.is_sunk(s))

    def all_sunk(self):
        return bool(self.fleet) and all(self.is_sunk(s) for s in self.fleet)
