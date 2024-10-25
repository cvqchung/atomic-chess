# Description: A playable game of atomic chess with methods to move pieces, see the board, and see the game status.
#              Contains classes for the chess board itself, and the individual pieces with their respective move rules

from functools import wraps


class ChessVar:
    """
    Used to play a game of atomic chess! Pieces move and capture the same as standard chess.
    There is no check or checkmate, no castling, en passant, or pawn promotion
    Locations on the board will be in "algebraic notation": columns labeled a-h and rows labeled 1-8
    When a piece is captured, all pieces (except pawns) in the 8 squares surrounding the captured piece are killed
    Captures are suicidal. Pawns can only be removed by capture (not explosion). Kings cannot capture.

    Contains methods for making moves, viewing the board, and viewing the game status.
    """
    def __init__(self):
        self._board = ChessBoard(self)
        self._game_state = 'UNFINISHED'
        self._turn = 'w'

    def get_game_state(self):
        """Returns the state of the game: unfinished or black/white won"""
        return self._game_state

    def set_game_state(self, who_won):
        """
        Sets the state of the game in case of a win. Called by check_king
        Will set self._game_state to 'BLACK_WON' or 'WHITE_WON' depending on state
        """
        self._game_state = who_won

    def move_decorator(function):
        """Decorator function for make_move. Will change turn color after successful move is made"""
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            """Changes turn color if move is made successfully"""
            result = function(self, *args, **kwargs)
            if result is True:
                if self._turn == "w":
                    self._turn = "b"
                elif self._turn == "b":
                    self._turn = "w"
            return result
        return wrapper

    @move_decorator
    def make_move(self, point_A, point_B):
        """
        Takes 2 strings that represent the square being moved from (point_A) and the square being moved to (point_B)
        Calls ChessBoard to check move validity (check_move)
        If valid move: update the board with movement (move_piece), update game status (check_king), return True
        If invalid move: return False.
        Returns False if game has been won.
        """
        # return False if game has been won
        if self._game_state != "UNFINISHED":
            print("Error: This game has been finished")
            return False

        # check move
        result = self._board.check_move(point_A, point_B, self._turn)

        if result is False:
            return False
        # valid move! move the piece and update game status if necessary
        if result is True:
            self._board.move_piece(point_A, point_B)
            self._board.check_king()
            return True

    def print_board(self):
        """
        Outputs the current state of the board. Board is a dictionary of lists.
        first letter indicates player: w = white, b = black
        second letter indicates piece: P = pawn, B = bishop, N = knight, R = rook, Q = queen, K = king
        Prints self._board to console
        """
        print("   a  b  c  d  e  f  g  h")
        for row in self._board.get_board():
            print(row, end="  ")
            for space in self._board.get_board()[row]:
                if space == "_":
                    print("_ ", end=" ")
                else:
                    print(space.get_piece(), end=" ")
            print()


