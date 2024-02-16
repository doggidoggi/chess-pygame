import copy
import random

from src.Game.Board.move import *
from src.Game.Pieces.Bishop import Bishop
from src.Game.Pieces.King import King
from src.Game.Pieces.Knight import Knight
from src.Game.Pieces.Pawn import Pawn
from src.Game.Pieces.Queen import Queen
from src.Game.Pieces.Rook import Rook


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

    def generate_moves_for_piece(self, row, column):
        moves = []
        enemyColor = BLACK if self.whiteMove else WHITE
        allyColor = WHITE if self.whiteMove else BLACK
        for_piece = self.board[row][column]

        def pawn_moves():
            if self.whiteMove:
                if row - 1 <= 7 and self.board[row - 1][column] is None:
                    moves.append(Move((row, column), (row - 1, column),
                                      self))
                    if row == 6 and self.board[row - 2][column] is None:
                        moves.append(Move((row, column), (row - 2, column),
                                          self))
                if row - 1 <= 7 and column - 1 >= 0:
                    if self.board[row - 1][column - 1] and self.board[row - 1][column - 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row - 1, column - 1),
                                          self))
                    elif (row - 1, column - 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row - 1, column - 1),
                                          self))
                if row - 1 <= 7 and column + 1 <= 7:
                    if self.board[row - 1][column + 1] and self.board[row - 1][column + 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row - 1, column + 1),
                                          self))
                    elif (row - 1, column + 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row - 1, column + 1),
                                          self))

            else:

                if row + 1 <= 7 and self.board[row + 1][column] is None:
                    moves.append(Move((row, column), (row + 1, column),
                                      self))
                    if row == 1 and self.board[row + 2][column] is None:
                        moves.append(Move((row, column), (row + 2, column),
                                          self))
                if row + 1 <= 7 and column - 1 >= 0:
                    if self.board[row + 1][column - 1] and self.board[row + 1][column - 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row + 1, column - 1),
                                          self))
                    elif (row + 1, column - 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row + 1, column - 1),
                                          self))
                if row + 1 <= 7 and column + 1 <= 7:
                    if self.board[row + 1][column + 1] and self.board[row + 1][column + 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row + 1, column + 1),
                                          self))
                    elif (row + 1, column + 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row + 1, column + 1),
                                          self))

        def bishop_moves():
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # направо, налево
            for direction in directions:
                for length in range(1, 8):
                    endRow = row + direction[0] * length
                    endColumn = column + direction[1] * length
                    if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                        if self.board[endRow][endColumn] is None:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self))
                        elif self.board[endRow][endColumn].piece_color == enemyColor:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self))
                            break
                        elif self.board[endRow][endColumn].piece_color == allyColor:
                            break

        def knight_moves():
            directions = [(2, -1), (1, -2), (2, 1), (1, 2), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]  # направо, налево
            for direction in directions:
                endRow = row + direction[0]
                endColumn = column + direction[1]
                if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                    if self.board[endRow][endColumn] is None:
                        moves.append(Move((row, column), (endRow, endColumn),
                                          self))
                    elif self.board[endRow][endColumn].piece_color == enemyColor:
                        moves.append(Move((row, column), (endRow, endColumn),
                                          self))
                        continue
                    elif self.board[endRow][endColumn].piece_color == allyColor:
                        continue

        def queen_moves():
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # направо, налево
            for direction in directions:
                for length in range(1, 8):
                    endRow = row + direction[0] * length
                    endColumn = column + direction[1] * length
                    if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                        if self.board[endRow][endColumn] is None:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self))
                        elif self.board[endRow][endColumn].piece_color == enemyColor:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self))
                            break
                        elif self.board[endRow][endColumn].piece_color == allyColor:
                            break

        def rook_moves():
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # направо, налево, вниз, вверх
            for direction in directions:
                for length in range(1, 8):
                    endRow = row + direction[0] * length
                    endColumn = column + direction[1] * length
                    if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                        if self.board[endRow][endColumn] is None:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self))
                        elif self.board[endRow][endColumn].piece_color == enemyColor:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self))
                            break
                        elif self.board[endRow][endColumn].piece_color == allyColor:
                            break

        def king_moves():
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for direction in directions:
                endRow = row + direction[0]
                endColumn = column + direction[1]
                if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                    if self.board[endRow][endColumn] and self.board[endRow][endColumn].piece_color == allyColor:
                        continue
                    else:
                        moves.append(Move((row, column), (endRow, endColumn),
                                          self))

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

    def promote_piece(self, piece_to_promotion, choice):
        color = WHITE if choice <= 3 else BLACK
        if choice == 0 or choice == 7:
            self.board[piece_to_promotion[0]][piece_to_promotion[1]] = Queen(color)
        elif choice == 1 or choice == 6:
            self.board[piece_to_promotion[0]][piece_to_promotion[1]] = Rook(color)
        elif choice == 2 or choice == 5:
            self.board[piece_to_promotion[0]][piece_to_promotion[1]] = Knight(color)
        elif choice == 3 or choice == 4:
            self.board[piece_to_promotion[0]][piece_to_promotion[1]] = Bishop(color)
        self.piece_to_promote = ()
        self.is_variant_stalemate()
        self.is_variant_checkmate()

    def get_castle_moves(self, row, column, moves):
        left_rook_position: Piece = self.board[row][0]
        right_rook_position: Piece = self.board[row][7]
        king: Piece = self.board[row][column]
        if self.inCheck():
            return
        if king and (self.whiteMove and left_rook_position and not left_rook_position.moved and not king.moved) or (
                left_rook_position and not self.whiteMove and not left_rook_position.moved and not king.moved):
            self.get_king_castling(row, column, moves)
        if king and (self.whiteMove and right_rook_position and not right_rook_position.moved and not king.moved) or (
                right_rook_position and not self.whiteMove and not right_rook_position.moved and not king.moved):
            self.get_queen_castling(row, column, moves)

    def get_king_castling(self, row, column, moves):
        if self.board[row][column + 1] is None and self.board[row][column + 2] is None:
            if not self.get_square_under_attack((row, column + 1)) and not self.get_square_under_attack(
                    (row, column + 2)):
                moves.append(Move((row, column), (row, column + 2), self))

    def get_queen_castling(self, row, column, moves):
        if (self.board[row][column - 1] is None and self.board[row][column - 2] is None
                and self.board[row][column - 3] is None):
            if not self.get_square_under_attack((row, column - 1)) and not self.get_square_under_attack(
                    (row, column - 2)):
                moves.append(Move((row, column), (row, column - 2), self))

    def getValidMoves(self):
        if not self.game_end:
            temp_board = copy.deepcopy(self)
            temp_possible_en_passant = copy.deepcopy(self.possible_en_passant)
            validMoves = temp_board.getAllPossibleMoves()
            if temp_board.whiteMove:
                temp_board.get_castle_moves(self.whiteKingPosition[0], self.whiteKingPosition[1], validMoves)
            else:
                temp_board.get_castle_moves(self.blackKingPosition[0], self.blackKingPosition[1], validMoves)
            for i in range(len(validMoves) - 1, -1, -1):
                temp_board.make_move(validMoves[i])
                temp_board.whiteMove = not temp_board.whiteMove
                if temp_board.inCheck():
                    validMoves.remove(validMoves[i])
                temp_board.whiteMove = not temp_board.whiteMove
                temp_board.undoMove()
            self.possible_en_passant = temp_possible_en_passant
            return validMoves
        return

    def undoMove(self):
        if self.moveHistory:
            move = self.moveHistory.pop()
            self.board[move.endRow][move.endColumn] = move.capturedPiece
            self.board[move.startRow][move.startColumn] = move.movedPiece
            move.movedPiece.moved = False
            self.whiteMove = not self.whiteMove
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.startRow, move.startColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.startRow, move.startColumn)
            if move.is_en_passant_move:
                self.board[move.endRow][move.endColumn] = None
                self.board[move.startRow][move.endColumn] = move.capturedPiece
                self.possible_en_passant = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and abs(move.startRow - move.endRow) == 2:
                self.possible_en_passant = ()
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.startRow][move.startColumn] = move.movedPiece
                    self.board[move.endRow][7] = self.board[move.endRow][move.endColumn - 1]
                    self.board[move.endRow][move.endColumn - 1] = None
                else:
                    self.board[move.startRow][move.startColumn] = move.movedPiece
                    self.board[move.endRow][0] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][move.endColumn + 1] = None

    def inCheck(self):
        if self.whiteMove:
            return self.get_square_under_attack(self.whiteKingPosition)
        else:
            return self.get_square_under_attack(self.blackKingPosition)

    def castling(self, move: Move):
        pass

    def get_square_under_attack(self, position):
        self.whiteMove = not self.whiteMove
        oppMoves = self.getAllPossibleMoves()
        for move in oppMoves:
            if move.endRow == position[0] and move.endColumn == position[1]:
                self.whiteMove = not self.whiteMove
                return True
        self.whiteMove = not self.whiteMove
        return False

    def getAllPossibleMoves(self):
        allyMoves = []
        for row in range(8):
            for column in range(8):
                if self.board[row][column]:
                    if (self.board[row][column].piece_color == WHITE and self.whiteMove) or (
                            self.board[row][column].piece_color == BLACK and not self.whiteMove
                    ):
                        for move in self.generate_moves_for_piece(row, column):
                            allyMoves.append(move)
        return allyMoves

    def is_en_passant(self, move: Move) -> bool:
        return abs(move.startRow - move.endRow) == 2

    def is_piece(self, position: tuple) -> bool:
        """
        Проверяет позицию на наличие фигуры независимо от цвета
        """
        if self.board[position[0]][position[1]]:
            return True
        return False

    def is_legal(self, move: Move) -> bool:
        return True if move in self.getValidMoves() else False

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
                self.winner = BLACK if self.whiteMove else WHITE
                return True
        return False

    def is_variant_check(self) -> bool:
        return self.get_square_under_attack(self.blackKingPosition if not self.whiteMove
                                            else self.whiteKingPosition)

    def _setup_board(self):
        self.board[1][7] = Pawn(piece_color=BLACK)  # Пешки черного цвета.
        self.board[1][6] = Pawn(piece_color=BLACK)
        self.board[1][5] = Pawn(piece_color=BLACK)
        self.board[1][4] = Pawn(piece_color=BLACK)
        self.board[1][3] = Pawn(piece_color=BLACK)
        self.board[1][2] = Pawn(piece_color=BLACK)
        self.board[1][1] = Pawn(piece_color=BLACK)
        self.board[1][0] = Pawn(piece_color=BLACK)

        self.board[1][3] = Pawn(piece_color=BLACK)
        self.board[1][2] = Pawn(piece_color=BLACK)
        self.board[1][1] = Pawn(piece_color=BLACK)
        self.board[1][0] = Pawn(piece_color=BLACK)
        self.board[6][0] = Pawn(piece_color=WHITE)  # Пешки белого цвета.
        self.board[6][1] = Pawn(piece_color=WHITE)
        self.board[6][2] = Pawn(piece_color=WHITE)
        self.board[6][3] = Pawn(piece_color=WHITE)
        self.board[6][4] = Pawn(piece_color=WHITE)
        self.board[6][5] = Pawn(piece_color=WHITE)
        self.board[6][6] = Pawn(piece_color=WHITE)
        self.board[6][7] = Pawn(piece_color=WHITE)

        self.board[7][1] = Knight(piece_color=WHITE)  # Легкие фигуры белого цвета.
        self.board[7][2] = Bishop(piece_color=WHITE)
        self.board[7][5] = Bishop(piece_color=WHITE)
        self.board[7][6] = Knight(piece_color=WHITE)

        self.board[0][1] = Knight(piece_color=BLACK)  # Легкие фигуры черного цвета.
        self.board[0][2] = Bishop(piece_color=BLACK)
        self.board[0][5] = Bishop(piece_color=BLACK)
        self.board[0][6] = Knight(piece_color=BLACK)

        self.board[7][0] = Rook(piece_color=WHITE)  # Тяжелые фигуры белого цвета.
        self.board[7][3] = Queen(piece_color=WHITE)
        self.board[7][7] = Rook(piece_color=WHITE)

        self.board[0][0] = Rook(piece_color=BLACK)  # Тяжелые фигуры черного цвета.
        self.board[0][3] = Queen(piece_color=BLACK)
        self.board[0][7] = Rook(piece_color=BLACK)
        self.board[7][4] = King(piece_color=WHITE)  # Белый король.
        self.board[0][4] = King(piece_color=BLACK)  # Черный король.

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


