__author__ = 'Jeff'


'''Takes the training data and processes it into a form useable for averaged perceptron. Our perceptron
will train and test on each space in a sentence and its respective features. E.g., the 4th space in
a word and the brown clusters of the words surrounding the space. Since the training data is of complete
sentences, naturally we need to modify the training examples to include spaces that should actually
be filled in with a missing word. We do this by randomly "removing" one word from each sentence in
the training data, ie each sentence will be processed into n-1 negative examples and 1 positive example.
We do this as opposed to having a '''
def preprocess(data):
    pass
