__author__ = 'Jeff'

from collections import defaultdict
import pickle

class AveragedPerceptron(object):

    def __init__(self):
        self.weights = dict([('-1', dict()), ('0', dict()), ('1', dict())])
        self.averaged_weights = dict([('-1', dict()), ('0', dict()), ('1', dict())])
        self._totals = dict([('-1', dict()), ('0', dict()), ('1', dict())])
        # The last time the feature was changed, for the averaging.
        self._tstamps = dict([('-1', dict()), ('0', dict()), ('1', dict())])
        # Number of instances seen
        self.i = 0

    def predict(self, features):
        self.i += 1
        prediction = 0
        if features.get('0', 0):
            prediction += self.weights['0'].get(features['0'], 0)
        if features.get('-1', 0):
            prediction += self.weights['-1'].get(features['-1'], 0)
        if features.get('1', 0):
            prediction += self.weights['1'].get(features['0'], 0)
        return prediction


    def update(self, label, features):
        '''Update the feature weights.'''
        def helper(n):
            if features.get(n, 0):
                feature = features[n]
                self._totals[n][feature] = self._totals[n].get(feature, 0) + ((self.i - self._tstamps[n].get(feature, 0)) * self.weights[n].get(feature, 0))
                self._tstamps[n][feature] = self.i
                self.weights[n][feature] = self.weights[n].get(feature, 0) + label
        helper('0')
        helper('-1')
        helper('0')
        return None

    def average_weights(self):
        '''Average weights from all iterations.'''
        def helper(n):
            for feature, weight in self.weights[n].items():
                total = self._totals[n][feature]
                total += (self.i - self._tstamps[n][feature]) * weight
                averaged = round(total / float(self.i), 3)
                if averaged:
                    self.averaged_weights[n][feature] = averaged
        helper('0')
        helper('-1')
        helper('0')
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
        parts = example.strip('\n').split()
        label = int(parts[-1])
        clusters = [cluster.split(',') for cluster in parts[0:-1]]
        ret = dict()
        if len(clusters) == 2:
            (cluster1, pos1), (cluster2, pos2) = clusters
            ret['0'] = (cluster1, cluster2)
        elif len(clusters) == 3:
            (cluster1, pos1), (cluster2, pos2), (cluster3, pos3) = clusters
            if int(pos1) == -1:
                ret['0'] = (cluster2, cluster3)
                ret['-1'] = (cluster1, cluster2, cluster3)
            else:
            #elif int(pos1) == 0:
                ret['0'] = (cluster1, cluster2)
                ret['1'] = (cluster1, cluster2, cluster3)

        if len(clusters) == 4:
            (cluster1, pos1), (cluster2, pos2), (cluster3, pos3), (cluster4, pos4) = clusters
            ret['0'] = (cluster2, cluster3)
            ret['-1'] = (cluster1, cluster2, cluster3)
            ret['1'] = (cluster2, cluster3, cluster4)

        return ret

    examples = open(examples_path)
    model = AveragedPerceptron()
    for example in examples:
        features, label = parse(example)
        prediction = model.predict(features)
        if prediction * label <= 0:
            model.update(label, features)
    model.average_weights()
    model.save('ap_model')
    return model


#this is wrong fix this
def test_sentence(weights, sentence, clusters):
    def feat_to_string(feature):
        part1, part2 = feature
        return ('(\'%s\',%s\')' % (part1, part2))
    parts = sentence.split(' ')
    sentence_weights = []
    for i in range(0, len(parts)):
            feature = ('missing', 'missing')
            if i == 0:
                feature = ('start', clusters.get(parts[i], 'missing'))
                sentence_weights.append(weights.get(feat_to_string(feature), 0.0))
            else:
                feature = (clusters.get(parts[i-1], 'missing'), clusters.get(parts[i], 'missing'))
                sentence_weights.append(weights.get(feat_to_string(feature), 0.0))
    if parts:
            last_feature = (clusters.get(parts[-1]), 'end')
            sentence_weights.append(weights.get(feat_to_string(last_feature), 0.0))

    print sentence_weights