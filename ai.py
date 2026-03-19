import copy
import sys
import threading

PIECE_VALUES = {
    "Pawn":   100,
    "Knight": 300,
    "Bishop": 320,
    "Rook":   500,
    "Queen":  900,
    "King":   20000,
}


def evaluate(board, ai_color):
    score = 0
    for piece in board.pieces.values():
        v = PIECE_VALUES.get(piece.name, 0)
        score += v if piece.color == ai_color else -v
    return score


def minimax(board, depth, alpha, beta, maximizing, ai_color, last_move=None):
    human_color = "black" if ai_color == "white" else "white"
    current = ai_color if maximizing else human_color

    if depth == 0:
        return evaluate(board, ai_color), None

    pieces_snapshot = [p for p in board.pieces.values() if p.color == current]
    all_moves = []
    for piece in pieces_snapshot:
        for target in board.get_legal_moves(piece, last_move):
            all_moves.append((piece.pos_tuple(), (target.q, target.r, target.s)))

    if not all_moves:
        if board.is_in_check(current):
            return (-99999 if maximizing else 99999), None
        return 0, None  # stalemate

    best_move = None
    if maximizing:
        best = float("-inf")
        for from_key, to_key in all_moves:
            b2 = copy.deepcopy(board)
            moved = b2.pieces[from_key]
            b2.move_piece(from_key, to_key)
            import hexmath
            new_last = type("Move", (), {
                "piece": b2.pieces[to_key],
                "from_pos": hexmath.Hex(*from_key),
                "to_pos": hexmath.Hex(*to_key),
            })()
            score, _ = minimax(b2, depth - 1, alpha, beta, False, ai_color, new_last)
            if score > best:
                best, best_move = score, (from_key, to_key)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best, best_move
    else:
        best = float("inf")
        for from_key, to_key in all_moves:
            b2 = copy.deepcopy(board)
            b2.move_piece(from_key, to_key)
            import hexmath
            new_last = type("Move", (), {
                "piece": b2.pieces[to_key],
                "from_pos": hexmath.Hex(*from_key),
                "to_pos": hexmath.Hex(*to_key),
            })()
            score, _ = minimax(b2, depth - 1, alpha, beta, True, ai_color, new_last)
            if score < best:
                best, best_move = score, (from_key, to_key)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best, best_move


class AIWorker:
    """Runs minimax on a background thread so the UI stays responsive."""

    def __init__(self):
        self._thread = None
        self.result  = None   # (from_key, to_key) when done
        self.thinking = False

    def start(self, board, ai_color, depth, last_move):
        self.result   = None
        self.thinking = True
        board_copy    = copy.deepcopy(board)

        if sys.platform == "emscripten":
            # WebAssembly: no real threading — run synchronously
            _, move = minimax(board_copy, depth, float("-inf"), float("inf"),
                              True, ai_color, last_move)
            self.result   = move
            self.thinking = False
        else:
            def run():
                _, move = minimax(board_copy, depth, float("-inf"), float("inf"),
                                  True, ai_color, last_move)
                self.result   = move
                self.thinking = False
            self._thread = threading.Thread(target=run, daemon=True)
            self._thread.start()
