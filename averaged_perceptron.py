
from collections import defaultdict
import pickle
import random

class AveragedPerceptron(object):

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

    def update(self, label, old_weight, feature, positive_weight):
        '''Update the feature weights.'''
        self._totals[feature] = self._totals.get(feature, 0) + ((self.i - self._tstamps.get(feature, 0)) * old_weight)
        self._tstamps[feature] = self.i
        if label > 0:
            self.weights[feature] = old_weight + positive_weight
        else:
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
        ret = None
        if len(clusters) == 2:
            (cluster1, pos1), (cluster2, pos2) = clusters
            ret = '%s,%s' % (cluster1, cluster2)
        elif len(clusters) == 3:
            (cluster1, pos1), (cluster2, pos2), (cluster3, pos3) = clusters
            if int(pos1) == -1:
                ret = '%s,%s' % (cluster2, cluster3)
            else:
            #elif int(pos1) == 0:
                ret = '%s,%s' % (cluster1, cluster2)
        if len(clusters) == 4:
            (cluster1, pos1), (cluster2, pos2), (cluster3, pos3), (cluster4, pos4) = clusters
            ret = '%s,%s' % (cluster2, cluster3)
        return ret


    examples = open(examples_path)
    model = AveragedPerceptron()
    for example in examples:
        feature, label = parse(example)
        prediction = model.predict(feature)
        if prediction * label <= 0:
            model.update(label, prediction, feature, positive_weight)
    model.average_weights()
    model.save(save_path)
    return model

def test_helper(weights, parts, brown_cluster):
    def instance_predict(feature):
        return weights.get(feature, 0.0)


    clustered_parts = [brown_cluster.get(part, 'missing') for part in parts]
    clustered_parts.insert(0, 'start')
    clustered_parts.append('end')
    instances = []

    #stops right before iterating over end
    for i in range(0, (len(clustered_parts)-1)):
        cluster_set = dict()
        cluster_set['0'] = clustered_parts[i]
        cluster_set['1'] = clustered_parts[i+1]
        #feature = ('(\'%s\',%s\')' % (cluster_set['0'], cluster_set['1']))
        feature = ('%s,%s' % (cluster_set['0'], cluster_set['1']))
        instances.append(feature)
    return [instance_predict(instance) for instance in instances]

def test(test_inst_path, weights_path, clusters_path, results_path):
    sentences = open(test_inst_path)
    results = open(results_path, 'w')
    weights = pickle.load(open(weights_path))
    clusters = pickle.load(open(clusters_path))
    correct = 0
    total = 0
    for sentence in sentences:
        parts = sentence.strip('\n').split()
        rand_index = -1
        #if total % 2 == 0:
            #randint is stupid since it's inclusive on both ends
        rand_index = random.randint(0, (len(parts) - 1))
        parts.pop(rand_index)

        predictions = test_helper(weights, parts, clusters)
        i, element = max([(i, element) for (i, element) in enumerate(predictions)], key=lambda (i, element): element)
        if element > 0:
            if i == rand_index:
                correct += 1
        else:
            if rand_index == -1:
                correct += 1


        prediction_str = ','.join([str(prediction) for prediction in predictions])
        best_guess_str = '%i:%i' % (i, element)
        rand_index_str = str(rand_index)

        results.write('%s %s %s\n' % (prediction_str, best_guess_str, rand_index_str))

        total += 1

    return ('Correct:%i Total:%i' % (correct, total))