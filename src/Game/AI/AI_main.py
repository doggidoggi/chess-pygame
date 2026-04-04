import math
import os
import random
from pathlib import Path
from typing import Optional

from src.constants import BLACK, WHITE, PROJECT_DIR
from src.Game.Pieces.Bishop import Bishop
from src.Game.Pieces.King import King
from src.Game.Pieces.Knight import Knight
from src.Game.Pieces.Pawn import Pawn
from src.Game.Pieces.Queen import Queen
from src.Game.Pieces.Rook import Rook

AI_SEARCH_DEPTH = 3
CHECKMATE_SCORE = 100_000
QUIESCENCE_LIMIT = 8

PIECE_VALUES = {
    'Pawn': 100,
    'Knight': 320,
    'Bishop': 330,
    'Rook': 500,
    'Queen': 900,
    'King': 20_000,
}

PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_TABLE = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

PIECE_SQUARE_TABLES = {
    'Pawn': PAWN_TABLE,
    'Knight': KNIGHT_TABLE,
    'Bishop': BISHOP_TABLE,
    'Rook': ROOK_TABLE,
    'Queen': QUEEN_TABLE,
    'King': KING_TABLE,
}

AI_MODE_AUTO = 'auto'
AI_MODE_CLASSIC = 'classic'
AI_MODE_SELF_LEARNING = 'self_learning'

_DEFAULT_MODEL_CANDIDATES = (
    lambda: os.environ.get('CHESS_AI_CHECKPOINT'),
    lambda: str(PROJECT_DIR / 'models' / 'chess_value_net_latest.pt'),
    lambda: str(PROJECT_DIR / 'models' / 'generation_latest.pt'),
    lambda: str(PROJECT_DIR / 'assets' / 'models' / 'chess_value_net_latest.pt'),
)

_TRAINED_AI_CACHE = None
_TRAINED_AI_CACHE_KEY = None
_TRAINED_AI_IMPORT_ERROR = None


def get_piece_value(piece):
    if piece is None:
        return 0
    return PIECE_VALUES.get(piece.piece_type, 0)


def get_piece_square_value(piece, row, column):
    table = PIECE_SQUARE_TABLES.get(piece.piece_type)
    if table is None:
        return 0
    if piece.piece_color == WHITE:
        return table[row][column]
    return table[7 - row][column]


def evaluate_board(board):
    score = 0
    white_bishops = 0
    black_bishops = 0

    for row in range(len(board.board)):
        for column in range(len(board.board[row])):
            piece = board.board[row][column]
            if piece is None:
                continue

            piece_score = get_piece_value(piece) + get_piece_square_value(piece,
                                                                          row,
                                                                          column)

            if piece.piece_color == WHITE:
                score += piece_score
                if isinstance(piece, Bishop):
                    white_bishops += 1
            else:
                score -= piece_score
                if isinstance(piece, Bishop):
                    black_bishops += 1

            if isinstance(piece, Pawn):
                if piece.piece_color == WHITE:
                    score += max(0, 6 - row) * 3
                else:
                    score -= max(0, row - 1) * 3
            elif isinstance(piece, Knight):
                if 2 <= row <= 5 and 2 <= column <= 5:
                    score += 12 if piece.piece_color == WHITE else -12
            elif isinstance(piece, Rook):
                if column in (3, 4):
                    score += 8 if piece.piece_color == WHITE else -8

    if white_bishops >= 2:
        score += 30
    if black_bishops >= 2:
        score -= 30

    return score


def auto_promote_pending_pawn(board):
    if not board.piece_to_promote:
        return

    row, column = board.piece_to_promote
    piece = board.board[row][column]
    if isinstance(piece, Pawn):
        promoted_piece = Queen(piece.piece_color)
        promoted_piece.moved = True
        board.board[row][column] = promoted_piece
    board.piece_to_promote = ()


def apply_ai_move(board, move):
    if move is None:
        return None
    board.make_move(move)
    auto_promote_pending_pawn(board)
    return move


def score_move(move):
    score = 0

    if move.capturedPiece is not None:
        score += 10 * get_piece_value(move.capturedPiece) - get_piece_value(
            move.movedPiece)

    if move.is_en_passant_move:
        score += 105

    if move.is_promotion_move:
        score += 800

    if move.is_castle_move:
        score += 60

    center_distance = abs(3.5 - move.endRow) + abs(3.5 - move.endColumn)
    score += int((7 - center_distance) * 3)

    return score


def order_moves(valid_moves):
    return sorted(valid_moves, key=score_move, reverse=True)


def quiescence_search(board, alpha, beta, color_multiplier,
                      depth_left=QUIESCENCE_LIMIT):
    stand_pat = color_multiplier * evaluate_board(board)

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    if depth_left <= 0:
        return alpha

    tactical_moves = [
        move for move in board.getValidMoves()
        if
        move.capturedPiece is not None or move.is_en_passant_move or move.is_promotion_move
    ]

    for move in order_moves(tactical_moves):
        apply_ai_move(board, move)
        score = -quiescence_search(board, -beta, -alpha, -color_multiplier,
                                   depth_left - 1)
        board.undoMove()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def negamax(board, depth, alpha, beta, color_multiplier, ply=0):
    valid_moves = board.getValidMoves()

    if not valid_moves:
        if board.inCheck():
            return -CHECKMATE_SCORE + ply
        return 0

    if depth == 0:
        return quiescence_search(board, alpha, beta, color_multiplier)

    best_score = -math.inf

    for move in order_moves(valid_moves):
        apply_ai_move(board, move)
        score = -negamax(board, depth - 1, -beta, -alpha, -color_multiplier,
                         ply + 1)
        board.undoMove()

        if score > best_score:
            best_score = score
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break

    return best_score


