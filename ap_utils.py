__author__ = 'Jeff'
import pickle
import random
import time

def create_offsets(read_path, write_path):
    line_offset = []
    offset = 0.0
    for line in open(read_path):
        line_offset.append(offset)
        offset += float(len(line))
    return pickle.dump(line_offset, open(write_path, 'w'))

def create_brown_cluster_dictionary(read_path, write_path):
    new_dict = dict()
    for line in open(read_path):
        cluster, key, count = line.split('\t')
        new_dict[key] = cluster
    return pickle.dump(new_dict, open(write_path, 'w'))


'''Takes the training data and processes it into a form useable for averaged perceptron. Our perceptron
will train and test on each space in a sentence and its respective features. E.g., the 4th space in
a word and the brown clusters of the words surrounding the space. Since the training data is of complete
sentences, naturally we need to modify the training examples to include spaces that should actually
be filled in with a missing word. We do this by randomly "removing" one word from each sentence in
the training data, ie each sentence of n words will be processed into n-1 negative examples and 1 positive
example.
 '''
def preprocess(read_path, write_path, cluster_path):

    def tup2str(tuple):
        part1, part2 = tuple
        return '%s,%s' % (part1, part2)

    brown_cluster = pickle.load(open(cluster_path))
    writeable = open(write_path, 'w+')
    for line in open(read_path):
        parts = line.strip('\n').split()


        #randomly remove one word from the sentence
        #while keeping track of its original index
        rand_index = random.randint(0, (len(parts) - 1))
        parts.pop(rand_index)

        #we want to be careful here,and only
        #extract features that are available
        for i in range(0, len(parts)):
            feature = ('missing', 'missing')
            label = (i == rand_index)
            if i == 0:
                feature = ('start', brown_cluster.get(parts[i], 'missing'))
            else:
                feature = (brown_cluster.get(parts[i-1], 'missing'), brown_cluster.get(parts[i], 'missing'))

            writeable.write('%s %i\n' % (tup2str(feature), int(label)))

        #handle the very last space
        #it should be the length of the current parts
        #because that matches the last index of the original parts
        if parts:
            last_label = (len(parts) == rand_index)
            last_feature = (brown_cluster.get(parts[-1]), 'end')
            writeable.write('%s %i\n' % (tup2str(last_feature), int(last_label)))
        else:
            last_label = True
            last_feature = ('start', 'end')
            writeable.write('%s %i\n' % (tup2str(last_feature), int(last_label)))


def preprocess2(read_path, write_path, cluster_path):

    brown_cluster = pickle.load(open(cluster_path))
    writeable = open(write_path, 'w+')
    for line in open(read_path):
        parts = line.strip('\n').split()
        clustered_parts = [brown_cluster.get(part, 'missing') for part in parts]

        #randomly remove one cluster
        #while keeping track of its original index
        rand_index = random.randint(0, (len(clustered_parts) - 1))
        clustered_parts.pop(rand_index)
        clustered_parts.insert(0, 'start')
        clustered_parts.append('end')



        #stops right before iterating over end
        for i in range(0, (len(clustered_parts)-1)):
            features = []
            label =  i == rand_index
            if clustered_parts[i] != 'start':
                features.append((clustered_parts[i-1], -1))
            features.append((clustered_parts[i], 0))
            features.append((clustered_parts[i+1], 1))
            if clustered_parts[i+1] != 'end':
                features.append((clustered_parts[i+2], 2))

            for feature, pos in features:
                writeable.write('%s,%i ' % (feature, pos))
            writeable.write('%i\n' % int(label))


def split(read_path, training_path, test_path):
    training = open(training_path, 'w')
    test = open(test_path, 'w')
    i = 0
    for line in open(read_path):
        if i < 28000000:
            training.write(line)
        else:
            test.write(line)




