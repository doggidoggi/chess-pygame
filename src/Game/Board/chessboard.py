import random

from src.Game.Board.move import Move
from src.Game.Pieces.piece import Piece
from src.Game.Pieces.Bishop import Bishop
from src.Game.Pieces.King import King
from src.Game.Pieces.Knight import Knight
from src.Game.Pieces.Pawn import Pawn
from src.Game.Pieces.Queen import Queen
from src.Game.Pieces.Rook import Rook
from src.config import WHITE, BLACK


FEN_TO_PIECE_CLASS = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King,
}
PIECE_CLASS_TO_FEN = {
    Pawn: 'p',
    Knight: 'n',
    Bishop: 'b',
    Rook: 'r',
    Queen: 'q',
    King: 'k',
}
STANDARD_START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


class BaseBoard:
    def __init__(self):
        self.whiteMove = True
        self.checked = False
        self.checkmate = False
        self.stalemate = False
        self.whiteKingPosition = (7, 4)
        self.blackKingPosition = (0, 4)
        self.moveHistory = []
        self.board = [[None] * 8 for _ in range(8)]
        self.piece_to_promote = ()
        self.possible_en_passant = ()
        self.winner = None
        self.game_end = False
        self.draw_reason = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.position_history = []
        self.position_counts = {}

    @staticmethod
    def _is_inside(row, column):
        return 0 <= row <= 7 and 0 <= column <= 7

    @staticmethod
    def _opponent_color(color):
        return BLACK if color == WHITE else WHITE

    def _current_color(self):
        return WHITE if self.whiteMove else BLACK

    def _is_current_turn_piece(self, piece: Piece | None):
        return piece is not None and piece.piece_color == self._current_color()


    def _current_position_count(self):
        return self.position_counts.get(self._repetition_position_key(), 0)

    def _coords_to_algebraic_optional(self, coords: tuple | tuple[()]):
        if not coords:
            return '-'
        return self._coords_to_algebraic(coords)

    def _has_legal_en_passant_capture(self):
        if not self.possible_en_passant:
            return False

        target_row, target_column = self.possible_en_passant
        mover_color = self._current_color()
        pawn_row = target_row + 1 if mover_color == WHITE else target_row - 1
        if not self._is_inside(pawn_row, target_column):
            return False

        for pawn_column in (target_column - 1, target_column + 1):
            if not self._is_inside(pawn_row, pawn_column):
                continue

            piece = self.board[pawn_row][pawn_column]
            if isinstance(piece, Pawn) and piece.piece_color == mover_color:
                move = Move((pawn_row, pawn_column), (target_row, target_column), self)
                if move.is_en_passant_move and self._simulate_and_check_legal(move):
                    return True

        return False

    def _repetition_position_key(self):
        return (
            self.to_fen(include_counters=False).rsplit(' ', 1)[0],
            self._coords_to_algebraic_optional(self.possible_en_passant) if self._has_legal_en_passant_capture() else '-',
        )

    def _record_current_position(self):
        key = self._repetition_position_key()
        self.position_history.append(key)
        self.position_counts[key] = self.position_counts.get(key, 0) + 1
        return key

    def _pop_current_position(self):
        if not self.position_history:
            return None

        key = self.position_history.pop()
        current_count = self.position_counts.get(key, 0)
        if current_count <= 1:
            self.position_counts.pop(key, None)
        else:
            self.position_counts[key] = current_count - 1
        return key

    def _reset_position_history(self):
        self.position_history = []
        self.position_counts = {}
        self._record_current_position()

    def is_draw_by_threefold_repetition(self) -> bool:
        return self._current_position_count() >= 3

    def is_draw_by_fifty_move_rule(self) -> bool:
        return self.halfmove_clock >= 100

    def _update_draw_state(self):
        self.draw_reason = None

        if self.is_draw_by_fifty_move_rule():
            self.game_end = True
            self.checkmate = False
            self.stalemate = False
            self.winner = None
            self.draw_reason = 'fifty-move-rule'
            return True

        if self.is_draw_by_threefold_repetition():
            self.game_end = True
            self.checkmate = False
            self.stalemate = False
            self.winner = None
            self.draw_reason = 'threefold-repetition'
            return True

        return False

    def _post_move_updates(self):
        if not self.game_end:
            self.checkmate = False
            self.stalemate = False
            self.winner = None
            self.draw_reason = None

        self._record_current_position()
        if not self.game_end:
            self._update_draw_state()

    def _snapshot_move_state(self, move: Move):
        move.previous_white_move = self.whiteMove
        move.previous_possible_en_passant = self.possible_en_passant
        move.previous_piece_to_promote = self.piece_to_promote
        move.previous_white_king_position = self.whiteKingPosition
        move.previous_black_king_position = self.blackKingPosition
        move.previous_game_end = self.game_end
        move.previous_checkmate = self.checkmate
        move.previous_stalemate = self.stalemate
        move.previous_winner = self.winner
        move.previous_draw_reason = self.draw_reason
        move.previous_now_move = getattr(self, 'now_move', None)
        move.previous_halfmove_clock = self.halfmove_clock
        move.previous_fullmove_number = self.fullmove_number
        move.previous_moved_state = move.movedPiece.moved if move.movedPiece else False

        move.castle_rook = None
        move.castle_rook_start = None
        move.castle_rook_end = None
        move.castle_rook_previous_moved = None
        move.extra_removed_pieces = []

        if move.is_castle_move:
            rook_start_column = 7 if move.endColumn - move.startColumn == 2 else 0
            rook_end_column = move.endColumn - 1 if rook_start_column == 7 else move.endColumn + 1
            rook = self.board[move.startRow][rook_start_column]
            move.castle_rook = rook
            move.castle_rook_start = (move.startRow, rook_start_column)
            move.castle_rook_end = (move.startRow, rook_end_column)
            if rook is not None:
                move.castle_rook_previous_moved = rook.moved

    def _apply_standard_move(self, move: Move, toggle_turn: bool = True):
        self._snapshot_move_state(move)
        self.moveHistory.append(move)

        self.board[move.startRow][move.startColumn] = None

        if move.is_en_passant_move:
            self.board[move.startRow][move.endColumn] = None

        self.board[move.endRow][move.endColumn] = move.movedPiece

        if isinstance(move.movedPiece, King):
            if move.movedPiece.piece_color == WHITE:
                self.whiteKingPosition = (move.endRow, move.endColumn)
            else:
                self.blackKingPosition = (move.endRow, move.endColumn)

        if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
            self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
        else:
            self.possible_en_passant = ()

        if move.is_castle_move and move.castle_rook is not None:
            rook_start_row, rook_start_column = move.castle_rook_start
            rook_end_row, rook_end_column = move.castle_rook_end
            self.board[rook_start_row][rook_start_column] = None
            self.board[rook_end_row][rook_end_column] = move.castle_rook
            move.castle_rook.moved = True

        self.piece_to_promote = (move.endRow, move.endColumn) if move.is_promotion_move else ()
        move.movedPiece.moved = True

        if isinstance(move.movedPiece, Pawn) or move.is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if move.movedPiece and move.movedPiece.piece_color == BLACK:
            self.fullmove_number += 1

        if toggle_turn:
            self.whiteMove = not self.whiteMove

    def _restore_standard_move(self, move: Move):
        self.whiteMove = move.previous_white_move
        self.possible_en_passant = move.previous_possible_en_passant
        self.piece_to_promote = move.previous_piece_to_promote
        self.whiteKingPosition = move.previous_white_king_position
        self.blackKingPosition = move.previous_black_king_position
        self.game_end = move.previous_game_end
        self.checkmate = move.previous_checkmate
        self.stalemate = move.previous_stalemate
        self.winner = move.previous_winner
        self.draw_reason = move.previous_draw_reason
        self.halfmove_clock = move.previous_halfmove_clock
        self.fullmove_number = move.previous_fullmove_number
        if hasattr(self, 'now_move') and move.previous_now_move is not None:
            self.now_move = move.previous_now_move

        self.board[move.startRow][move.startColumn] = move.movedPiece
        self.board[move.endRow][move.endColumn] = move.capturedPiece

        if move.is_en_passant_move:
            self.board[move.endRow][move.endColumn] = None
            self.board[move.startRow][move.endColumn] = move.capturedPiece

        if move.is_castle_move and move.castle_rook is not None:
            rook_start_row, rook_start_column = move.castle_rook_start
            rook_end_row, rook_end_column = move.castle_rook_end
            self.board[rook_end_row][rook_end_column] = None
            self.board[rook_start_row][rook_start_column] = move.castle_rook
            move.castle_rook.moved = move.castle_rook_previous_moved

        move.movedPiece.moved = move.previous_moved_state

    def _restore_extra_removed_pieces(self, move: Move):
        for row, column, piece in move.extra_removed_pieces:
            self.board[row][column] = piece

    def generate_moves_for_piece(self, row, column, captures_only: bool = False):
        moves = []
        for_piece = self.board[row][column]
        if for_piece is None:
            return moves

        allyColor = for_piece.piece_color
        enemyColor = self._opponent_color(allyColor)

        def pawn_moves():
            direction = for_piece.direction
            start_row = 6 if allyColor == WHITE else 1

            if not captures_only:
                one_step_row = row + direction
                if self._is_inside(one_step_row, column) and self.board[one_step_row][column] is None:
                    moves.append(Move((row, column), (one_step_row, column), self))

                    two_step_row = row + (2 * direction)
                    if row == start_row and self._is_inside(two_step_row, column) and self.board[two_step_row][column] is None:
                        moves.append(Move((row, column), (two_step_row, column), self))

            capture_row = row + direction
            for capture_column in (column - 1, column + 1):
                if not self._is_inside(capture_row, capture_column):
                    continue

                target_piece = self.board[capture_row][capture_column]
                if target_piece is not None and target_piece.piece_color == enemyColor:
                    moves.append(Move((row, column), (capture_row, capture_column), self))
                elif (capture_row, capture_column) == self.possible_en_passant:
                    moves.append(Move((row, column), (capture_row, capture_column), self))

        def bishop_moves():
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for d_row, d_column in directions:
                for length in range(1, 8):
                    endRow = row + d_row * length
                    endColumn = column + d_column * length
                    if not self._is_inside(endRow, endColumn):
                        break

                    target_piece = self.board[endRow][endColumn]
                    if target_piece is None:
                        if not captures_only:
                            moves.append(Move((row, column), (endRow, endColumn), self))
                        continue

                    if target_piece.piece_color == enemyColor:
                        moves.append(Move((row, column), (endRow, endColumn), self))
                    break

        def knight_moves():
            directions = [(2, -1), (1, -2), (2, 1), (1, 2), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]
            for d_row, d_column in directions:
                endRow = row + d_row
                endColumn = column + d_column
                if not self._is_inside(endRow, endColumn):
                    continue

                target_piece = self.board[endRow][endColumn]
                if target_piece is None:
                    if not captures_only:
                        moves.append(Move((row, column), (endRow, endColumn), self))
                elif target_piece.piece_color == enemyColor:
                    moves.append(Move((row, column), (endRow, endColumn), self))

        def rook_moves():
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
            for d_row, d_column in directions:
                for length in range(1, 8):
                    endRow = row + d_row * length
                    endColumn = column + d_column * length
                    if not self._is_inside(endRow, endColumn):
                        break

                    target_piece = self.board[endRow][endColumn]
                    if target_piece is None:
                        if not captures_only:
                            moves.append(Move((row, column), (endRow, endColumn), self))
                        continue

                    if target_piece.piece_color == enemyColor:
                        moves.append(Move((row, column), (endRow, endColumn), self))
                    break

        def queen_moves():
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for d_row, d_column in directions:
                for length in range(1, 8):
                    endRow = row + d_row * length
                    endColumn = column + d_column * length
                    if not self._is_inside(endRow, endColumn):
                        break

                    target_piece = self.board[endRow][endColumn]
                    if target_piece is None:
                        if not captures_only:
                            moves.append(Move((row, column), (endRow, endColumn), self))
                        continue

                    if target_piece.piece_color == enemyColor:
                        moves.append(Move((row, column), (endRow, endColumn), self))
                    break

        def king_moves():
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for d_row, d_column in directions:
                endRow = row + d_row
                endColumn = column + d_column
                if not self._is_inside(endRow, endColumn):
                    continue

                target_piece = self.board[endRow][endColumn]
                if target_piece is None:
                    if not captures_only:
                        moves.append(Move((row, column), (endRow, endColumn), self))
                elif target_piece.piece_color != allyColor:
                    moves.append(Move((row, column), (endRow, endColumn), self))

        if isinstance(for_piece, Pawn):
            pawn_moves()
        elif isinstance(for_piece, Knight):
            knight_moves()
        elif isinstance(for_piece, Bishop):
            bishop_moves()
        elif isinstance(for_piece, Rook):
            rook_moves()
        elif isinstance(for_piece, Queen):
            queen_moves()
        elif isinstance(for_piece, King):
            king_moves()

        return moves

    @staticmethod
    def _coords_to_algebraic(position: tuple[int, int]) -> str:
        row, column = position
        return f"{chr(ord('a') + column)}{8 - row}"

    @staticmethod
    def _algebraic_to_coords(square: str) -> tuple[int, int] | tuple:
        if square == '-':
            return ()
        if len(square) != 2:
            raise ValueError(f'invalid square notation: {square}')

        file_char = square[0].lower()
        rank_char = square[1]
        if file_char < 'a' or file_char > 'h' or rank_char < '1' or rank_char > '8':
            raise ValueError(f'invalid square notation: {square}')

        return 8 - int(rank_char), ord(file_char) - ord('a')

    @staticmethod
    def _create_piece_from_fen_token(token: str):
        piece_class = FEN_TO_PIECE_CLASS.get(token.lower())
        if piece_class is None:
            raise ValueError(f'unsupported FEN piece token: {token}')
        color = WHITE if token.isupper() else BLACK
        return piece_class(color)

    @staticmethod
    def _piece_to_fen_token(piece: Piece) -> str:
        fen_symbol = PIECE_CLASS_TO_FEN.get(type(piece))
        if fen_symbol is None:
            raise ValueError(f'unsupported piece for FEN export: {piece!r}')
        return fen_symbol.upper() if piece.piece_color == WHITE else fen_symbol

    def _castle_rights_to_fen(self) -> str:
        rights = []

        white_king = self.board[7][4]
        if isinstance(white_king, King) and white_king.piece_color == WHITE and not white_king.moved:
            kingside_rook = self.board[7][7]
            queenside_rook = self.board[7][0]
            if isinstance(kingside_rook, Rook) and kingside_rook.piece_color == WHITE and not kingside_rook.moved:
                rights.append('K')
            if isinstance(queenside_rook, Rook) and queenside_rook.piece_color == WHITE and not queenside_rook.moved:
                rights.append('Q')

        black_king = self.board[0][4]
        if isinstance(black_king, King) and black_king.piece_color == BLACK and not black_king.moved:
            kingside_rook = self.board[0][7]
            queenside_rook = self.board[0][0]
            if isinstance(kingside_rook, Rook) and kingside_rook.piece_color == BLACK and not kingside_rook.moved:
                rights.append('k')
            if isinstance(queenside_rook, Rook) and queenside_rook.piece_color == BLACK and not queenside_rook.moved:
                rights.append('q')

        return ''.join(rights) or '-'

    def to_fen(self, include_counters: bool = True) -> str:
        ranks = []
        for row in self.board:
            empty_count = 0
            rank_parts = []
            for piece in row:
                if piece is None:
                    empty_count += 1
                    continue

                if empty_count:
                    rank_parts.append(str(empty_count))
                    empty_count = 0
                rank_parts.append(self._piece_to_fen_token(piece))

            if empty_count:
                rank_parts.append(str(empty_count))

            ranks.append(''.join(rank_parts) or '8')

        active_color = 'w' if self.whiteMove else 'b'
        castling_rights = self._castle_rights_to_fen()
        en_passant = '-' if not self.possible_en_passant else self._coords_to_algebraic(self.possible_en_passant)

        fen = f"{'/'.join(ranks)} {active_color} {castling_rights} {en_passant}"
        if include_counters:
            fen += f" {self.halfmove_clock} {self.fullmove_number}"
        return fen

    def load_fen(self, fen: str, clear_history: bool = True):
        parts = fen.strip().split()
        if len(parts) not in (4, 6):
            raise ValueError('FEN must have 4 or 6 space-separated fields')

        board_part, active_color, castling_part, en_passant_part = parts[:4]
        halfmove_clock = int(parts[4]) if len(parts) == 6 else 0
        fullmove_number = int(parts[5]) if len(parts) == 6 else 1

        rows = board_part.split('/')
        if len(rows) != 8:
            raise ValueError('FEN board part must contain 8 ranks')

        self.board = [[None] * 8 for _ in range(8)]
        self.whiteKingPosition = (-1, -1)
        self.blackKingPosition = (-1, -1)
        self.checkmate = False
        self.stalemate = False
        self.checked = False
        self.game_end = False
        self.winner = None
        self.piece_to_promote = ()

        if clear_history:
            self.moveHistory = []

        self.position_history = []
        self.position_counts = {}

        for row_index, fen_row in enumerate(rows):
            column = 0
            for token in fen_row:
                if token.isdigit():
                    column += int(token)
                    continue

                if column >= 8:
                    raise ValueError(f'invalid FEN rank width in rank {row_index + 1}')

                piece = self._create_piece_from_fen_token(token)
                self.board[row_index][column] = piece

                if isinstance(piece, King):
                    if piece.piece_color == WHITE:
                        self.whiteKingPosition = (row_index, column)
                    else:
                        self.blackKingPosition = (row_index, column)
                elif isinstance(piece, (Rook, King)):
                    piece.moved = True

                column += 1

            if column != 8:
                raise ValueError(f'invalid FEN rank width in rank {row_index + 1}')

        self.whiteMove = active_color == 'w'
        if active_color not in ('w', 'b'):
            raise ValueError('FEN active color must be w or b')

        self.possible_en_passant = self._algebraic_to_coords(en_passant_part)
        self.halfmove_clock = halfmove_clock
        self.fullmove_number = fullmove_number

        if castling_part != '-':
            for token in castling_part:
                if token == 'K':
                    white_king = self.board[7][4]
                    white_rook = self.board[7][7]
                    if not isinstance(white_king, King) or white_king.piece_color != WHITE:
                        raise ValueError('FEN castling rights include K but white king is not on e1')
                    if not isinstance(white_rook, Rook) or white_rook.piece_color != WHITE:
                        raise ValueError('FEN castling rights include K but white rook is not on h1')
                    white_king.moved = False
                    white_rook.moved = False
                elif token == 'Q':
                    white_king = self.board[7][4]
                    white_rook = self.board[7][0]
                    if not isinstance(white_king, King) or white_king.piece_color != WHITE:
                        raise ValueError('FEN castling rights include Q but white king is not on e1')
                    if not isinstance(white_rook, Rook) or white_rook.piece_color != WHITE:
                        raise ValueError('FEN castling rights include Q but white rook is not on a1')
                    white_king.moved = False
                    white_rook.moved = False
                elif token == 'k':
                    black_king = self.board[0][4]
                    black_rook = self.board[0][7]
                    if not isinstance(black_king, King) or black_king.piece_color != BLACK:
                        raise ValueError('FEN castling rights include k but black king is not on e8')
                    if not isinstance(black_rook, Rook) or black_rook.piece_color != BLACK:
                        raise ValueError('FEN castling rights include k but black rook is not on h8')
                    black_king.moved = False
                    black_rook.moved = False
                elif token == 'q':
                    black_king = self.board[0][4]
                    black_rook = self.board[0][0]
                    if not isinstance(black_king, King) or black_king.piece_color != BLACK:
                        raise ValueError('FEN castling rights include q but black king is not on e8')
                    if not isinstance(black_rook, Rook) or black_rook.piece_color != BLACK:
                        raise ValueError('FEN castling rights include q but black rook is not on a8')
                    black_king.moved = False
                    black_rook.moved = False
                else:
                    raise ValueError(f'unsupported FEN castling token: {token}')

        self.validate_internal_state(raise_on_error=True)
        self._reset_position_history()

    def promote_piece(self, piece_to_promotion, choice):
        row, column = piece_to_promotion
        piece = self.board[row][column]
        if piece is None:
            return

        color = piece.piece_color
        piece_index = choice % 4

        if piece_index == 0:
            self.board[row][column] = Queen(color)
        elif piece_index == 1:
            self.board[row][column] = Rook(color)
        elif piece_index == 2:
            self.board[row][column] = Knight(color)
        else:
            self.board[row][column] = Bishop(color)

        self.piece_to_promote = ()
        self.is_variant_stalemate()
        self.is_variant_checkmate()

    def get_castle_moves(self, row, column, moves):
        if not self._is_inside(row, column):
            return

        king = self.board[row][column]
        if not isinstance(king, King):
            return
        if king.moved:
            return

        enemy_color = self._opponent_color(king.piece_color)
        if self.is_square_attacked((row, column), enemy_color):
            return

        right_rook = self.board[row][7]
        if isinstance(right_rook, Rook) and right_rook.piece_color == king.piece_color and not right_rook.moved:
            self.get_king_castling(row, column, moves)

        left_rook = self.board[row][0]
        if isinstance(left_rook, Rook) and left_rook.piece_color == king.piece_color and not left_rook.moved:
            self.get_queen_castling(row, column, moves)

    def get_king_castling(self, row, column, moves):
        enemy_color = self._opponent_color(self.board[row][column].piece_color)
        if self._is_inside(row, column + 2):
            if self.board[row][column + 1] is None and self.board[row][column + 2] is None:
                if not self.is_square_attacked((row, column + 1), enemy_color) and not self.is_square_attacked(
                    (row, column + 2), enemy_color
                ):
                    moves.append(Move((row, column), (row, column + 2), self))

    def get_queen_castling(self, row, column, moves):
        enemy_color = self._opponent_color(self.board[row][column].piece_color)
        if self._is_inside(row, column - 3):
            if self.board[row][column - 1] is None and self.board[row][column - 2] is None and self.board[row][column - 3] is None:
                if not self.is_square_attacked((row, column - 1), enemy_color) and not self.is_square_attacked(
                    (row, column - 2), enemy_color
                ):
                    moves.append(Move((row, column), (row, column - 2), self))

    @staticmethod
    def _normalize_delta(row_delta: int, column_delta: int) -> tuple[int, int]:
        def _sign(value: int) -> int:
            if value > 0:
                return 1
            if value < 0:
                return -1
            return 0

        return _sign(row_delta), _sign(column_delta)

    def _supports_fast_legal_generation(self) -> bool:
        return True

    def _simulate_and_check_legal(self, move: Move) -> bool:
        mover_color = move.movedPiece.piece_color
        enemy_color = self._opponent_color(mover_color)

        self.make_move(move)
        king_position = self.whiteKingPosition if mover_color == WHITE else self.blackKingPosition
        is_legal = not self.is_square_attacked(king_position, enemy_color)
        self.undoMove()
        return is_legal

    def _analyze_king_state(self, color):
        king_position = self.whiteKingPosition if color == WHITE else self.blackKingPosition
        king_row, king_column = king_position

        pins = {}
        checkers = []

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        for d_row, d_column in directions:
            possible_pin = None
            for distance in range(1, 8):
                row = king_row + d_row * distance
                column = king_column + d_column * distance
                if not self._is_inside(row, column):
                    break

                piece = self.board[row][column]
                if piece is None:
                    continue

                if piece.piece_color == color and not isinstance(piece, King):
                    if possible_pin is None:
                        possible_pin = (row, column)
                    else:
                        break
                    continue

                enemy_attacks_along_ray = False
                is_straight = d_row == 0 or d_column == 0
                is_diagonal = d_row != 0 and d_column != 0

                if is_straight and isinstance(piece, (Rook, Queen)):
                    enemy_attacks_along_ray = True
                elif is_diagonal and isinstance(piece, (Bishop, Queen)):
                    enemy_attacks_along_ray = True
                elif distance == 1 and isinstance(piece, King):
                    enemy_attacks_along_ray = True
                elif distance == 1 and isinstance(piece, Pawn):
                    if piece.piece_color == WHITE and d_row == 1 and abs(d_column) == 1:
                        enemy_attacks_along_ray = True
                    elif piece.piece_color == BLACK and d_row == -1 and abs(d_column) == 1:
                        enemy_attacks_along_ray = True

                if enemy_attacks_along_ray:
                    if possible_pin is None:
                        checkers.append((row, column, d_row, d_column, piece))
                    else:
                        pins[possible_pin] = (d_row, d_column, row, column)
                break

        knight_directions = [(2, -1), (1, -2), (2, 1), (1, 2), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]
        for d_row, d_column in knight_directions:
            row = king_row + d_row
            column = king_column + d_column
            if not self._is_inside(row, column):
                continue

            piece = self.board[row][column]
            if isinstance(piece, Knight) and piece.piece_color != color:
                checkers.append((row, column, d_row, d_column, piece))

        return {
            'king_position': king_position,
            'pins': pins,
            'checkers': checkers,
            'in_check': bool(checkers),
        }

    def _is_move_allowed_by_pin(self, move: Move, pins: dict) -> bool:
        pin = pins.get((move.startRow, move.startColumn))
        if pin is None:
            return True

        pin_direction = (pin[0], pin[1])
        move_direction = self._normalize_delta(move.endRow - move.startRow, move.endColumn - move.startColumn)
        return move_direction == pin_direction or move_direction == (-pin_direction[0], -pin_direction[1])

    def _build_check_evasion_targets(self, king_position, checker_info, captures_only: bool):
        checker_row, checker_column, d_row, d_column, checking_piece = checker_info
        targets = {(checker_row, checker_column)}

        if captures_only:
            return targets

        if isinstance(checking_piece, (Bishop, Rook, Queen)):
            row = king_position[0] + d_row
            column = king_position[1] + d_column
            while (row, column) != (checker_row, checker_column):
                targets.add((row, column))
                row += d_row
                column += d_column

        return targets

    def _generate_legal_king_moves(self, captures_only: bool = False, include_castling: bool = True):
        legal_moves = []
        king_position = self.whiteKingPosition if self.whiteMove else self.blackKingPosition

        for move in self.generate_moves_for_piece(king_position[0], king_position[1], captures_only=captures_only):
            if self._simulate_and_check_legal(move):
                legal_moves.append(move)

        if include_castling and not captures_only:
            castle_moves = []
            self.get_castle_moves(king_position[0], king_position[1], castle_moves)
            for move in castle_moves:
                if self._simulate_and_check_legal(move):
                    legal_moves.append(move)

        return legal_moves

    def _get_legal_moves_with_fast_filtering(self, captures_only: bool = False):
        mover_color = self._current_color()
        king_state = self._analyze_king_state(mover_color)
        king_position = king_state['king_position']
        pins = king_state['pins']
        checkers = king_state['checkers']
        check_count = len(checkers)

        if check_count >= 2:
            return self._generate_legal_king_moves(captures_only=captures_only, include_castling=False)

        allowed_targets = None
        if check_count == 1:
            allowed_targets = self._build_check_evasion_targets(king_position, checkers[0], captures_only=captures_only)

        legal_moves = []
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if not self._is_current_turn_piece(piece):
                    continue

                if isinstance(piece, King):
                    legal_moves.extend(
                        self._generate_legal_king_moves(
                            captures_only=captures_only,
                            include_castling=check_count == 0,
                        )
                    )
                    continue

                for move in self.generate_moves_for_piece(row, column, captures_only=captures_only):
                    if not self._is_move_allowed_by_pin(move, pins):
                        continue

                    if allowed_targets is not None:
                        move_target = (move.endRow, move.endColumn)
                        captured_square = (move.startRow, move.endColumn) if move.is_en_passant_move else move_target
                        if move_target not in allowed_targets and captured_square not in allowed_targets:
                            continue

                    if move.is_en_passant_move:
                        if self._simulate_and_check_legal(move):
                            legal_moves.append(move)
                    else:
                        legal_moves.append(move)

        return legal_moves

    def _get_legal_moves_via_simulation(self, captures_only: bool = False):
        validMoves = self.getAllPossibleMoves(captures_only=captures_only)

        if not captures_only:
            king_position = self.whiteKingPosition if self.whiteMove else self.blackKingPosition
            self.get_castle_moves(king_position[0], king_position[1], validMoves)

        legal_moves = []
        for move in validMoves:
            if self._simulate_and_check_legal(move):
                legal_moves.append(move)

        return legal_moves

    def getValidMoves(self, captures_only: bool = False):
        if self.game_end:
            return []

        if not self._supports_fast_legal_generation():
            return self._get_legal_moves_via_simulation(captures_only=captures_only)

        return self._get_legal_moves_with_fast_filtering(captures_only=captures_only)

    def undoMove(self):
        if not self.moveHistory:
            return

        self._pop_current_position()
        move = self.moveHistory.pop()
        self._restore_standard_move(move)
        self._restore_extra_removed_pieces(move)

    def inCheck(self):
        if self.whiteMove:
            return self.is_square_attacked(self.whiteKingPosition, BLACK)
        return self.is_square_attacked(self.blackKingPosition, WHITE)

    def castling(self, move: Move):
        pass

    def is_square_attacked(self, position, by_color):
        row, column = position

        pawn_row = row + 1 if by_color == WHITE else row - 1
        for pawn_column in (column - 1, column + 1):
            if self._is_inside(pawn_row, pawn_column):
                piece = self.board[pawn_row][pawn_column]
                if isinstance(piece, Pawn) and piece.piece_color == by_color:
                    return True

        knight_directions = [(2, -1), (1, -2), (2, 1), (1, 2), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]
        for d_row, d_column in knight_directions:
            source_row = row + d_row
            source_column = column + d_column
            if self._is_inside(source_row, source_column):
                piece = self.board[source_row][source_column]
                if isinstance(piece, Knight) and piece.piece_color == by_color:
                    return True

        king_directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for d_row, d_column in king_directions:
            source_row = row + d_row
            source_column = column + d_column
            if self._is_inside(source_row, source_column):
                piece = self.board[source_row][source_column]
                if isinstance(piece, King) and piece.piece_color == by_color:
                    return True

        diagonal_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for d_row, d_column in diagonal_directions:
            for length in range(1, 8):
                source_row = row + d_row * length
                source_column = column + d_column * length
                if not self._is_inside(source_row, source_column):
                    break

                piece = self.board[source_row][source_column]
                if piece is None:
                    continue
                if piece.piece_color != by_color:
                    break
                if isinstance(piece, (Bishop, Queen)):
                    return True
                break

        straight_directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        for d_row, d_column in straight_directions:
            for length in range(1, 8):
                source_row = row + d_row * length
                source_column = column + d_column * length
                if not self._is_inside(source_row, source_column):
                    break

                piece = self.board[source_row][source_column]
                if piece is None:
                    continue
                if piece.piece_color != by_color:
                    break
                if isinstance(piece, (Rook, Queen)):
                    return True
                break

        return False

    def get_square_under_attack(self, position):
        attacking_color = BLACK if self.whiteMove else WHITE
        return self.is_square_attacked(position, attacking_color)

    def getAllPossibleMoves(self, captures_only: bool = False):
        allyMoves = []
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if self._is_current_turn_piece(piece):
                    allyMoves.extend(self.generate_moves_for_piece(row, column, captures_only=captures_only))
        return allyMoves

    def board_state_key(self):
        pieces = []
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    pieces.append((row, column, piece.symbol(), piece.moved))

        return (
            self.whiteMove,
            tuple(pieces),
            self.whiteKingPosition,
            self.blackKingPosition,
            self.possible_en_passant,
            self.piece_to_promote,
            self.game_end,
            self.checkmate,
            self.stalemate,
            self.winner,
            self.draw_reason,
            self.halfmove_clock,
            self.fullmove_number,
            getattr(self, 'now_move', None),
            tuple(self.position_history),
        )

    def validate_internal_state(self, raise_on_error: bool = False):
        errors = []
        white_kings = []
        black_kings = []

        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if isinstance(piece, King):
                    if piece.piece_color == WHITE:
                        white_kings.append((row, column))
                    else:
                        black_kings.append((row, column))

        if len(white_kings) > 1:
            errors.append(f'multiple white kings on board: {white_kings}')
        if len(black_kings) > 1:
            errors.append(f'multiple black kings on board: {black_kings}')

        if len(white_kings) == 1 and self.whiteKingPosition != white_kings[0]:
            errors.append(
                f'whiteKingPosition mismatch: stored={self.whiteKingPosition}, actual={white_kings[0]}'
            )
        elif len(white_kings) == 0 and not self.game_end:
            errors.append('white king missing while game_end is False')

        if len(black_kings) == 1 and self.blackKingPosition != black_kings[0]:
            errors.append(
                f'blackKingPosition mismatch: stored={self.blackKingPosition}, actual={black_kings[0]}'
            )
        elif len(black_kings) == 0 and not self.game_end:
            errors.append('black king missing while game_end is False')

        if self.position_history:
            current_key = self._repetition_position_key()
            if self.position_history[-1] != current_key:
                errors.append(
                    f'position_history tail mismatch: stored={self.position_history[-1]}, actual={current_key}'
                )
            if self.position_counts.get(current_key, 0) <= 0:
                errors.append('current repetition position is missing from position_counts')

        if raise_on_error and errors:
            raise ValueError('; '.join(errors))

        return errors

    def perft(self, depth: int) -> int:
        if depth < 0:
            raise ValueError('depth must be >= 0')
        if depth == 0:
            return 1

        total = 0
        for move in self.getValidMoves():
            self.make_move(move)
            total += self.perft(depth - 1)
            self.undoMove()
        return total

    def perft_divide(self, depth: int):
        if depth < 1:
            raise ValueError('depth must be >= 1')

        result = {}
        for move in self.getValidMoves():
            self.make_move(move)
            result[move.uci()] = self.perft(depth - 1)
            self.undoMove()
        return result

    def is_en_passant(self, move: Move) -> bool:
        return isinstance(move.movedPiece, Pawn) and abs(move.startRow - move.endRow) == 2

    def is_piece(self, position: tuple) -> bool:
        return self.board[position[0]][position[1]] is not None

    def is_legal(self, move: Move) -> bool:
        return move in self.getValidMoves()

    def is_variant_checkmate(self) -> bool:
        if not self.game_end:
            validMoves = self.getValidMoves()
            if len(validMoves) == 0 and self.inCheck():
                self.checkmate = True
                self.game_end = True
                self.winner = BLACK if self.whiteMove else WHITE
                return True
        return False

    def is_variant_stalemate(self) -> bool:
        if not self.game_end:
            validMoves = self.getValidMoves()
            if len(validMoves) == 0 and not self.inCheck():
                self.stalemate = True
                self.game_end = True
                self.winner = None
                self.draw_reason = 'stalemate'
                return True
            if self._update_draw_state():
                return True
        return False

    def is_variant_check(self) -> bool:
        king_position = self.blackKingPosition if not self.whiteMove else self.whiteKingPosition
        attacking_color = WHITE if not self.whiteMove else BLACK
        return self.is_square_attacked(king_position, attacking_color)

    def _setup_board(self):
        for column in range(8):
            self.board[1][column] = Pawn(piece_color=BLACK)
            self.board[6][column] = Pawn(piece_color=WHITE)

        self.board[7][1] = Knight(piece_color=WHITE)
        self.board[7][2] = Bishop(piece_color=WHITE)
        self.board[7][5] = Bishop(piece_color=WHITE)
        self.board[7][6] = Knight(piece_color=WHITE)

        self.board[0][1] = Knight(piece_color=BLACK)
        self.board[0][2] = Bishop(piece_color=BLACK)
        self.board[0][5] = Bishop(piece_color=BLACK)
        self.board[0][6] = Knight(piece_color=BLACK)

        self.board[7][0] = Rook(piece_color=WHITE)
        self.board[7][3] = Queen(piece_color=WHITE)
        self.board[7][7] = Rook(piece_color=WHITE)

        self.board[0][0] = Rook(piece_color=BLACK)
        self.board[0][3] = Queen(piece_color=BLACK)
        self.board[0][7] = Rook(piece_color=BLACK)

        self.board[7][4] = King(piece_color=WHITE)
        self.board[0][4] = King(piece_color=BLACK)
        self.whiteKingPosition = (7, 4)
        self.blackKingPosition = (0, 4)

    def __str__(self):
        def c(row, col):
            piece = self.board[row][col]
            if piece is None:
                return '  '
            return piece.symbol()

        print('     +----+----+----+----+----+----+----+----+')
        for row in range(7, -1, -1):
            print(' ', row, end='  ')
            for col in range(8):
                print('|', c(row, col), end=' ')
            print('|')
            print('     +----+----+----+----+----+----+----+----+')
        print(end='        ')
        for col in range(8):
            print(col, end='    ')
        return ''

    def make_move(self, move: Move):
        if self._is_current_turn_piece(move.movedPiece):
            self._apply_standard_move(move)
            self._post_move_updates()


class OppositeChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self._reset_position_history()

    def is_variant_checkmate(self) -> bool:
        if not self.game_end:
            validMoves = self.getValidMoves()
            if len(validMoves) == 0 and self.inCheck():
                self.checkmate = True
                self.game_end = True
                self.winner = BLACK if not self.whiteMove else WHITE
                return True
        return False

    def is_variant_stalemate(self) -> bool:
        if not self.game_end:
            validMoves = self.getValidMoves()
            if len(validMoves) == 0 and not self.inCheck():
                self.stalemate = True
                self.game_end = True
                self.winner = None
                self.draw_reason = 'stalemate'
                return True
            if self._update_draw_state():
                return True
        return False


class UntilTheFirstCheck(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self._reset_position_history()


class LOSChess(BaseBoard):
    pass


class MarseilleChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self.now_move = 1
        self._reset_position_history()

    def make_move(self, move: Move):
        if not self._is_current_turn_piece(move.movedPiece):
            return

        self._apply_standard_move(move, toggle_turn=False)

        mover_color = move.movedPiece.piece_color
        enemy_king_position = self.blackKingPosition if mover_color == WHITE else self.whiteKingPosition

        if self.now_move < 2:
            self.now_move += 1
            if self.is_square_attacked(enemy_king_position, mover_color):
                self.game_end = True
        else:
            self.now_move = 1
            self.whiteMove = not self.whiteMove

        self._post_move_updates()


class MiniChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self._reset_position_history()

    def _setup_board(self):
        self.board[1][0] = Pawn(piece_color=BLACK)
        self.board[1][1] = Pawn(piece_color=BLACK)
        self.board[1][2] = Pawn(piece_color=BLACK)
        self.board[1][3] = Pawn(piece_color=BLACK)
        self.board[1][4] = Pawn(piece_color=BLACK)
        self.board[0][0] = Rook(piece_color=BLACK)
        self.board[0][4] = King(piece_color=BLACK)
        self.board[0][1] = Knight(piece_color=BLACK)
        self.board[0][2] = Bishop(piece_color=BLACK)
        self.board[0][3] = Queen(piece_color=BLACK)

        self.board[3][0] = Pawn(piece_color=WHITE)
        self.board[3][1] = Pawn(piece_color=WHITE)
        self.board[3][2] = Pawn(piece_color=WHITE)
        self.board[3][3] = Pawn(piece_color=WHITE)
        self.board[3][4] = Pawn(piece_color=WHITE)
        self.board[4][0] = Rook(piece_color=WHITE)
        self.board[4][4] = King(piece_color=WHITE)
        self.board[4][1] = Knight(piece_color=WHITE)
        self.board[4][2] = Bishop(piece_color=WHITE)
        self.board[4][3] = Queen(piece_color=WHITE)

        self.whiteKingPosition = (4, 4)
        self.blackKingPosition = (0, 4)


class WithoutTimerChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self._reset_position_history()


class NukeBoard(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self._reset_position_history()

    def _supports_fast_legal_generation(self) -> bool:
        return False

    def _record_nuke_removed_piece(self, move: Move, row, column):
        piece = self.board[row][column]
        if piece is not None:
            move.extra_removed_pieces.append((row, column, piece))
            self.board[row][column] = None

    def make_move(self, move: Move):
        if not self._is_current_turn_piece(move.movedPiece):
            return

        self._snapshot_move_state(move)
        self.moveHistory.append(move)

        self.board[move.startRow][move.startColumn] = None

        if move.is_en_passant_move:
            self.board[move.startRow][move.endColumn] = None

        if isinstance(move.movedPiece, King):
            if move.movedPiece.piece_color == WHITE:
                self.whiteKingPosition = (move.endRow, move.endColumn)
            else:
                self.blackKingPosition = (move.endRow, move.endColumn)

        if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
            self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
        else:
            self.possible_en_passant = ()

        self.piece_to_promote = (move.endRow, move.endColumn) if move.is_promotion_move else ()
        move.movedPiece.moved = True

        if move.capturedPiece:
            self._record_nuke_removed_piece(move, move.endRow, move.endColumn)

            for d_row, d_column in [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, -1), (1, -1), (1, 1), (-1, 1)]:
                row = move.endRow + d_row
                column = move.endColumn + d_column
                if not self._is_inside(row, column):
                    continue

                piece = self.board[row][column]
                if piece is not None and piece.piece_color != move.movedPiece.piece_color:
                    if isinstance(piece, King):
                        self.game_end = True
                    self._record_nuke_removed_piece(move, row, column)

            if isinstance(move.movedPiece, King):
                for row in range(len(self.board)):
                    for column in range(len(self.board[row])):
                        piece = self.board[row][column]
                        if piece is not None and piece.piece_color == move.movedPiece.piece_color:
                            self._record_nuke_removed_piece(move, row, column)
                self.game_end = True
        else:
            self.board[move.endRow][move.endColumn] = move.movedPiece

        if move.is_castle_move and move.castle_rook is not None:
            rook_start_row, rook_start_column = move.castle_rook_start
            rook_end_row, rook_end_column = move.castle_rook_end
            self.board[rook_start_row][rook_start_column] = None
            self.board[rook_end_row][rook_end_column] = move.castle_rook
            move.castle_rook.moved = True

        if isinstance(move.movedPiece, Pawn) or move.is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if move.movedPiece and move.movedPiece.piece_color == BLACK:
            self.fullmove_number += 1

        self.whiteMove = not self.whiteMove
        self._post_move_updates()

    def undoMove(self):
        if not self.moveHistory:
            return

        self._pop_current_position()
        move = self.moveHistory.pop()

        self.whiteMove = move.previous_white_move
        self.possible_en_passant = move.previous_possible_en_passant
        self.piece_to_promote = move.previous_piece_to_promote
        self.whiteKingPosition = move.previous_white_king_position
        self.blackKingPosition = move.previous_black_king_position
        self.game_end = move.previous_game_end
        self.checkmate = move.previous_checkmate
        self.stalemate = move.previous_stalemate
        self.winner = move.previous_winner
        self.draw_reason = move.previous_draw_reason
        self.halfmove_clock = move.previous_halfmove_clock
        self.fullmove_number = move.previous_fullmove_number

        self.board[move.startRow][move.startColumn] = move.movedPiece
        self.board[move.endRow][move.endColumn] = move.capturedPiece

        if move.is_en_passant_move:
            self.board[move.endRow][move.endColumn] = None
            self.board[move.startRow][move.endColumn] = move.capturedPiece

        if move.is_castle_move and move.castle_rook is not None:
            rook_start_row, rook_start_column = move.castle_rook_start
            rook_end_row, rook_end_column = move.castle_rook_end
            self.board[rook_end_row][rook_end_column] = None
            self.board[rook_start_row][rook_start_column] = move.castle_rook
            move.castle_rook.moved = move.castle_rook_previous_moved

        move.movedPiece.moved = move.previous_moved_state
        self._restore_extra_removed_pieces(move)


def random960():
    start_position = ['R', 'K', 'R']
    for piece in ['Q', 'N', 'N']:
        start_position.insert(random.choice(range(len(start_position) + 1)), piece)
    f_bishop_position = random.choice(range(len(start_position) + 1))
    start_position.insert(f_bishop_position, 'B')
    start_position.insert(random.choice(range(f_bishop_position + 1, len(start_position) + 1, 2)), 'B')
    return start_position


class Chess960(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self._reset_position_history()

    def _setup_board(self):
        for column in range(8):
            self.board[1][column] = Pawn(piece_color=BLACK)
            self.board[6][column] = Pawn(piece_color=WHITE)

        positions = random960()
        for i, piece_code in enumerate(positions):
            if piece_code == 'B':
                self.board[0][i] = Bishop(BLACK)
            elif piece_code == 'N':
                self.board[0][i] = Knight(BLACK)
            elif piece_code == 'R':
                self.board[0][i] = Rook(BLACK)
            elif piece_code == 'K':
                self.board[0][i] = King(BLACK)
                self.blackKingPosition = (0, i)
            elif piece_code == 'Q':
                self.board[0][i] = Queen(BLACK)

        for i, piece_code in enumerate(positions):
            if piece_code == 'B':
                self.board[7][i] = Bishop(WHITE)
            elif piece_code == 'N':
                self.board[7][i] = Knight(WHITE)
            elif piece_code == 'R':
                self.board[7][i] = Rook(WHITE)
            elif piece_code == 'K':
                self.board[7][i] = King(WHITE)
                self.whiteKingPosition = (7, i)
            elif piece_code == 'Q':
                self.board[7][i] = Queen(WHITE)


class Checkers:
    pass
