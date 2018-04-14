# import adam's module up here
from random import randint

def prep_feature_matrix(board, num_leaves):
    '''Creates a matrix of input features for predictor algorithm
    
    Inputs:
        board: current board state as 2D list from row 1-8, column A-H
        num_leaves: the number of possible board states that should be examined

    Outputs:
        features: A num_leaves x 832 matrix representing possible board states
                  by location and whether a given piece exists at that location

    '''

    possible_states = []
    #while adam's module returns a possible state iter, append it to possible_states. 'board' input is used here
    #appending initial state for now just to have something
    possible_states.append(([[12, 6, 2, 10, 4, 2, 6, 12], [8, 8, 8, 8, 8, 8, 8, 8], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [9, 9, 9, 9, 9, 9, 9, 9], [13, 7, 3, 11, 5, 3, 7, 13]]))

    # Randomly choose num_leaves states from possible_states to examine with predictor
    chosen_states = []
    for i in range(num_leaves):
         chosen_states.append(possible_states[randint(0, len(possible_states) - 1)])

    # Return an encoded form of the chosen states
    return encode_states(chosen_states)


def encode_states(chosen_states):
    '''Encode chosen states into predictor friendly feature matrix'''
    encoding_map = {
        8  : [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # White pawn
        12 : [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # White rook
        6  : [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # White knight
        2  : [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], # White bishop
        10 : [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], # White queen
        4  : [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], # White king
        9  : [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], # Black pawn
        13 : [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], # Black rook
        7  : [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], # Black knight
        3  : [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], # Black bishop
        11 : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], # Black queen
        5  : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], # Black king
        0  : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], # Unoccupied space
    }
   
    encoded_states = []
    for state in chosen_states:
        encoded_state = []
        for row in state:
            for col in row:
                for feature in encoding_map[col]:
                    encoded_state.append(feature)
        encoded_states.append(encoded_state)

    return encoded_states
