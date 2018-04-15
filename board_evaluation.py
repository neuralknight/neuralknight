# import adam's module up here
from random import randint
from numpy import array as ndarray

def evaluate_boards(boards):
    '''Determine value for each board state in array of board states
    
    Inputs:
        boards: Array of board states

    Outputs:
        best_state: The highest valued board state in the array

    '''

    # Piece values
    pawn_val = 1
    knight_val = 3
    bishop_val = 3
    rook_val = 5
    queen_val = 10
    king_val = 200

    # Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
    pawn_squares = [
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 27, 27, 10,  5,  5,
         0,  0,  0, 25, 25,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-25,-25, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0,
    ]

    knight_squares = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-20,-30,-30,-20,-40,-50,
    ]

    bishop_squares = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-40,-10,-10,-40,-10,-20,
    ]

    king_squares = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-40,-10,-10,-40,-10,-20,
    ]

    # Translate encoding
    own_pawn = 9
    own_knight = 7
    own_bishop = 3
    own_rook = 13
    own_queen = 11
    own_king = 5

    opp_pawn = 8
    opp_knight = 6
    opp_bishop = 2
    opp_rook = 12
    opp_queen = 10
    opp_king = 4
    
    boards = (([[12, 6, 2, 10, 4, 2, 6, 12], [8, 8, 8, 8, 8, 8, 8, 8], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [9, 9, 9, 9, 9, 9, 9, 9], [13, 7, 3, 11, 5, 3, 7, 13]]))

    for board in boards:


