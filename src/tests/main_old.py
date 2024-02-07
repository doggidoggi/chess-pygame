import traceback
import pygame
import sys

WHITE = 1
BLACK = 2
WIDTH = HEIGHT = 600  # размеры окна
SQUARES_AMOUNT = 8  # количество клеток
SQUARE_SIZE = WIDTH // SQUARES_AMOUNT  # размеры одной шахматной клетки
IMAGES = {}  # изображения, которые будут загружаться во время старта игры
FPS = 30  # кадры в секунду
SQUARE_COLORS = [pygame.Color(184, 139, 74), pygame.Color(227, 193, 111)]  # цвета клеток для шахматной доски
rowsToSquares = {'7': 1, '6': 2, '5': 3, '4': 4,
                 '3': 5, '2': 6, '1': 7, '0': 8}
colsToSquares = {'0': 'a', '1': 'b', '2': 'c', '3': 'd',
                 '4': 'e', '5': 'f', '6': 'g', '7': 'h'}


class Pawn:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color
        if self.color == WHITE:
            self.direction = -1  # Пешка может сделать из начального положения ход на 2 клетки
            self.start_row = 6  # вперёд, поэтому поместим индекс начального ряда в start_row.
        else:
            self.direction = 1
            self.start_row = 1

    def set_position(self, row, column):
        self.row = row
        self.column = column

    def getName(self):
        return 'wPawn' if self.color == WHITE else 'bPawn'

    def getColor(self):
        return self.color


class Bishop:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color

    def set_position(self, new_row, new_column):
        self.row = new_row
        self.column = new_column

    def getName(self):
        return 'wBishop' if self.color == WHITE else 'bBishop'

    def getColor(self):
        return self.color


class Knight:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color

    def set_position(self, new_row, new_column):
        self.row = new_row
        self.column = new_column

    def getName(self):
        return 'wKnight' if self.color == WHITE else 'bKnight'

    def getColor(self):
        return self.color


class Queen:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color

    def set_position(self, new_row, new_col):
        self.row = new_row
        self.column = new_col

    def getName(self):
        return 'wQueen' if self.color == WHITE else 'bQueen'

    def getColor(self):
        return self.color


class Rook:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color

    def set_position(self, new_row, new_col):
        self.row = new_row
        self.column = new_col

    def getName(self):
        return 'wRook' if self.color == WHITE else 'bRook'

    def getColor(self):
        return self.color


class King:
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color

    def set_position(self, new_row, new_col):
        self.row = new_row
        self.column = new_col

    def getName(self):
        return 'wKing' if self.color == WHITE else 'bKing'

    def getColor(self):
        return self.color


class Move:
    def __init__(self, startPosition, endPosition, board):
        self.movedPiece = board[startPosition[0]][startPosition[1]]
        self.startRow = startPosition[0]
        self.startColumn = startPosition[1]
        self.endRow = endPosition[0]
        self.endColumn = endPosition[1]
        self.capturedPiece = board[endPosition[0]][endPosition[1]]
        rowsToSquares = {'7': 1, '6': 2, '5': 3, '4': 4,
                         '3': 5, '2': 6, '1': 7, '0': 8}
        colsToSquares = {'0': 'a', '1': 'b', '2': 'c', '3': 'd',
                         '4': 'e', '5': 'f', '6': 'g', '7': 'h'}

    def __eq__(self, other):
        if (self.startRow, self.startColumn, self.endColumn, self.endRow) == (
                other.startRow, other.startColumn, other.endColumn, other.endRow):
            return True


