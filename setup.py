import chess.pgn
import chess.polyglot
from pathlib import Path
import pickle
import subprocess


fno = 1
gno = 1

pattern_db = {}   # zobrist_hash -> { move_uci: count }

def load_pgn_into_db(filepath, pattern_db, fno):
    with open(filepath, encoding="utf-8", errors="replace") as f:
        print(f"DBG: New File {fno} Loaded!")
        gno = 0
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                print("DBG: File Load Complete!")
                break
            gno += 1
            if gno % 5000 == 0:
                print(f"DBG: New Game {gno} Loaded!")

            board = game.board()
            for move in game.mainline_moves():
                key = chess.polyglot.zobrist_hash(board)
                move_str = move.uci()
                if key not in pattern_db:
                    pattern_db[key] = {}
                pattern_db[key][move_str] = pattern_db[key].get(move_str, 0) + 1
                board.push(move)
    return gno

base = Path(__file__).resolve().parent

load_pgn_into_db(base / "games.pgn", pattern_db, fno=1)
load_pgn_into_db(base / "moregames.pgn", pattern_db, fno=2)
load_pgn_into_db(base / "evenmoregames.pgn", pattern_db, fno=3)


with open(Path(__file__).resolve().parent / "pattern_db.pkl", "wb") as f:
    pickle.dump(pattern_db, f)