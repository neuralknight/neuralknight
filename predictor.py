import sklearn

def predict_board_state_values(classifier, x_pred):
    '''Predict probability of board states being win/loss/draw

    Inputs:
        classifier: the latest classifier model
        x_pred: an ndarray of board states represented by encoded features

    Outputs:
        predictions: an m x 3 list, where m is the number of board states in
                     board_states, and the 2nd dimension are the probabilities
                     of win/loss/draw respectively for that board state

    '''

    predictions = classifier.predict(x_pred)
    return(predictions)
