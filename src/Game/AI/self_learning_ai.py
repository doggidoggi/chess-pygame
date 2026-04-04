from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

import torch
import torch.nn as nn

from src.constants import BLACK, WHITE
from src.Game.Pieces.Bishop import Bishop
from src.Game.Pieces.Pawn import Pawn
from src.Game.Pieces.Queen import Queen
from src.Game.Pieces.Rook import Rook


AI_SEARCH_DEPTH = 3
CHECKMATE_SCORE = 100_000
QUIESCENCE_LIMIT = 8
DEFAULT_VALUE_SCALE = 1_000.0

PIECE_VALUES = {
    "Pawn": 100,
    "Knight": 320,
    "Bishop": 330,
    "Rook": 500,
    "Queen": 900,
    "King": 20_000,
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
    "Pawn": PAWN_TABLE,
    "Knight": KNIGHT_TABLE,
    "Bishop": BISHOP_TABLE,
    "Rook": ROOK_TABLE,
    "Queen": QUEEN_TABLE,
    "King": KING_TABLE,
}


class BoardProtocol(Protocol):
    board: list[list[object | None]]
    whiteMove: bool
    piece_to_promote: tuple[int, int] | tuple[()]

    def getValidMoves(self) -> list[object]: ...
    def make_move(self, move: object) -> None: ...
    def undoMove(self) -> None: ...
    def inCheck(self) -> bool: ...


class BaseEvaluator(Protocol):
    def evaluate(self, board: BoardProtocol) -> float: ...


class BoardEncoderProtocol(Protocol):
    def encode(self, board: BoardProtocol) -> torch.Tensor: ...


@dataclass(slots=True)
class SearchConfig:
    depth: int = AI_SEARCH_DEPTH
    quiescence_limit: int = QUIESCENCE_LIMIT
    checkmate_score: int = CHECKMATE_SCORE


class HeuristicEvaluator:
    """Текущая ручная оценка. Полезна как baseline и fallback."""

    def evaluate(self, board: BoardProtocol) -> float:
        score = 0.0
        white_bishops = 0
        black_bishops = 0

        for row in range(len(board.board)):
            for column in range(len(board.board[row])):
                piece = board.board[row][column]
                if piece is None:
                    continue

                piece_score = self._get_piece_value(piece) + self._get_piece_square_value(
                    piece,
                    row,
                    column,
                )

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
                elif piece.__class__.__name__ == "Knight":
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

    @staticmethod
    def _get_piece_value(piece: object) -> int:
        return PIECE_VALUES.get(getattr(piece, "piece_type", ""), 0)

    @staticmethod
    def _get_piece_square_value(piece: object, row: int, column: int) -> int:
        table = PIECE_SQUARE_TABLES.get(getattr(piece, "piece_type", ""))
        if table is None:
            return 0
        if getattr(piece, "piece_color", None) == WHITE:
            return table[row][column]
        return table[7 - row][column]


