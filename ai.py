import random


class AI:
    """Computer opponent. Coordinates are 0-based (row, col) tuples."""

    def __init__(self, size=6):
        self.size = size
        self.tried = set()
        self.pending_hits = set()   # hits on ships not yet known to be sunk
        self.targets = []           # untried cells next to hits (LIFO)

    def _neighbours(self, pos):
        r, c = pos
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            n = (r + dr, c + dc)
            if 0 <= n[0] < self.size and 0 <= n[1] < self.size and n not in self.tried:
                yield n

    def choose(self):
        """Return an untried (row, col), or None if the board is exhausted.

        Pure selection: prints nothing and does not decide hit/miss.
        """
        while self.targets:
            pos = self.targets.pop()
            if pos not in self.tried:
                self.tried.add(pos)
                return pos
        options = [(r, c) for r in range(self.size) for c in range(self.size)
                   if (r, c) not in self.tried]
        if not options:
            return None
        pos = random.choice(options)
        self.tried.add(pos)
        return pos

    def report(self, pos, result, sunk_cells=None):
        """Tell the AI what its shot did ('hit', 'sunk' or 'miss')."""
        if result == "miss":
            return
        self.pending_hits.add(pos)
        if result == "sunk" and sunk_cells:
            self.pending_hits -= set(sunk_cells)
        # Rebuild targets from unresolved hits; newest hit's neighbours last
        # so they are tried first.
        self.targets = []
        queued = set()
        for hit in sorted(self.pending_hits, key=lambda h: h == pos):
            for n in self._neighbours(hit):
                if n not in queued:
                    queued.add(n)
                    self.targets.append(n)
