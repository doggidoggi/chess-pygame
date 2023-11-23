import copy
from config import *
from piece import *
from move import *


class BaseBoard:
    def __init__(self):
        self.whiteMove = True
        self.checked = False
        self.checkmate = False
        self.stalemate = False
        self.whiteKingPosition = (7, 4)
        self.blackKingPosition = (0, 4)
        self.moveHistory = []
        self.game_end = False
        self.board = [[None] * 8 for _ in range(8)]
        squares_under_attack = []
        self.possible_en_passant = ()


class Board(BaseBoard):  # определение класса Board для доски
    def __init__(self):
        super().__init__()
        self._setup_board()

    def generate_moves_for_piece(self, row, column):
        moves = []
        enemyColor = BLACK if self.whiteMove else WHITE
        allyColor = WHITE if self.whiteMove else BLACK
        for_piece: Piece = self.board[row][column]

        def pawn_moves():
            if self.whiteMove:
                if self.board[row - 1][column] is None:
                    moves.append(Move((row, column), (row - 1, column),
                                      self))
                    if row == 6 and self.board[row - 2][column] is None:
                        moves.append(Move((row, column), (row - 2, column),
                                          self))
                if column - 1 >= 0:
                    if self.board[row - 1][column - 1] and self.board[row - 1][column - 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row - 1, column - 1),
                                          self))
                    elif (row - 1, column - 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row - 1, column - 1),
                                          self))
                if column + 1 <= 7:
                    if self.board[row - 1][column + 1] and self.board[row - 1][column + 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row - 1, column + 1),
                                          self))
                    elif (row - 1, column + 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row - 1, column + 1),
                                          self))

            else:

                if self.board[row + 1][column] is None:
                    moves.append(Move((row, column), (row + 1, column),
                                      self))
                    if row == 1 and self.board[row + 2][column] is None:
                        moves.append(Move((row, column), (row + 2, column),
                                          self))
                if column - 1 >= 0:
                    if self.board[row + 1][column - 1] and self.board[row + 1][column - 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row + 1, column - 1),
                                          self))
                    elif (row + 1, column - 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row + 1, column - 1),
                                          self))
                if column + 1 <= 7:
                    if self.board[row + 1][column + 1] and self.board[row + 1][column + 1].piece_color == enemyColor:
                        moves.append(Move((row, column), (row + 1, column + 1),
                                          self))
                    elif (row + 1, column + 1) == self.possible_en_passant:
                        moves.append(Move((row, column), (row + 1, column + 1),
                                          self))

        def bishop_moves():
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # направо, налево
            for direction in directions:
                for length in range(1, SQUARES_AMOUNT):
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
                for length in range(1, SQUARES_AMOUNT):
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
                for length in range(1, SQUARES_AMOUNT):
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

    def get_castle_moves(self, row, column, moves):
        left_rook_position: Piece = self.board[row][0]
        right_rook_position: Piece = self.board[row][7]
        king: Piece = self.board[row][column]
        if self.inCheck():
            return
        if (self.whiteMove and left_rook_position and not left_rook_position.moved and not king.moved) or (
                left_rook_position and not self.whiteMove and not left_rook_position.moved and not king.moved):
            self.get_king_castling(row, column, moves)
        if (self.whiteMove and right_rook_position and not right_rook_position.moved and not king.moved) or (
                right_rook_position and not self.whiteMove and not right_rook_position.moved and not king.moved):
            self.get_queen_castling(row, column, moves)

    def get_king_castling(self, row, column, moves):
        if self.board[row][column + 1] is None and self.board[row][column + 2] is None:
            if not self.get_square_under_attack((row, column + 1)) and not self.get_square_under_attack((row, column + 2)):
                moves.append(Move((row, column), (row, column + 2), self, is_castle=True))

    def get_queen_castling(self, row, column, moves):
        if self.board[row][column - 1] is None and self.board[row][column - 2] is None and self.board[row][column - 3] is None:
            if not self.get_square_under_attack((row, column - 1)) and not self.get_square_under_attack((row, column - 2)):
                moves.append(Move((row, column), (row, column - 2), self, is_castle=True))

    def getValidMoves(self):
        temp_board = copy.deepcopy(self)
        temp_possible_en_passant = copy.deepcopy(self.possible_en_passant)
        validMoves = temp_board.getAllPossibleMoves()
        if temp_board.whiteMove:
            temp_board.get_castle_moves(self.whiteKingPosition[0], self.whiteKingPosition[1], validMoves)
        else:
            temp_board.get_castle_moves(self.blackKingPosition[0], self.blackKingPosition[1], validMoves)
        for i in range(len(validMoves) - 1, -1, -1):
            temp_board._test_move(validMoves[i])
            temp_board.whiteMove = not temp_board.whiteMove
            if temp_board.inCheck():
                validMoves.remove(validMoves[i])
            temp_board.whiteMove = not temp_board.whiteMove
            temp_board.undoMove()
        self.possible_en_passant = temp_possible_en_passant
        return validMoves

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

    def _test_move(self, move: Move):
        if (move.movedPiece.piece_color == WHITE and self.whiteMove or
                move.movedPiece.piece_color == BLACK and not self.whiteMove):
            self.moveHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.symbol() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.symbol() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            elif isinstance(move.movedPiece, Pawn):
                if self.is_en_passant(move):
                    move.movedPiece.en_passant = True
                else:
                    move.movedPiece.en_passant = False
            self.whiteMove = not self.whiteMove

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

            move.movedPiece.moved = True
            self.whiteMove = not self.whiteMove

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
        for row in range(SQUARES_AMOUNT):
            for column in range(SQUARES_AMOUNT):
                if self.board[row][column]:
                    if (self.board[row][column].piece_color == WHITE and self.whiteMove) or (
                            self.board[row][column].piece_color == BLACK and not self.whiteMove
                    ):
                        for move in self.generate_moves_for_piece(row, column):
                            allyMoves.append(move)
        return allyMoves

    def is_en_passant(self, move: Move) -> bool:
        return abs(move.startRow - move.endRow) == 2

    def is_promotion(self, move: Move) -> bool:
        return move.endRow == 7 or move.endRow == 0

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
        validMoves = self.getValidMoves()
        if len(validMoves) == 0 and self.inCheck():
            self.checkmate = True
            self.game_end = True
            return True
        return False

    def is_variant_stalemate(self) -> bool:
        validMoves = self.getValidMoves()
        if len(validMoves) == 0 and not self.inCheck():
            self.stalemate = True
            self.game_end = True
            return True
        return False

    def is_variant_check(self) -> bool:
        return self.get_square_under_attack(self.blackKingPosition if not self.whiteMove
                                            else self.whiteKingPosition)

    def _setup_board(self):
        """
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
        """
        """
        self.board[7][1] = Knight(piece_color=WHITE)  # Легкие фигуры белого цвета.
        self.board[7][2] = Bishop(piece_color=WHITE)
        self.board[7][5] = Bishop(piece_color=WHITE)
        self.board[7][6] = Knight(piece_color=WHITE)
        self.board[0][1] = Knight(piece_color=BLACK)  # Легкие фигуры черного цвета.
        self.board[0][2] = Bishop(piece_color=BLACK)
        self.board[0][5] = Bishop(piece_color=BLACK)
        self.board[0][6] = Knight(piece_color=BLACK)
        """
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
