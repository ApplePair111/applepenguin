from uci_wrapper import UCIEngine
import pickle
import chess
import chess.engine
from decidemove import decide_move
from pathlib import Path



STOCKFISH_PATH = Path(__file__).resolve().parent / "stockfish-bin" / "stockfish"   # check with: which stockfish

# load your pattern DB
with open("pattern_db.pkl", "rb") as f:
    pattern_db = pickle.load(f)

# start Stockfish
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) # type: ignore

uciengine = UCIEngine("ApplePenguin", "ApplePair111", decide_move, None, (pattern_db, engine), None)
uciengine.run()

# a board to test on — starting position
#board = chess.Board()

#move = decide_move(board, pattern_db, engine)
#print("Chosen move:", move.uci())

engine.quit()