class ClassicChess(BaseBoard):  # TODO-LIST: Доделать классы для режимов игры и реализовать таймер для классической игры
    pass


class OppositeChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()

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
                self.winner = BLACK if not self.whiteMove else WHITE
                return True
        return False

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove


class UntilTheFirstCheck(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove


class LOSChess(BaseBoard):
    pass


class MarseilleChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()
        self.now_move = 1

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            if self.now_move < 2:
                self.now_move += 1
                if self.get_square_under_attack(self.whiteKingPosition
                                                if not self.whiteMove else self.blackKingPosition):
                    self.game_end = True
            else:
                self.now_move = 1
                self.whiteMove = not self.whiteMove


class MiniChess(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove

    def _setup_board(self):
        self.board[1][0] = Pawn(piece_color=BLACK)  # Фигуры черного цвета.
        self.board[1][1] = Pawn(piece_color=BLACK)
        self.board[1][2] = Pawn(piece_color=BLACK)
        self.board[1][3] = Pawn(piece_color=BLACK)
        self.board[1][4] = Pawn(piece_color=BLACK)
        self.board[0][0] = Rook(piece_color=BLACK)
        self.board[0][4] = King(piece_color=BLACK)
        self.board[0][1] = Knight(piece_color=BLACK)
        self.board[0][2] = Bishop(piece_color=BLACK)
        self.board[0][3] = Queen(piece_color=BLACK)

        self.board[3][0] = Pawn(piece_color=WHITE)  # Фигуры белого цвета.
        self.board[3][1] = Pawn(piece_color=WHITE)
        self.board[3][2] = Pawn(piece_color=WHITE)
        self.board[3][3] = Pawn(piece_color=WHITE)
        self.board[3][4] = Pawn(piece_color=WHITE)
        self.board[4][0] = Rook(piece_color=WHITE)
        self.board[4][4] = King(piece_color=WHITE)
        self.board[4][1] = Knight(piece_color=WHITE)
        self.board[4][2] = Bishop(piece_color=WHITE)
        self.board[4][3] = Queen(piece_color=WHITE)


class WithoutTimerChess(BaseBoard):  # определение класса Board для доски
    def __init__(self):
        super().__init__()
        self._setup_board()

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove


class BirdChess(BaseBoard):
    pass


class NukeBoard(BaseBoard):
    def __init__(self):
        super().__init__()
        self._setup_board()

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            if move.capturedPiece:
                self.board[move.endRow][move.endColumn] = None
                if (move.endRow - 1 >= 0 and self.board[move.endRow - 1][move.endColumn] and
                        self.board[move.endRow - 1][move.endColumn].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow - 1][move.endColumn], King):
                        self.game_end = True
                    self.board[move.endRow - 1][move.endColumn] = None

                if (move.endRow + 1 <= 7 and self.board[move.endRow + 1][move.endColumn] and
                        self.board[move.endRow + 1][move.endColumn].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow + 1][move.endColumn], King):
                        self.game_end = True
                    self.board[move.endRow + 1][move.endColumn] = None

                if (move.endColumn + 1 <= 7 and self.board[move.endRow][move.endColumn + 1] and
                        self.board[move.endRow][move.endColumn + 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow][move.endColumn + 1], King):
                        self.game_end = True
                    self.board[move.endRow][move.endColumn + 1] = None

                if (move.endColumn - 1 <= 7 and self.board[move.endRow][move.endColumn - 1] and
                        self.board[move.endRow][move.endColumn - 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow][move.endColumn - 1], King):
                        self.game_end = True
                    self.board[move.endRow][move.endColumn - 1] = None

                if (move.endRow - 1 >= 0 <= move.endColumn - 1 and self.board[move.endRow - 1][move.endColumn - 1] and
                        self.board[move.endRow - 1][move.endColumn - 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow - 1][move.endColumn - 1], King):
                        self.game_end = True
                    self.board[move.endRow - 1][move.endColumn - 1] = None

                if (move.endRow + 1 <= 7 and 0 <= move.endColumn - 1 and self.board[move.endRow + 1][move.endColumn - 1]
                        and self.board[move.endRow + 1][move.endColumn - 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow + 1][move.endColumn - 1], King):
                        self.game_end = True
                    self.board[move.endRow + 1][move.endColumn - 1] = None

                if (move.endRow + 1 <= 7 and 7 >= move.endColumn + 1 and self.board[move.endRow + 1][move.endColumn + 1]
                        and self.board[move.endRow + 1][move.endColumn + 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow + 1][move.endColumn + 1], King):
                        self.game_end = True
                    self.board[move.endRow + 1][move.endColumn + 1] = None

                if (move.endRow - 1 <= 7 and 7 >= move.endColumn + 1 and self.board[move.endRow - 1][move.endColumn + 1]
                        and self.board[move.endRow - 1][move.endColumn + 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow - 1][move.endColumn + 1], King):
                        self.game_end = True
                    self.board[move.endRow - 1][move.endColumn + 1] = None

                if (move.endRow - 1 <= 7 and 0 <= move.endColumn - 1 and self.board[move.endRow - 1][move.endColumn - 1]
                        and self.board[move.endRow - 1][move.endColumn - 1].piece_color != move.movedPiece.piece_color):
                    if isinstance(self.board[move.endRow - 1][move.endColumn - 1], King):
                        self.game_end = True
                    self.board[move.endRow - 1][move.endColumn - 1] = None
                if isinstance(move.movedPiece, King):
                    for row in range(len(self.board)):
                        for column in range(len(self.board)):
                            if (self.board[row][column] and
                                    self.board[row][column].piece_color == move.movedPiece.piece_color):
                                self.board[row][column] = None
                    self.game_end = True

            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove


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

    def make_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            if isinstance(move.movedPiece, Pawn) and self.is_en_passant(move):
                self.possible_en_passant = ((move.startRow + move.endRow) // 2, move.startColumn)
            else:
                self.possible_en_passant = ()
            if move.is_en_passant_move:
                self.board[move.startRow][move.endColumn] = None
            if move.is_castle_move:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][7] = None
                else:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                    self.board[move.endRow][move.endColumn - 2] = None
            if move.is_promotion_move:
                self.piece_to_promote = (move.endRow, move.endColumn)
            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove

    def _setup_board(self):
        self.board[1][7] = Pawn(piece_color=BLACK)  # Пешки черного цвета.
        self.board[1][6] = Pawn(piece_color=BLACK)
        self.board[1][5] = Pawn(piece_color=BLACK)
        self.board[1][4] = Pawn(piece_color=BLACK)
        self.board[1][3] = Pawn(piece_color=BLACK)
        self.board[1][2] = Pawn(piece_color=BLACK)
        self.board[1][1] = Pawn(piece_color=BLACK)
        self.board[1][0] = Pawn(piece_color=BLACK)

        self.board[6][0] = Pawn(piece_color=WHITE)  # Пешки белого цвета.
        self.board[6][1] = Pawn(piece_color=WHITE)
        self.board[6][2] = Pawn(piece_color=WHITE)
        self.board[6][3] = Pawn(piece_color=WHITE)
        self.board[6][4] = Pawn(piece_color=WHITE)
        self.board[6][5] = Pawn(piece_color=WHITE)
        self.board[6][6] = Pawn(piece_color=WHITE)
        self.board[6][7] = Pawn(piece_color=WHITE)

        positions = random960()
        for i in range(len(positions)):
            if positions[i] == 'B':
                self.board[0][i] = Bishop(BLACK)
            elif positions[i] == 'N':
                self.board[0][i] = Knight(BLACK)
            elif positions[i] == 'R':
                self.board[0][i] = Rook(BLACK)
            elif positions[i] == 'K':
                self.board[0][i] = King(BLACK)
                self.blackKingPosition = (0, i)
            elif positions[i] == 'Q':
                self.board[0][i] = Queen(BLACK)
        for i in range(len(positions)):
            if positions[i] == 'B':
                self.board[7][i] = Bishop(WHITE)
            elif positions[i] == 'N':
                self.board[7][i] = Knight(WHITE)
            elif positions[i] == 'R':
                self.board[7][i] = Rook(WHITE)
            elif positions[i] == 'K':
                self.board[7][i] = King(WHITE)
                self.whiteKingPosition = (7, i)
            elif positions[i] == 'Q':
                self.board[7][i] = Queen(WHITE)


class Checkers:
    pass

