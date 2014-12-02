
from collections import defaultdict
import pickle
import random

class AveragedPerceptron(object):

    '''An averaged perceptron, as implemented by Matthew Honnibal.
    See more implementation details here:
        http://honnibal.wordpress.com/2013/09/11/a-good-part-of-speechpos-tagger-in-about-200-lines-of-python/
    '''

    def __init__(self):
        # Each feature gets its own weight vector, so weights is a dict-of-dicts
        self.weights = dict()
        self.averaged_weights = dict()
        self._totals = defaultdict(int)
        # The last time the feature was changed, for the averaging.
        self._tstamps = defaultdict(int)
        # Number of instances seen
        self.i = 0

    def predict(self, feature):
        self.i += 1
        return self.weights.get(feature, 0)

    def update(self, label, old_weight, feature):
        '''Update the feature weights.'''


        if label * old_weight > 0:
            return None
        self._totals[feature] = self._totals.get(feature, 0) + ((self.i - self._tstamps.get(feature, 0)) * old_weight)
        self._tstamps[feature] = self.i
        self.weights[feature] = old_weight + label
        return None

    def average_weights(self):
        '''Average weights from all iterations.'''
        for feature, weight in self.weights.items():
            total = self._totals[feature]
            total += (self.i - self._tstamps[feature]) * weight
            averaged = round(total / float(self.i), 3)
            if averaged:
                self.averaged_weights[feature] = averaged
        return None

    def save(self, path):
        '''Save the pickled model weights.'''
        return pickle.dump(dict(self.averaged_weights), open(path, 'w'))

    def load(self, path):
        '''Load the pickled model weights.'''
        self.weights = pickle.load(open(path))
        return None

def train(examples_path):
    '''Return an averaged perceptron model trained on examples in ''examples_path''
     In our case even though we're initially trying to do binary
    prediction (whether, given a space in the line, it should contain a missing word)
    we could possibly try to predict if the space is in the line, and what brownian
    cluster it is if it's in the line
    '''

    #adjust this to handle the format we preprocess the examples in
    def parse(example):
        #due to me fucking up and adding spaces, I have to join the two back together
        feature_1, feature_2, label = example.strip('\n').split(' ')
        feature = '%s%s' % (feature_1.strip('\''), feature_2.strip('\''))
        label = int(label)
        #and having the labels be binary oops -_-
        if label == 0:
            label = -1
        return feature, label


    examples = open(examples_path)
    model = AveragedPerceptron()
    for example in examples:
        feature, label = parse(example)
        prediction = model.predict(feature)
        if prediction * label <= 0:
            model.update(label, prediction, feature)
    model.average_weights()
    model.save('ap_model')
    return model