class Board:  # определение класса Board для доски
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.board[1][7] = Pawn(row=1, column=7, color=BLACK)  # Пешки черного цвета.
        self.board[1][6] = Pawn(row=1, column=6, color=BLACK)
        self.board[1][5] = Pawn(row=1, column=5, color=BLACK)
        self.board[1][4] = Pawn(row=1, column=4, color=BLACK)
        self.board[1][3] = Pawn(row=1, column=3, color=BLACK)
        self.board[1][2] = Pawn(row=1, column=2, color=BLACK)
        self.board[1][1] = Pawn(row=1, column=1, color=BLACK)
        self.board[1][0] = Pawn(row=1, column=0, color=BLACK)
        self.board[6][0] = Pawn(row=6, column=0, color=WHITE)  # Пешки белого цвета.
        self.board[6][1] = Pawn(row=6, column=1, color=WHITE)
        self.board[6][2] = Pawn(row=6, column=2, color=WHITE)
        self.board[6][3] = Pawn(row=6, column=3, color=WHITE)
        self.board[6][4] = Pawn(row=6, column=4, color=WHITE)
        self.board[6][5] = Pawn(row=6, column=5, color=WHITE)
        self.board[6][6] = Pawn(row=6, column=6, color=WHITE)
        self.board[6][7] = Pawn(row=6, column=7, color=WHITE)
        self.board[7][1] = Knight(row=7, column=1, color=WHITE)  # Легкие фигуры белого цвета.
        self.board[7][2] = Bishop(row=7, column=2, color=WHITE)
        self.board[7][5] = Bishop(row=7, column=5, color=WHITE)
        self.board[7][6] = Knight(row=7, column=6, color=WHITE)
        self.board[0][1] = Knight(row=0, column=1, color=BLACK)  # Легкие фигуры черного цвета.
        self.board[0][2] = Bishop(row=0, column=2, color=BLACK)
        self.board[0][5] = Bishop(row=0, column=5, color=BLACK)
        self.board[0][6] = Knight(row=0, column=6, color=BLACK)
        self.board[7][0] = Rook(row=7, column=0, color=WHITE)  # Тяжелые фигуры белого цвета.
        self.board[7][3] = Queen(row=7, column=3, color=WHITE)
        self.board[7][7] = Rook(row=7, column=7, color=WHITE)
        self.board[0][0] = Rook(row=0, column=0, color=BLACK)  # Тяжелые фигуры черного цвета.
        self.board[0][3] = Queen(row=0, column=3, color=BLACK)
        self.board[0][7] = Rook(row=0, column=7, color=BLACK)
        self.board[7][4] = King(row=7, column=4, color=WHITE)  # Белый король.
        self.board[0][4] = King(row=0, column=4, color=BLACK)  # Черный король.
        self.whiteMove = True
        self.whiteKingPosition = (7, 4)
        self.blackKingPosition = (0, 4)
        self.movesHistory = []

    def generatePieceAllPossibleMoves(self, row, column):
        moves = []
        enemyColor = BLACK if self.whiteMove else WHITE
        allyColor = WHITE if self.whiteMove else BLACK
        if self.board[row][column].getName()[1:] == 'Pawn':
            if self.whiteMove:
                if self.board[row - 1][column] is None:
                    moves.append(Move((row, column), (row - 1, column),
                                      self.board))
                    if row == 6 and self.board[row - 2][column] is None:
                        moves.append(Move((row, column), (row - 2, column),
                                          self.board))
                if (column - 1 >= 0 and self.board[row - 1][column - 1] and
                        self.board[row - 1][column - 1].getColor() == enemyColor):
                    moves.append(Move((row, column), (row - 1, column - 1),
                                      self.board))
                if (column + 1 <= 7 and self.board[row - 1][column + 1] and
                        self.board[row - 1][column + 1].getColor() == enemyColor):
                    moves.append(Move((row, column), (row - 1, column + 1),
                                      self.board))
            else:
                if self.board[row + 1][column] is None:
                    moves.append(Move((row, column), (row + 1, column),
                                      self.board))
                    if row == 1 and self.board[row + 2][column] is None:
                        moves.append(Move((row, column), (row + 2, column),
                                          self.board))
                if (column - 1 >= 0 and self.board[row + 1][column - 1] and
                        self.board[row + 1][column - 1].getColor() == enemyColor):
                    moves.append(Move((row, column), (row + 1, column - 1),
                                      self.board))
                if (column + 1 <= 7 and self.board[row + 1][column + 1] and
                        self.board[row + 1][column + 1].getColor() == enemyColor):
                    moves.append(Move((row, column), (row + 1, column + 1),
                                      self.board))
        elif self.board[row][column].getName()[1:] == 'Bishop':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # направо, налево
            for direction in directions:
                for length in range(1, SQUARES_AMOUNT):
                    endRow = row + direction[0] * length
                    endColumn = column + direction[1] * length
                    if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                        if self.board[endRow][endColumn] is None:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self.board))
                        elif self.board[endRow][endColumn].getColor() == enemyColor:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self.board))
                            break
                        elif self.board[endRow][endColumn].getColor() == allyColor:
                            break
        elif self.board[row][column].getName()[1:] == 'Queen':
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # направо, налево
            for direction in directions:
                for length in range(1, SQUARES_AMOUNT):
                    endRow = row + direction[0] * length
                    endColumn = column + direction[1] * length
                    if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                        if self.board[endRow][endColumn] is None:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self.board))
                        elif self.board[endRow][endColumn].getColor() == enemyColor:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self.board))
                            break
                        elif self.board[endRow][endColumn].getColor() == allyColor:
                            break
        elif self.board[row][column].getName()[1:] == 'King':
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for direction in directions:
                endRow = row + direction[0]
                endColumn = column + direction[1]
                if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                    # print(endRow, endColumn)
                    if self.board[endRow][endColumn] and self.board[endRow][endColumn].getColor() == allyColor:
                        continue
                    else:
                        moves.append(Move((row, column), (endRow, endColumn),
                                          self.board))
        elif self.board[row][column].getName()[1:] == 'Knight':
            directions = [(2, -1), (1, -2), (2, 1), (1, 2), (-2, -1), (-1, -2), (-2, 1), (-1, 2)]  # направо, налево
            for direction in directions:
                endRow = row + direction[0]
                endColumn = column + direction[1]
                if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                    if self.board[endRow][endColumn] is None:
                        moves.append(Move((row, column), (endRow, endColumn),
                                          self.board))
                    elif self.board[endRow][endColumn].getColor() == enemyColor:
                        moves.append(Move((row, column), (endRow, endColumn),
                                          self.board))
                        continue
                    elif self.board[endRow][endColumn].getColor() == allyColor:
                        continue
        elif self.board[row][column].getName()[1:] == 'Rook':
            directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # направо, налево, вниз, вверх
            for direction in directions:
                for length in range(1, SQUARES_AMOUNT):
                    endRow = row + direction[0] * length
                    endColumn = column + direction[1] * length
                    if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                        if self.board[endRow][endColumn] is None:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self.board))
                        elif self.board[endRow][endColumn].getColor() == enemyColor:
                            moves.append(Move((row, column), (endRow, endColumn),
                                              self.board))
                            break
                        elif self.board[endRow][endColumn].getColor() == allyColor:
                            break
        return moves

    def piece_color(self, piece):
        color = piece.getColor()
        return color

    def getValidMoves(self):
        validMoves = self.getAllPossibleMoves()
        for i in range(len(validMoves) - 1, -1, -1):
            self.make_move(validMoves[i])
            print(f'MOVED {colsToSquares.get(str(validMoves[i].startColumn))}'
                  f'{rowsToSquares.get(str(validMoves[i].startRow))}'
                  f'{colsToSquares.get(str(validMoves[i].endColumn))}'
                  f'{rowsToSquares.get(str(validMoves[i].endRow))}')
            self.whiteMove = not self.whiteMove
            if self.inCheck():
                print((f'REMOVED '
                       f'{colsToSquares.get(str(validMoves[i].startColumn))}'
                       f'{rowsToSquares.get(str(validMoves[i].startRow))}'
                       f'{colsToSquares.get(str(validMoves[i].endColumn))}'
                       f'{rowsToSquares.get(str(validMoves[i].endRow))}'))
                validMoves.remove(validMoves[i])
            self.whiteMove = not self.whiteMove
            self.undoMove()
        return validMoves

    def undoMove(self):
        if self.movesHistory:
            move = self.movesHistory.pop()
            self.board[move.endRow][move.endColumn] = move.capturedPiece
            self.board[move.startRow][move.startColumn] = move.movedPiece
            self.whiteMove = not self.whiteMove
            if move.movedPiece.getName() == 'wKing':
                self.whiteKingPosition = (move.startRow, move.startColumn)
                print(self.whiteKingPosition)
            elif move.movedPiece.getName() == 'bKing':
                self.blackKingPosition = (move.startRow, move.startColumn)
                print(self.blackKingPosition)

    def make_move(self, move: Move):
        if (self.piece_color(move.movedPiece) == WHITE and self.whiteMove or
                self.piece_color(move.movedPiece) == BLACK and not self.whiteMove):
            self.movesHistory.append(move)
            self.board[move.endRow][move.endColumn] = move.movedPiece
            self.board[move.startRow][move.startColumn] = None
            if move.movedPiece.getName() == 'wKing':
                self.whiteKingPosition = (move.endRow, move.endColumn)
            elif move.movedPiece.getName() == 'bKing':
                self.blackKingPosition = (move.endRow, move.endColumn)
            self.whiteMove = not self.whiteMove

    def inCheck(self):
        if self.whiteMove:
            return self.squareUnderAttack(self.whiteKingPosition[0], self.whiteKingPosition[1])
        else:
            return self.squareUnderAttack(self.blackKingPosition[0], self.blackKingPosition[1])

    def squareUnderAttack(self, row, column):
        self.whiteMove = not self.whiteMove
        oppMoves = self.getAllPossibleMoves()
        for move in oppMoves:
            if move.endRow == row and move.endColumn == column:
                print(move.endRow, move.endColumn, row, column)
                print(self.blackKingPosition)
                self.whiteMove = not self.whiteMove
                return True
        self.whiteMove = not self.whiteMove
        return False

    def getAllPossibleMoves(self):
        allyMoves = []
        for row in range(SQUARES_AMOUNT):
            for column in range(SQUARES_AMOUNT):
                if self.board[row][column]:
                    if (self.board[row][column].getColor() == WHITE and self.whiteMove) or (
                            self.board[row][column].getColor() == BLACK and not self.whiteMove
                    ):
                        for move in self.generatePieceAllPossibleMoves(row, column):
                            allyMoves.append(move)
        return allyMoves


