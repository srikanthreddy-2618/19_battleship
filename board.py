class Board:
    SIZE = 6

    def __init__(self):
        self.ships = []
        self.shots = set()

    def place_ship(self, cells, name=None):
        cells = set(cells)
        if not cells:
            raise ValueError("A ship must contain at least one cell.")
        if any(not (0 <= r < self.SIZE and 0 <= c < self.SIZE) for r, c in cells):
            raise ValueError("Ship contains a cell outside the board.")
        if any(cells & ship["cells"] for ship in self.ships):
            raise ValueError("Ships cannot overlap.")
        self.ships.append({
            "name": name or f"Ship {len(self.ships) + 1}",
            "cells": cells,
            "hits": set(),
        })

    def fire(self, pos):
        if pos in self.shots:
            return {"status": "repeat", "ship": None}
        self.shots.add(pos)
        for ship in self.ships:
            if pos in ship["cells"]:
                ship["hits"].add(pos)
                if ship["cells"] == ship["hits"]:
                    return {"status": "sunk", "ship": ship["name"]}
                return {"status": "hit", "ship": ship["name"]}
        return {"status": "miss", "ship": None}

    def all_sunk(self):
        return bool(self.ships) and all(ship["cells"] <= ship["hits"] for ship in self.ships)

    def remaining_cells(self):
        return sum(len(ship["cells"] - ship["hits"]) for ship in self.ships)

    def is_valid(self, pos):
        r, c = pos
        return 0 <= r < self.SIZE and 0 <= c < self.SIZE