def _resolve_checkpoint_path(checkpoint_path: Optional[str | os.PathLike[str]] = None) -> Optional[Path]:
    if checkpoint_path is not None:
        path = Path(checkpoint_path)
        return path if path.is_file() else None

    for candidate_factory in _DEFAULT_MODEL_CANDIDATES:
        candidate = candidate_factory()
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file():
            return path
    return None


def _build_trained_ai(depth: int = AI_SEARCH_DEPTH, checkpoint_path: Optional[str | os.PathLike[str]] = None):
    global _TRAINED_AI_IMPORT_ERROR

    resolved_checkpoint = _resolve_checkpoint_path(checkpoint_path)
    if resolved_checkpoint is None:
        return None, None

    try:
        import torch
        from src.Game.AI.chess_encoder import BoardEncoder
        from src.Game.AI.self_learning_ai import (
            ChessValueNet,
            HeuristicEvaluator,
            HybridEvaluator,
            NeuralEvaluator,
            SearchConfig,
            SelfLearningChessAI,
        )
    except Exception as exc:
        _TRAINED_AI_IMPORT_ERROR = exc
        return None, None

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    checkpoint = torch.load(resolved_checkpoint, map_location=device)

    model = ChessValueNet()
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    encoder = BoardEncoder()
    neural = NeuralEvaluator(model, encoder, device=device)
    evaluator = HybridEvaluator(neural, HeuristicEvaluator(), neural_weight=0.75)
    ai = SelfLearningChessAI(
        evaluator,
        search_config=SearchConfig(depth=depth, quiescence_limit=min(QUIESCENCE_LIMIT, 4)),
    )
    return ai, resolved_checkpoint


def get_trained_ai(depth: int = AI_SEARCH_DEPTH, checkpoint_path: Optional[str | os.PathLike[str]] = None):
    global _TRAINED_AI_CACHE, _TRAINED_AI_CACHE_KEY

    cache_key = (depth, str(_resolve_checkpoint_path(checkpoint_path) or ''))
    if _TRAINED_AI_CACHE is not None and _TRAINED_AI_CACHE_KEY == cache_key:
        return _TRAINED_AI_CACHE

    ai, resolved_checkpoint = _build_trained_ai(depth=depth, checkpoint_path=checkpoint_path)
    if ai is None:
        return None

    _TRAINED_AI_CACHE = ai
    _TRAINED_AI_CACHE_KEY = (depth, str(resolved_checkpoint))
    return _TRAINED_AI_CACHE


def reload_trained_ai(depth: int = AI_SEARCH_DEPTH, checkpoint_path: Optional[str | os.PathLike[str]] = None):
    global _TRAINED_AI_CACHE, _TRAINED_AI_CACHE_KEY
    _TRAINED_AI_CACHE = None
    _TRAINED_AI_CACHE_KEY = None
    return get_trained_ai(depth=depth, checkpoint_path=checkpoint_path)


def has_trained_ai(checkpoint_path: Optional[str | os.PathLike[str]] = None) -> bool:
    return _resolve_checkpoint_path(checkpoint_path) is not None


def find_best_move_classic(board, valid_moves=None, depth=AI_SEARCH_DEPTH):
    candidate_moves = list(
        valid_moves) if valid_moves is not None else board.getValidMoves()
    if not candidate_moves:
        return None
    if len(candidate_moves) == 1:
        return candidate_moves[0]

    ordered_moves = order_moves(candidate_moves)
    color_multiplier = 1 if board.whiteMove else -1

    best_score = -math.inf
    best_move = random.choice(ordered_moves[:min(2, len(ordered_moves))])

    alpha = -math.inf
    beta = math.inf

    for move in ordered_moves:
        apply_ai_move(board, move)
        score = -negamax(board, depth - 1, -beta, -alpha, -color_multiplier, 1)
        board.undoMove()

        if score > best_score:
            best_score = score
            best_move = move

        if score > alpha:
            alpha = score

    return best_move


def find_best_move_self_learning(
    board,
    valid_moves=None,
    depth=AI_SEARCH_DEPTH,
    checkpoint_path=None,
    fallback_to_classic=True,
):
    trained_ai = get_trained_ai(depth=depth, checkpoint_path=checkpoint_path)
    if trained_ai is not None:
        move = trained_ai.choose_move(board, valid_moves=valid_moves)
        if move is not None:
            return move

    if fallback_to_classic:
        return find_best_move_classic(board, valid_moves=valid_moves, depth=depth)
    return None


def find_best_move_with_mode(
    board,
    valid_moves=None,
    depth=AI_SEARCH_DEPTH,
    ai_mode=AI_MODE_AUTO,
    checkpoint_path=None,
    fallback_to_classic=True,
):
    if ai_mode == AI_MODE_CLASSIC:
        return find_best_move_classic(board, valid_moves=valid_moves, depth=depth)

    if ai_mode == AI_MODE_SELF_LEARNING:
        return find_best_move_self_learning(
            board,
            valid_moves=valid_moves,
            depth=depth,
            checkpoint_path=checkpoint_path,
            fallback_to_classic=fallback_to_classic,
        )

    return find_best_move_self_learning(
        board,
        valid_moves=valid_moves,
        depth=depth,
        checkpoint_path=checkpoint_path,
        fallback_to_classic=True,
    )


def find_best_move(board, valid_moves=None, depth=AI_SEARCH_DEPTH, checkpoint_path=None):
    return find_best_move_with_mode(
        board,
        valid_moves=valid_moves,
        depth=depth,
        ai_mode=AI_MODE_AUTO,
        checkpoint_path=checkpoint_path,
        fallback_to_classic=True,
    )
