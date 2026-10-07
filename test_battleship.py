import io, unittest
from unittest import mock
from board import Board
from ai import AI
from game import Battleship


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.b = Board()
        self.b.place_ship({(0, 0), (0, 1)})
        self.b.place_ship({(3, 3)})

    def test_hit_and_miss(self):
        self.assertEqual(self.b.fire((0, 0)), Board.HIT)
        self.assertEqual(self.b.fire((5, 5)), Board.MISS)

    def test_every_ship_cell_hits_every_empty_cell_misses(self):
        for r in range(Board.SIZE):
            for c in range(Board.SIZE):
                b = Board(); b.place_ship({(0, 0), (0, 1)}); b.place_ship({(3, 3)})
                res = b.fire((r, c))
                self.assertEqual(res != Board.MISS, (r, c) in {(0, 0), (0, 1), (3, 3)})

    def test_repeat_shot_rejected(self):
        self.b.fire((1, 1))
        with self.assertRaises(ValueError):
            self.b.fire((1, 1))

    def test_out_of_bounds(self):
        for p in ((-1, 0), (0, 6), (6, 6)):
            with self.assertRaises(ValueError):
                self.b.fire(p)

    def test_sink_one_then_all(self):
        self.assertEqual(self.b.fire((3, 3)), Board.SUNK)
        self.assertFalse(self.b.all_sunk())
        self.assertEqual(self.b.ships_remaining(), 1)
        self.assertEqual(self.b.fire((0, 0)), Board.HIT)
        self.assertEqual(self.b.fire((0, 1)), Board.SUNK)
        self.assertTrue(self.b.all_sunk())

    def test_overlap_and_bounds_on_place(self):
        with self.assertRaises(ValueError): self.b.place_ship({(0, 0)})
        with self.assertRaises(ValueError): self.b.place_ship({(9, 9)})

    def test_empty_board_not_sunk(self):
        self.assertFalse(Board().all_sunk())


class AITests(unittest.TestCase):
    def test_never_repeats_and_handles_exhaustion(self):
        ai = AI(6)
        shots = [ai.choose() for _ in range(36)]
        self.assertEqual(len(set(shots)), 36)
        self.assertIsNone(ai.choose())

    def test_adjacent_after_hit(self):
        for _ in range(30):
            ai = AI(6)
            ai.tried.add((2, 2))
            ai.report((2, 2), "hit")
            nxt = ai.choose()
            self.assertEqual(abs(nxt[0] - 2) + abs(nxt[1] - 2), 1)

    def test_corner_hit_stays_in_bounds(self):
        ai = AI(6); ai.tried.add((0, 0)); ai.report((0, 0), "hit")
        self.assertIn(ai.choose(), {(0, 1), (1, 0)})

    def test_choose_prints_nothing(self):
        with mock.patch("sys.stdout", new=io.StringIO()) as out:
            AI().choose()
        self.assertEqual(out.getvalue(), "")

    def test_returns_tuple(self):
        self.assertIsInstance(AI().choose(), tuple)


class GameTests(unittest.TestCase):
    def run_game(self, inputs):
        g = Battleship()
        with mock.patch("builtins.input", side_effect=inputs),              mock.patch("sys.stdout", new=io.StringIO()) as out:
            g.run()
        return g, out.getvalue()

    def test_quit(self):
        _, out = self.run_game(["q"])
        self.assertNotIn("HIT", out)

    def test_invalid_inputs(self):
        _, out = self.run_game(["abc", "1", "1,2,3", "0,1", "7,7", "-1,2", "", "q"])
        self.assertEqual(out.count("Use row,col."), 4)
        self.assertEqual(out.count("Outside board."), 3)
        self.assertNotIn("MISS", out)

    def test_repeat_shot_message_and_no_ai_move(self):
        _, out = self.run_game(["1,1", "1,1", "q"])
        self.assertIn("Already fired there.", out)
        self.assertEqual(out.count("AI fired at"), 1)

    def test_one_feedback_per_shot(self):
        _, out = self.run_game(["1,1", "q"])
        self.assertEqual(out.count("MISS!") + out.count("HIT!"), 2)  # player + AI shot

    def test_player_wins(self):
        cells = ["3,3", "3,4", "3,5", "5,1", "6,1", "1,6", "2,6"]
        with mock.patch("ai.AI.choose", return_value=None):
            g, out = self.run_game(cells)
        self.assertIn("You sank the fleet.", out)
        self.assertIn("sunk a ship", out)

    def test_ai_hits_recognised_and_ai_can_win(self):
        targets = sorted(Battleship().player.ships)
        with mock.patch("ai.AI.choose", side_effect=targets):
            g, out = self.run_game(["1,1", "1,2", "1,3", "1,4", "1,5", "2,1", "2,2",
                                    "2,3", "2,4", "2,5", "3,1", "3,2"])
        self.assertEqual(out.count("AI fired at"), len(targets))
        self.assertNotIn("AI MISS", out)
        self.assertIn("The AI sank your fleet", out)

    def test_ai_full_game_no_repeats(self):
        g = Battleship()
        seen = set()
        with mock.patch("sys.stdout", new=io.StringIO()):
            while not g.player.all_sunk():
                p = g.ai_turn()
                self.assertNotIn(p, seen); seen.add(p)


if __name__ == "__main__":
    unittest.main()
