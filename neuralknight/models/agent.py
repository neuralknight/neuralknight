import requests
from random import randint
from numpy import array as ndarray

# PORT = 8080
API_URL = 'http://localhost:6543'

def evaluate_boards(boards):
    '''Determine value for each board state in array of board states
    
    Inputs:
        boards: Array of board states

    Outputs:
        best_state: The highest valued board state in the array

    '''

    # Piece values
    pawn_val = 100
    knight_val = 300
    bishop_val = 300
    rook_val = 500
    queen_val = 1000
    king_val = 20000

    # Piece squares - from http://www.chessbin.com/post/Piece-Square-Table
    # Own piece squares
    own_pawn_squares = [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [ 5,  5, 10, 27, 27, 10,  5,  5],
        [ 0,  0,  0, 25, 25,  0,  0,  0],
        [ 5, -5,-10,  0,  0,-10, -5,  5],
        [ 5, 10, 10,-25,-25, 10, 10,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
    ]
    own_knight_squares = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-20,-30,-30,-20,-40,-50],
    ]
    own_bishop_squares = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-40,-10,-10,-40,-10,-20],
    ]
    own_rook_squares = [
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
    ]
    own_king_squares = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-40,-10,-10,-40,-10,-20],
    ]
    
    #Opp piece squares
    opp_pawn_squares = [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [-5, -5,-10,-15,-15,-10,-5,-5],
        [-10,-10,-15,-25,-25,-15,-10,-10],
        [-20, -20,-25,-30,-30,-25,-20,-20],
        [-30,-30,-35,-40,-40,-35,-30,-30],
        [-50,-50,-50,-50,-50,-50,-50,-50],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
    ]
    opp_knight_squares = [ # temp zeroed below
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-20,-30,-30,-20,-40,-50],
    ]
    opp_bishop_squares = [ # temp zeroed below
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-40,-10,-10,-40,-10,-20],
    ]
    opp_rook_squares = [ # temp zeroed below
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
    ]
    opp_king_squares = [ # temp zeroed below
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-40,-10,-10,-40,-10,-20],
    ]    
    zero_squares = [
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
         [0,  0,  0,  0,  0,  0,  0,  0],
    ]

    # opp squares zeroed for now
    opp_knight_squares = opp_bishop_squares = opp_rook_squares = opp_king_squares = zero_squares

    # Pair encoded pieces to values
    value_map = {
        9 : (pawn_val, own_pawn_squares),
        7 : (knight_val, own_knight_squares),
        3 : (bishop_val, own_bishop_squares),
        13: (rook_val, own_rook_squares),
        11: (queen_val, zero_squares),
        5 : (king_val, opp_king_squares),
        
        8 : (-pawn_val, opp_pawn_squares),
        6 : (-knight_val, opp_knight_squares),
        2 : (-bishop_val, opp_bishop_squares),
        12: (-rook_val, opp_rook_squares),
        10: (-queen_val, zero_squares),
        4 : (-king_val, opp_king_squares),
        
        0 : (0, zero_squares),
    }

    #test boards
    boards = (
        [[12, 6, 2, 10, 4, 2, 6, 12], [8, 8, 8, 8, 8, 8, 8, 8], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [9, 9, 9, 9, 9, 9, 9, 9], [13, 7, 3, 11, 5, 3, 7, 13]],
        [[12, 6, 2, 10, 4, 2, 6, 12], [8, 8, 8, 8, 8, 8, 8, 8], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 9, 0, 0, 0, 0], [9, 9, 9, 0, 9, 9, 9, 9], [13, 7, 3, 11, 5, 3, 7, 13]],
        [[12, 6, 2, 10, 4, 2, 6, 12], [8, 8, 8, 8, 8, 8, 8, 8], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [9, 0, 0, 0, 0, 0, 0, 0], [0, 9, 9, 9, 9, 9, 9, 9], [13, 7, 3, 11, 5, 3, 7, 13]],
    )

    best_board = boards[0]
    best_board_score = -999999
    for board in boards:
        board_score = 0
        for row in range(8):
            for col in range(8):
                board_score += value_map[board[row][col]][0]
                board_score += value_map[board[row][col]][1][row][col]
        if board_score > best_board_score:
            best_board_score = board_score
            best_board = board

    return best_board


def get_boards(game_id):
    '''Retrieves potential board states'''
    response = requests.get('{}/v1.0/games/{}/states'.format(API_URL, game_id))
    data = response.json()
    boards = data['boards']
    while data['cursor']:
        response = requests.get(url='{}/v1.0/games/{}/states'.format(API_URL, game_id), data={'cursor': data['cursor']})
        data = response.json()
        for board in data['boards']:
            boards.append(board)

    return boards

def put_best_board(best_board, game_id):
    data = {'best_board': best_board}
    response = requests.put(url='{}/v1.0/games/{}/states'.format(API_URL, game_id), data=data)
    data = response.json()
    
    return data['end']

def init_game():
    '''Initialize a new game'''
    response = requests.post('{}/v1.0/games'.format(API_URL))
    data = response.json()
    game_id = data['id']

    return game_id

def play_game():
    '''Play a game'''
    game_id = init_game()
    
    game_over = False
    while not game_over:
        boards = get_boards(game_id)
        best_board = evaluate_boards(boards)
        game_over = put_best_board(best_board, game_id)