class ChessBoard:
    """
    Represents a chess board. Board is initialized with starting positions
    Moves will be made in ChessVar class, and valid moves will update ChessBoard
    Board is a dictionary of lists: key is rows (1-8), index is columns (a-h algebraic, 0-7 index)
    """
    def __init__(self, game):
        self._game = game           # holds the ChessVar object, aka the game!
        self._board = {
            8: [Rook("b"), Knight("b"), Bishop("b"), Queen("b"), King("b"), Bishop("b"), Knight("b"), Rook("b")],
            7: [Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b"), Pawn("b")],
            6: ["_", "_", "_", "_", "_", "_", "_", "_"],
            5: ["_", "_", "_", "_", "_", "_", "_", "_"],
            4: ["_", "_", "_", "_", "_", "_", "_", "_"],
            3: ["_", "_", "_", "_", "_", "_", "_", "_"],
            2: [Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w"), Pawn("w")],
            1: [Rook("w"), Knight("w"), Bishop("w"), Queen("w"), King("w"), Bishop("w"), Knight("w"), Rook("w")]
            }


    def get_board(self):
        """Returns the board in its current state"""
        return self._board

    def check_move(self, point_A, point_B, color):
        """
        Checks for move validity
        If no matching color piece is in point_A, return False.
        If the move kills both kings, return False.
        If movement does not match with chess piece's movement rules, return False.
        Calls moving piece's class for movement rules.
        If move is valid, return True and call move_piece to update the board.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                        # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])
        space_A = self._board[row_A][column_A]    # contains the item in point A and B
        space_B = self._board[row_B][column_B]

        # need matching color piece in point A
        if space_A == "_":
            return False
        if space_A.get_color() != color:
            return False
        # cannot capture your own piece
        if space_B != "_":
            if space_B.get_color() == color:
                return False
        # cannot move out of bounds
        if column_B > 7 or column_B < 0 or row_B > 8 or row_B < 0:
            return False

        # check piece's movement rules
        result = space_A.get_movement(point_A, point_B, color, self._board)
        if result is False:
            return False

        # check if the move kills both kings
        dead_white = False
        dead_black = False
        for row in range(row_B-1, row_B+2):
            for column in range(column_B-1, column_B+2):
                if row < 1 or row > 8 or column < 0 or column > 7:
                    continue
                if self._board[row][column] == "_":
                    continue
                if self._board[row][column].get_piece() == "wK":
                    dead_white = True
                if self._board[row][column].get_piece() == "bK":
                    dead_white = True
        if dead_white and dead_black:
            return False

        # move is confirmed valid!
        return True


    def move_piece(self, point_A, point_B):
        """
        Moves the piece. Updates the board to reflect movement and captures/explosions
        If moving to empty square, move the piece into point_B
        If moving to nonempty square, removes the mover, target, and all non-pawn pieces in the 8 surrounding squares
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                         # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        # if moving to empty square: simply move the piece
        if self._board[row_B][column_B] == "_":
            self._board[row_B][column_B] = self._board[row_A][column_A]
            self._board[row_A][column_A] = "_"
            return

        # if moving to nonempty square:
        # remove the mover and target
        self._board[row_A][column_A] = "_"
        self._board[row_B][column_B] = "_"

        # explosion! remove all surrounding pieces, except pawns
        for row in range(row_B-1, row_B+2):
            for column in range(column_B-1, column_B+2):
                if row < 1 or row > 8 or column < 0 or column > 7:
                    continue
                if self._board[row][column] == "_":
                    continue
                elif self._board[row][column].get_type() == "P":
                    continue
                else:
                    self._board[row][column] = "_"
        return

    def check_king(self):
        """
        Checks if kings are left on the board. 1 king remaining means that color wins
        Called after valid moves are made, to check if game is won
        If color won, call set_game_state to change the game state to '[COLOR]_WON'
        """
        white_king = False
        black_king = False
        for row in self._board:
            for space in self._board[row]:
                if space == "_":
                    continue
                if space.get_piece() == "wK":
                    white_king = True
                if space.get_piece() == "bK":
                    black_king = True
        if black_king and not white_king:
            self._game.set_game_state("BLACK_WON")
        if white_king and not black_king:
            self._game.set_game_state("WHITE_WON")


class Piece:
    """Represents any chess piece in a chess game. Will be inherited."""
    def __init__(self, color, letter):
        self._color = color
        self._letter = letter

    def get_piece(self):
        """Returns the piece as a string, as it is represented on the board (w_ or b_)"""
        return self._color + self._letter

    def get_color(self):
        """Returns the color of the piece. ie, white will return 'w' """
        return self._color

    def get_type(self):
        """Returns the type of piece. ie, pawn will return 'P' """
        return self._letter


class Pawn(Piece):
    """
    Represents a Pawn chess piece, and its movement/capture rules. Inherits from Piece
    Pawn NOT affected by explosion
    """
    def __init__(self, color):
        super().__init__(color, "P")

    def get_movement(self, point_A, point_B, color, board):
        """
        Contains the movement rules for the piece
        Returns True if movement can be made, returns False if not.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                     # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        if color == "w":
            # first move for white pawn
            if row_A == 2 and column_A == column_B:
                if row_B - row_A == 1 or row_B - row_A == 2:
                    return True
            # capture diagonally
            elif board[row_B][column_B] != "_" and row_B - row_A == 1:
                if abs(column_A - column_B) == 1:
                    return True
            # move forward to vacant spot
            elif board[row_B][column_B] == "_" and column_A == column_B and row_B - row_A == 1:
                return True

        elif color == "b":
            # first move for black pawn
            if row_A == 7 and column_A == column_B:
                if row_A - row_B == 1 or row_A - row_B == 2:
                    return True
            # capture diagonally
            elif board[row_B][column_B] != "_" and row_A - row_B == 1:
                if abs(column_B - column_A) == 1:
                    return True
            # move forward to vacant spot
            elif board[row_B][column_B] == "_" and column_A == column_B and row_A - row_B == 1:
                return True

        return False

class King(Piece):
    """
    Represents a King chess piece, and its movement/capture rules. Inherits from Piece
    King can NOT capture
    """
    def __init__(self, color):
        super().__init__(color, "K")

    def get_movement(self, point_A, point_B, color, board):
        """
        Contains the movement rules for the piece
        Returns True if movement can be made, returns False if not.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                     # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        # can only move to vacant spots (cannot capture)
        if board[row_B][column_B] != "_":
            return False

        # can move 1 square in any direction
        if row_A == row_B and abs(column_A - column_B) == 1:
            return True
        elif column_A == column_B and abs(row_A - row_B) == 1:
            return True
        elif abs(column_A - column_B) == 1 and abs(row_A - row_B) == 1:
            return True
        return False


class Knight(Piece):
    """Represents a Knight chess piece, and its movement/capture rules. Inherits from Piece"""
    def __init__(self, color):
        super().__init__(color, "N")

    def get_movement(self, point_A, point_B, color, board):
        """
        Contains the movement rules for the piece
        Returns True if movement can be made, returns False if not.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                     # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        # can move in L shape (2 squares, 1 square)
        if abs(row_A - row_B) == 2 and abs(column_A - column_B) == 1:
            return True
        if abs(column_A - column_B) == 2 and abs(row_A - row_B) == 1:
            return True
        return False


class Rook(Piece):
    """Represents a Rook chess piece, and its movement/capture rules. Inherits from Piece"""
    def __init__(self, color):
        super().__init__(color, "R")

    def get_movement(self, point_A, point_B, color, board):
        """
        Contains the movement rules for the piece
        Returns True if movement can be made, returns False if not.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                     # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        # can move in a straight line in any direction, path must be empty
        # move right
        if row_A == row_B and column_A < column_B:
            for column in range (column_A+1, column_B):
                if board[row_A][column] != "_":
                    return False
            return True
        # move left
        elif row_A == row_B and column_A > column_B:
            for column in range(column_B+1, column_A):
                if board[row_A][column] != "_":
                    return False
            return True
        # move up
        elif column_A == column_B and row_A < row_B:
            for row in range(row_A+1, row_B):
                if board[row][column_A] != "_":
                    return False
            return True
        # move down
        elif column_A == column_B and row_A > row_B:
            for row in range(row_B+1, row_A):
                if board[row][column_A] != "_":
                    return False
            return True
        return False


class Bishop(Piece):
    """Represents a Bishop chess piece, and its movement/capture rules. Inherits from Piece"""
    def __init__(self, color):
        super().__init__(color, "B")

    def get_movement(self, point_A, point_B, color, board):
        """
        Contains the movement rules for the piece
        Returns True if movement can be made, returns False if not.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                     # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        # can move diagonally in any direction, path must be empty
        if row_A == row_B or column_A == column_B:
            return False
        if abs(row_A - row_B) != abs(column_A - column_B):
            return False
        # move up and right
        if row_A < row_B and column_A < column_B:
            column = column_A + 1
            for row in range(row_A + 1, row_B):
                if board[row][column] != "_":
                    return False
                column += 1
            return True
        # move up and left
        elif row_A < row_B and column_A > column_B:
            column = column_A - 1
            for row in range(row_A + 1, row_B):
                if board[row][column] != "_":
                    return False
                column -= 1
            return True
        # move down and right
        elif row_A > row_B and column_A < column_B:
            column = column_B - 1
            for row in range(row_B + 1, row_A):
                if board[row][column] != "_":
                    return False
                column -= 1
            return True
        # move down and left
        elif row_A > row_B and column_A > column_B:
            column = column_B + 1
            for row in range(row_B + 1, row_A):
                if board[row][column] != "_":
                    return False
                column += 1
            return True
        return False


class Queen(Piece):
    """Represents a Queen chess piece, and its movement/capture rules. Inherits from Piece"""
    def __init__(self, color):
        super().__init__(color, "Q")

    def get_movement(self, point_A, point_B, color, board):
        """
        Contains the movement rules for the piece
        Returns True if movement can be made, returns False if not.
        """
        # get the row and column indices for point A and B, for easier indexing
        row_A = int(point_A[1])                     # contains the row number (key)
        row_B = int(point_B[1])
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        column_A = columns.index(point_A[0])        # contains the column's index
        column_B = columns.index(point_B[0])

        # can move in any direction, path must be empty

        # straight moves:
        # move right
        if row_A == row_B and column_A < column_B:
            for column in range (column_A+1, column_B):
                if board[row_A][column] != "_":
                    return False
            return True
        # move left
        elif row_A == row_B and column_A > column_B:
            for column in range(column_B+1, column_A):
                if board[row_A][column] != "_":
                    return False
            return True
        # move up
        elif column_A == column_B and row_A < row_B:
            for row in range(row_A+1, row_B):
                if board[row][column_A] != "_":
                    return False
            return True
        # move down
        elif column_A == column_B and row_A > row_B:
            for row in range(row_B+1, row_A):
                if board[row][column_A] != "_":
                    return False
            return True

        # diagonal moves
        # move up and right
        if row_A < row_B and column_A < column_B:
            column = column_A + 1
            for row in range(row_A + 1, row_B):
                if board[row][column] != "_":
                    return False
                column += 1
            return True
        # move up and left
        elif row_A < row_B and column_A > column_B:
            column = column_A - 1
            for row in range(row_A + 1, row_B):
                if board[row][column] != "_":
                    return False
                column -= 1
            return True
        # move down and right
        elif row_A > row_B and column_A < column_B:
            column = column_B - 1
            for row in range(row_B + 1, row_A):
                if board[row][column] != "_":
                    return False
                column -= 1
            return True
        # move down and left
        elif row_A > row_B and column_A > column_B:
            column = column_B + 1
            for row in range(row_B + 1, row_A):
                if board[row][column] != "_":
                    return False
                column += 1
            return True
        return False


