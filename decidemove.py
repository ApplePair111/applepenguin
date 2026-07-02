import chess
import chess.engine
import chess.polyglot


def decide_move(board: chess.Board, pattern_db: dict, engine: chess.engine.SimpleEngine,
                 blunder_threshold_cp: int = 100, depth: int = 15) -> chess.Move:
    """
    1. Look up current position in pattern_db.
    2. If found, take the most-played continuation.
    3. Validate it with Stockfish (root_moves trick) against Stockfish's actual best move.
    4. If it's within blunder_threshold_cp of the best move -> play it (pattern mode).
    5. Otherwise (no pattern found, OR pattern move is a blunder) -> play Stockfish's best move.
    """
    key = chess.polyglot.zobrist_hash(board)

    if key in pattern_db:
        moves_seen = pattern_db[key]                          # {move_uci: count}
        candidate_uci = max(moves_seen, key=moves_seen.get)    # most common continuation
        candidate_move = chess.Move.from_uci(candidate_uci)

        if candidate_move in board.legal_moves:
            # get Stockfish's actual best move + its eval
            best_info = engine.analyse(board, chess.engine.Limit(depth=depth))
            best_score = best_info["score"].pov(board.turn) # type: ignore
            best_move = best_info["pv"][0] # type: ignore

            # get eval of just the candidate move
            cand_info = engine.analyse(board, chess.engine.Limit(depth=depth), root_moves=[candidate_move])
            cand_score = cand_info["score"].pov(board.turn) # type: ignore

            loss = _centipawn_loss(best_score, cand_score)

            if loss < blunder_threshold_cp:
                print(f"[pattern] playing {candidate_uci} (loss={loss}cp)")
                return candidate_move
            else:
                print(f"[pattern->override] {candidate_uci} was a blunder (loss={loss}cp), playing {best_move.uci()} instead")
                return best_move

    # no pattern hit -> full Stockfish
    result = engine.play(board, chess.engine.Limit(depth=depth))
    print(f"[engine] no pattern match, playing {result.move.uci()}") # type: ignore
    return result.move # type: ignore


def _centipawn_loss(best_score: chess.engine.Score, cand_score: chess.engine.Score) -> int:
    def to_cp(score: chess.engine.Score) -> int:
        if score.is_mate():
            mate_in = score.mate()
            return 10000 if mate_in > 0 else -10000 # type: ignore
        return score.score() # type: ignore
    return to_cp(best_score) - to_cp(cand_score)