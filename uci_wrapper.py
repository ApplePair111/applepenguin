# uci_wrapper.py
"""
Minimal UCI protocol handler, importable as a library.
Your main script provides a `decide_move(board) -> chess.Move` callback,
and this handles all the stdin/stdout/UCI plumbing around it.
"""

import sys
import chess


class UCIEngine:
    def __init__(self, name: str, author: str, decide_move_fn, on_new_game=None):
        """
        name, author        -> shown to the GUI via 'id name' / 'id author'
        decide_move_fn       -> callable(board: chess.Board) -> chess.Move
        on_new_game          -> optional callable(), called on 'ucinewgame'
        """
        self.name = name
        self.author = author
        self.decide_move_fn = decide_move_fn
        self.on_new_game = on_new_game
        self.board = chess.Board()

    def run(self):
        """Blocking loop — call this from your main script's entrypoint."""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            if line == "uci":
                self._handle_uci()
            elif line == "isready":
                self._send("readyok")
            elif line == "ucinewgame":
                self.board.reset()
                if self.on_new_game:
                    self.on_new_game()
            elif line.startswith("position"):
                self._handle_position(line)
            elif line.startswith("go"):
                self._handle_go(line)
            elif line == "quit":
                break
            elif line == "stop":
                pass  # no background search to interrupt in a synchronous engine

    def _send(self, text: str):
        print(text)
        sys.stdout.flush()

    def _handle_uci(self):
        self._send(f"id name {self.name}")
        self._send(f"id author {self.author}")
        self._send("uciok")

    def _handle_position(self, line: str):
        parts = line.split()
        if len(parts) < 2:
            return

        if parts[1] == "startpos":
            self.board.reset()
            idx = 2
        elif parts[1] == "fen":
            fen = " ".join(parts[2:8])
            self.board.set_fen(fen)
            idx = 8
        else:
            return

        if len(parts) > idx and parts[idx] == "moves":
            for uci_move in parts[idx + 1:]:
                self.board.push_uci(uci_move)

    def _handle_go(self, line: str):
        # parse go params if you want time management later, e.g.:
        # tokens = line.split()
        # if "movetime" in tokens: ...
        move = self.decide_move_fn(self.board)
        self._send(f"bestmove {move.uci()}")