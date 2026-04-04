from src.Game.Pieces.King import King
from src.Game.Pieces.Pawn import Pawn


class Move:
    def __init__(self, startPosition: tuple, endPosition: tuple, board):
        self.startRow = startPosition[0]
        self.startColumn = startPosition[1]
        self.endRow = endPosition[0]
        self.endColumn = endPosition[1]
        self.board = board

        self.movedPiece = board.board[self.startRow][self.startColumn]
        self.capturedPiece = board.board[self.endRow][self.endColumn]

        self.is_en_passant_move = (
            isinstance(self.movedPiece, Pawn)
            and (self.endRow, self.endColumn) == board.possible_en_passant
            and self.startColumn != self.endColumn
            and self.capturedPiece is None
        )
        if self.is_en_passant_move:
            self.capturedPiece = board.board[self.startRow][self.endColumn]

        self.is_castle_move = isinstance(self.movedPiece, King) and abs(self.endColumn - self.startColumn) == 2
        self.is_promotion_move = isinstance(self.movedPiece, Pawn) and self.endRow in (0, 7)
        self.is_capture = self.capturedPiece is not None

        self.previous_white_move = None
        self.previous_possible_en_passant = ()
        self.previous_piece_to_promote = ()
        self.previous_white_king_position = None
        self.previous_black_king_position = None
        self.previous_game_end = False
        self.previous_checkmate = False
        self.previous_stalemate = False
        self.previous_winner = None
        self.previous_now_move = None
        self.previous_halfmove_clock = 0
        self.previous_fullmove_number = 1

        self.previous_moved_state = False
        self.castle_rook = None
        self.castle_rook_start = None
        self.castle_rook_end = None
        self.castle_rook_previous_moved = None
        self.extra_removed_pieces = []

    def uci(self) -> str:
        files = 'abcdefgh'
        ranks = '87654321'
        return (
            f'{files[self.startColumn]}{ranks[self.startRow]}'
            f'{files[self.endColumn]}{ranks[self.endRow]}'
        )

    def __repr__(self):
        suffix = ''
        if self.is_promotion_move:
            suffix += '=promo'
        if self.is_castle_move:
            suffix += '=castle'
        if self.is_en_passant_move:
            suffix += '=ep'
        if self.is_capture:
            suffix += '=x'
        return f'Move({self.uci()}{suffix})'

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.startRow, self.startColumn, self.endColumn, self.endRow) == (
            other.startRow, other.startColumn, other.endColumn, other.endRow
        )
