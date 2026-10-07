from board import Board
from ai import AI


class Battleship:
    def __init__(self):
        self.player = Board()   # the human's own ships (AI fires here)
        self.enemy = Board()    # the AI's ships (human fires here)
        self.ai = AI(Board.SIZE)
        self._setup()

    def _setup(self):
        # Internal coordinates are 0-based (row, col); the player types 1-based.
        for cells in ({(1, 1), (1, 2), (1, 3)}, {(3, 3), (4, 3)}, {(5, 0), (5, 1)}):
            self.player.place_ship(cells)
        for cells in ({(2, 2), (2, 3), (2, 4)}, {(4, 0), (5, 0)}, {(0, 5), (1, 5)}):
            self.enemy.place_ship(cells)

    def show(self):
        print("\nYour shots are coordinates like 2,3 (row,col, 1-%d). 'q' quits." % Board.SIZE)
        print("Enemy ships left:", self.enemy.ships_remaining(),
              "| Ship cells remaining:", len(self.enemy.ships - self.enemy.shots))
        for r in range(Board.SIZE):
            row = ""
            for c in range(Board.SIZE):
                if (r, c) in self.enemy.shots:
                    row += "X " if (r, c) in self.enemy.ships else "o "
                else:
                    row += ". "
            print("  " + row)

    @staticmethod
    def parse(raw):
        """'r,c' (1-based) -> 0-based (row, col); raises ValueError if bad."""
        parts = raw.split(",")
        if len(parts) != 2:
            raise ValueError("Use row,col.")
        r, c = (int(p.strip()) for p in parts)
        pos = (r - 1, c - 1)
        if not Board.in_bounds(pos):
            raise ValueError("Outside board.")
        return pos

    @staticmethod
    def announce(result, who="You"):
        if result == Board.SUNK:
            print("HIT! %s sunk a ship!" % who)
        elif result == Board.HIT:
            print("HIT!")
        else:
            print("MISS!")

    def player_turn(self, pos):
        """Fire at the enemy. Returns the result; raises ValueError if illegal."""
        result = self.enemy.fire(pos)
        self.announce(result)
        return result

    def ai_turn(self):
        """AI fires at the player's board. Returns the shot or None."""
        pos = self.ai.choose()
        if pos is None:
            print("AI has no cells left to fire at.")
            return None
        result = self.player.fire(pos)
        print("AI fired at %d,%d" % (pos[0] + 1, pos[1] + 1))
        self.announce(result, who="AI")
        self.ai.report(pos, result, self.player.sunk_ship_at(pos))
        return pos

    def run(self):
        print("Battleship")
        while True:
            self.show()
            try:
                raw = input("> ").strip().lower()
            except EOFError:
                return
            if raw in ("q", "quit"):
                return
            try:
                pos = self.parse(raw)
            except ValueError as e:
                print(e if str(e) in ("Use row,col.", "Outside board.") else "Use row,col.")
                continue
            try:
                self.player_turn(pos)
            except ValueError as e:
                print(e)
                continue
            if self.enemy.all_sunk():
                print("You sank the fleet.")
                return
            self.ai_turn()
            if self.player.all_sunk():
                print("The AI sank your fleet. You lose.")
                return
