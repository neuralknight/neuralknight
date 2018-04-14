import sklearn
from sklearn.naive_bayes import GaussianNB

def train_classifier(x_train, y_train):
    '''Trains classifier given a set of features and corresponding labels

    Inputs:
        x_train: board states of a given game, represented as features in
                 ndarray format
        y_train: list of labels associated with x_train's states, represented
                 as an m x 1 ndarray, where m is the number of board states in x
    Outputs:
        classifier: An updated classifier

    '''

    gnb = GaussianNB()
    classifier = gnb.fit(x_train, y_train)

    return(classifier)
