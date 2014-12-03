__author__ = 'Jeff'

from collections import defaultdict
import pickle
import random

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
            prediction += self.weights['1'].get(features['1'], 0)
        return prediction


    def update(self, label, features, positive_weight):
        '''Update the feature weights.'''
        def helper(n):
            if features.get(n, 0):
                feature = features[n]
                self._totals[n][feature] = self._totals[n].get(feature, 0) + ((self.i - self._tstamps[n].get(feature, 0)) * self.weights[n].get(feature, 0))
                self._tstamps[n][feature] = self.i
                if label > 0:
                    self.weights[n][feature] = self.weights[n].get(feature, 0) + positive_weight
                else:
                    self.weights[n][feature] = self.weights[n].get(feature, 0) + label
        helper('0')
        helper('-1')
        helper('1')
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
        helper('1')
        return None

    def save(self, path):
        '''Save the pickled model weights.'''
        return pickle.dump(dict(self.averaged_weights), open(path, 'w'))

    def load(self, path):
        '''Load the pickled model weights.'''
        self.weights = pickle.load(open(path))
        return None

def train(examples_path, save_path, positive_weight):
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
            ret['0'] = '%s,%s' % (cluster1, cluster2)
        elif len(clusters) == 3:
            (cluster1, pos1), (cluster2, pos2), (cluster3, pos3) = clusters
            if int(pos1) == -1:
                ret['0'] = '%s,%s' % (cluster2, cluster3)
                ret['-1'] = '%s,%s,%s' % (cluster1, cluster2, cluster3)
            else:
            #elif int(pos1) == 0:
                ret['0'] = '%s,%s' % (cluster1, cluster2)
                ret['1'] = '%s,%s,%s' % (cluster1, cluster2, cluster3)

        if len(clusters) == 4:
            (cluster1, pos1), (cluster2, pos2), (cluster3, pos3), (cluster4, pos4) = clusters
            ret['0'] = '%s,%s' % (cluster2, cluster3)
            ret['-1'] = '%s,%s,%s' % (cluster1, cluster2, cluster3)
            ret['1'] = '%s,%s,%s' % (cluster2, cluster3, cluster4)

        if label == 0:
            label = -1
        return ret, label

    examples = open(examples_path)
    model = AveragedPerceptron()
    for example in examples:
        features, label = parse(example)
        prediction = model.predict(features)
        if prediction * label <= 0:
            model.update(label, features, positive_weight)
    model.average_weights()
    model.save(save_path)
    return model

def test_helper(weights, parts, brown_cluster):
    def instance_predict(feature_set):
        prediction = 0.0
        prediction += weights['0'].get(feature_set['0'], 0.0)
        print 'weight0 ' + str(weights['0'].get(feature_set['0'], 0.0))
        if feature_set.get('-1', 0):
            prediction += weights['-1'].get(feature_set['-1'], 0.0)
            print 'weight-1 ' + str(weights['-1'].get(feature_set['-1'], 0.0))
        if feature_set.get('1', 0):
            prediction += weights['1'].get(feature_set['1'], 0.0)
            print 'weight1 ' + str(weights['1'].get(feature_set['1'], 0.0))

        return prediction


    clustered_parts = [brown_cluster.get(part, 'missing') for part in parts]
    clustered_parts.insert(0, 'start')
    clustered_parts.append('end')
    instances = []

    #stops right before iterating over end
    for i in range(0, (len(clustered_parts)-1)):
        cluster_set = dict()
        if clustered_parts[i] != 'start':
            cluster_set['-1'] = clustered_parts[i-1]
        cluster_set['0'] = clustered_parts[i]
        cluster_set['1'] = clustered_parts[i+1]
        if clustered_parts[i+1] != 'end':
            cluster_set['2'] = clustered_parts[i+2]
        print 'cluster set ' + str(cluster_set)

        feature_set = dict()
        feature_set['0'] = ('%s,%s' % (cluster_set['0'], cluster_set['1']))
        if cluster_set.get('-1', 0):
            feature_set['-1'] = ('%s,%s,%s' % (cluster_set['-1'], cluster_set['0'], cluster_set['1']))
        if cluster_set.get('2', 0):
            feature_set['1'] = ('%s,%s,%s' % (cluster_set['0'], cluster_set['1'], cluster_set['2']))
        print 'feature set ' + str(feature_set)
        instances.append(feature_set)

    return [instance_predict(instance) for instance in instances]

def test(test_inst_path, weights_path, clusters_path):
    sentences = open(test_inst_path)
    weights = pickle.load(open(weights_path))
    clusters = pickle.load(open(clusters_path))
    correct = 0
    total = 0
    for sentence in sentences:
        parts = sentence.strip('\n').split()
        #randint is stupid since it's inclusive on both ends
        rand_index = random.randint(0, (len(parts) - 1))
        parts.pop(rand_index)
        predictions = test_helper(weights, parts, clusters)
        max([(i, element) for (i, element) in enumerate(predictions)], key=lambda (i, element): element)

