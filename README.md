# Atomic Chess
ChessVar class for playing an abstract board game that is a variant of chess--atomic chess. 

Locations on the board will be specified using "algebraic notation", with columns labeled a-h and rows labeled 1-8

### Basic Rules:
- As in standard chess, white moves first.
- Pieces move and capture the same as in standard chess, except that there is no check or checkmate, and there is no castling, en passant, or pawn promotion.
- As in standard chess, each pawn should be able to move two spaces forward on its first move (but not on subsequent moves).

### Special rules for this variant of chess:
In Atomic Chess, whenever a piece is captured, an **explosion** occurs at the 8 squares immediately surrounding the captured piece in all the directions. This explosion kills all of the pieces in its range except for pawns. Different from regular chess, where only the captured piece is taken off the board, in Atomic Chess, every capture is suicidal. Even the capturing piece is affected by the explosion and must be taken off the board.

As a result, a pawn can only be removed from the board when directly involved in a capture. If that is the case, both capturing and captured pawns must be removed from the board.

Because every capture causes an explosion that affects not only the victim but also the capturing piece itself, the king is not allowed to make captures. Also, a player cannot blow up both kings at the same time. In other words, the move that would kill both kings in one step is not allowed. Blowing up a king has the same effect as capturing it, which will end the game

**If a player's king is captured or blown up, the game ends, and that player loses.**