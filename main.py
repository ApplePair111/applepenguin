from uci_wrapper import UCIEngine
import sys
import chess.pgn
import chess.polyglot
import chess.engine
import glob

pattern_db = {}   # zobrist_hash -> { move_uci: count }

for filename in glob.glob("chessgames/game*.pgn"):
    with open(filename) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            board = game.board()
            for move in game.mainline_moves():
                key = chess.polyglot.zobrist_hash(board)   # hash of position BEFORE the move
                move_str = move.uci()

                if key not in pattern_db:
                    pattern_db[key] = {}
                pattern_db[key][move_str] = pattern_db[key].get(move_str, 0) + 1

                board.push(move)   # now advance

print(pattern_db)