class ChessValueNet(nn.Module):
    """Небольшая value-сеть для self-play обучения."""

    def __init__(self, in_channels: int = 18, hidden_channels: int = 96):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(in_channels, hidden_channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden_channels, hidden_channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden_channels, hidden_channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(hidden_channels, hidden_channels, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        self.value_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(hidden_channels * 8 * 8, 256),
            nn.ReLU(),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        return self.value_head(features)


class NeuralEvaluator:
    """Подключает обучаемую value-сеть к текущему negamax-поиску."""

    def __init__(
        self,
        model: nn.Module,
        encoder: BoardEncoderProtocol,
        *,
        device: str | torch.device = "cpu",
        value_scale: float = DEFAULT_VALUE_SCALE,
    ) -> None:
        self.model = model.to(device)
        self.encoder = encoder
        self.device = torch.device(device)
        self.value_scale = float(value_scale)
        self.model.eval()

    @torch.no_grad()
    def evaluate(self, board: BoardProtocol) -> float:
        encoded = self.encoder.encode(board).unsqueeze(0).to(self.device)
        value = self.model(encoded).squeeze().item()
        return float(value) * self.value_scale


class HybridEvaluator:
    """Смешивает сеть и эвристику. Полезно на ранних этапах обучения."""

    def __init__(
        self,
        neural_evaluator: NeuralEvaluator,
        heuristic_evaluator: Optional[HeuristicEvaluator] = None,
        *,
        neural_weight: float = 0.7,
    ) -> None:
        self.neural_evaluator = neural_evaluator
        self.heuristic_evaluator = heuristic_evaluator or HeuristicEvaluator()
        self.neural_weight = float(neural_weight)

    def evaluate(self, board: BoardProtocol) -> float:
        neural_score = self.neural_evaluator.evaluate(board)
        heuristic_score = self.heuristic_evaluator.evaluate(board)
        return self.neural_weight * neural_score + (1.0 - self.neural_weight) * heuristic_score


class SelfLearningChessAI:
    """Drop-in обертка: использует evaluator и текущий search."""

    def __init__(
        self,
        evaluator: BaseEvaluator,
        *,
        search_config: Optional[SearchConfig] = None,
    ) -> None:
        self.evaluator = evaluator
        self.search_config = search_config or SearchConfig()

    def choose_move(self, board: BoardProtocol, valid_moves: Optional[Iterable[object]] = None) -> object | None:
        return find_best_move(
            board,
            valid_moves=list(valid_moves) if valid_moves is not None else None,
            depth=self.search_config.depth,
            evaluator=self.evaluator,
            search_config=self.search_config,
        )


def auto_promote_pending_pawn(board: BoardProtocol) -> None:
    """
    Важно: board.undoMove() должен корректно откатывать это превращение.
    Если откат ломается, сначала почини историю хода/превращения в Board.
    """
    if not getattr(board, "piece_to_promote", None):
        return

    row, column = board.piece_to_promote
    piece = board.board[row][column]
    if isinstance(piece, Pawn):
        promoted_piece = Queen(piece.piece_color)
        promoted_piece.moved = True
        board.board[row][column] = promoted_piece
    board.piece_to_promote = ()


def apply_ai_move(board: BoardProtocol, move: object) -> object | None:
    if move is None:
        return None
    board.make_move(move)
    auto_promote_pending_pawn(board)
    return move


def get_piece_value(piece: object | None) -> int:
    if piece is None:
        return 0
    return PIECE_VALUES.get(getattr(piece, "piece_type", ""), 0)


def score_move(move: object) -> int:
    score = 0

    captured_piece = getattr(move, "capturedPiece", None)
    moved_piece = getattr(move, "movedPiece", None)

    if captured_piece is not None:
        score += 10 * get_piece_value(captured_piece) - get_piece_value(moved_piece)

    if getattr(move, "is_en_passant_move", False):
        score += 105

    if getattr(move, "is_promotion_move", False):
        score += 800

    if getattr(move, "is_castle_move", False):
        score += 60

    end_row = getattr(move, "endRow", 0)
    end_column = getattr(move, "endColumn", 0)
    center_distance = abs(3.5 - end_row) + abs(3.5 - end_column)
    score += int((7 - center_distance) * 3)

    return score


def order_moves(valid_moves: Iterable[object]) -> list[object]:
    return sorted(valid_moves, key=score_move, reverse=True)


def quiescence_search(
    board: BoardProtocol,
    alpha: float,
    beta: float,
    color_multiplier: int,
    evaluator: BaseEvaluator,
    *,
    depth_left: int,
) -> float:
    stand_pat = color_multiplier * evaluator.evaluate(board)

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    if depth_left <= 0:
        return alpha

    tactical_moves = [
        move
        for move in board.getValidMoves()
        if getattr(move, "capturedPiece", None) is not None
        or getattr(move, "is_en_passant_move", False)
        or getattr(move, "is_promotion_move", False)
    ]

    for move in order_moves(tactical_moves):
        apply_ai_move(board, move)
        score = -quiescence_search(
            board,
            -beta,
            -alpha,
            -color_multiplier,
            evaluator,
            depth_left=depth_left - 1,
        )
        board.undoMove()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def negamax(
    board: BoardProtocol,
    depth: int,
    alpha: float,
    beta: float,
    color_multiplier: int,
    evaluator: BaseEvaluator,
    *,
    ply: int = 0,
    search_config: Optional[SearchConfig] = None,
) -> float:
    config = search_config or SearchConfig()
    valid_moves = board.getValidMoves()

    if not valid_moves:
        if board.inCheck():
            return -config.checkmate_score + ply
        return 0.0

    if depth == 0:
        return quiescence_search(
            board,
            alpha,
            beta,
            color_multiplier,
            evaluator,
            depth_left=config.quiescence_limit,
        )

    best_score = -math.inf

    for move in order_moves(valid_moves):
        apply_ai_move(board, move)
        score = -negamax(
            board,
            depth - 1,
            -beta,
            -alpha,
            -color_multiplier,
            evaluator,
            ply=ply + 1,
            search_config=config,
        )
        board.undoMove()

        if score > best_score:
            best_score = score
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break

    return best_score


def find_best_move(
    board: BoardProtocol,
    valid_moves: Optional[list[object]] = None,
    *,
    depth: int = AI_SEARCH_DEPTH,
    evaluator: Optional[BaseEvaluator] = None,
    search_config: Optional[SearchConfig] = None,
) -> object | None:
    if evaluator is None:
        evaluator = HeuristicEvaluator()

    config = search_config or SearchConfig(depth=depth)
    candidate_moves = list(valid_moves) if valid_moves is not None else board.getValidMoves()
    if not candidate_moves:
        return None
    if len(candidate_moves) == 1:
        return candidate_moves[0]

    ordered_moves = order_moves(candidate_moves)
    color_multiplier = 1 if board.whiteMove else -1

    best_score = -math.inf
    best_move = ordered_moves[0]

    alpha = -math.inf
    beta = math.inf

    for move in ordered_moves:
        apply_ai_move(board, move)
        score = -negamax(
            board,
            config.depth - 1,
            -beta,
            -alpha,
            -color_multiplier,
            evaluator,
            ply=1,
            search_config=config,
        )
        board.undoMove()

        if score > best_score:
            best_score = score
            best_move = move

        if score > alpha:
            alpha = score

    return best_move