class ChessEngine:
    def __init__(self, board):
        self.board = board

    def loadImages(self):
        pieces = ['bBishop', 'bKing', 'bKnight', 'bPawn', 'bQueen', 'bRook',
                  'wBishop', 'wKing', 'wKnight', 'wPawn', 'wQueen', 'wRook']
        for piece in pieces:
            IMAGES[piece] = pygame.image.load("../assets/images/pieces80/" + piece + ".png")

    def draw_board(self, screen):
        for row in range(SQUARES_AMOUNT):
            for column in range(SQUARES_AMOUNT):
                color = SQUARE_COLORS[(row + column) % 2]
                pygame.draw.rect(screen, color, (SQUARE_SIZE * column, SQUARE_SIZE * row,
                                                 SQUARE_SIZE, SQUARE_SIZE))

    def draw_squares_valid_moves(self, screen, board, selectedCell):
        if selectedCell:
            piece = board.ChessBoard[selectedCell[0]][selectedCell[1]]
            if piece:
                row, column = selectedCell
                surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                surface.set_alpha(100)
                surface.fill((1, 50, 32))
                screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))
                for move in board.generate_moves_for_piece(selectedCell[0], selectedCell[1]):
                    screen.blit(surface, (move.endColumn * SQUARE_SIZE, move.endRow * SQUARE_SIZE))

    def draw_pieces(self, screen):
        for row in range(SQUARES_AMOUNT):
            for column in range(SQUARES_AMOUNT):
                piece = self.board[row][column]
                if piece:
                    screen.blit(IMAGES[piece.getName()],
                                pygame.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def animation_move(self, coordinates, screen):
        coordinates = []
        for frame in range(FPS):
            coordinates.append(())
            self.draw_game(screen)

    def draw_game(self, screen, board, selectedCell):
        self.draw_board(screen)
        self.draw_squares_valid_moves(screen, board, selectedCell)
        self.draw_pieces(screen)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
    pygame.display.set_caption('Шахматы')
    screen.fill(color=pygame.Color(184, 139, 74))
    running = True
    clock = pygame.time.Clock()
    selectedCell = ()
    board = Board()
    validMoves = board.getValidMoves()
    game = ChessEngine(board.board)
    game.loadImages()
    playerClicks = []
    PIECE_MOVED_FLAG = False
    while running:  # цикл игры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # выход из игры
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                coordinates = event.pos
                row = coordinates[1] // SQUARE_SIZE
                column = coordinates[0] // SQUARE_SIZE
                piece = board.board[row][column]
                if piece or playerClicks:
                    if (row, column) == selectedCell:
                        selectedCell = ()
                        playerClicks = []
                    else:
                        selectedCell = (row, column)
                        playerClicks.append(selectedCell)
                if len(playerClicks) == 2:
                    move = (f'{colsToSquares.get(str(playerClicks[0][1]))}{rowsToSquares.get(str(playerClicks[0][0]))}'
                            f'{colsToSquares.get(str(selectedCell[1]))}{rowsToSquares.get(str(selectedCell[0]))}')
                    print(move)
                    if board.board[playerClicks[0][0]][playerClicks[0][1]] and Move((playerClicks[0][0],
                                                                                     playerClicks[0][1]),
                                                                                    (selectedCell[0], selectedCell[1]),
                                                                                    board.board) in validMoves:
                        board.make_move(Move((playerClicks[0][0], playerClicks[0][1]),
                                             (selectedCell[0], selectedCell[1]), board.board))
                        PIECE_MOVED_FLAG = True
                        playerClicks = []
                        selectedCell = ()
                    else:
                        selectedCell = ()
                        playerClicks = []
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                board.undoMove()
        game.draw_game(screen, board, selectedCell)
        clock.tick(FPS)
        pygame.display.flip()
        if PIECE_MOVED_FLAG:
            validMoves = board.getValidMoves()
            PIECE_MOVED_FLAG = not PIECE_MOVED_FLAG
    pygame.quit()


main()
