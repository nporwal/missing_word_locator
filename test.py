from random import randrange
import sys
import ldb_prob_sum
from ldb_prob_sum import index_mw,depth,load_totals,load_ldb_counts
import numpy as np
import matplotlib.pyplot as plt
#from ldb_prob import index_mw,depth
print 'Done importing.'



# The number of lines to test on
if len(sys.argv) > 1:
    n = int(sys.argv[1])
else:
    n = 20
print n

# if 0, then no output except accuracy at end. If 1, then outputs all sentences.
if len(sys.argv) > 2:
    verbosity = int(sys.argv[2])
else:
    verbosity = 1

testfile = open("rest_of_train.txt")

def test_on(l,weights):
    wl = l.split()
    removed_index = randrange(len(wl))
    wl.pop(removed_index)
    guessed_index = index_mw(' '.join(wl),weights)
    if verbosity == 1:
        print 'Testing on:'
        print ' '.join(wl)
        print 'Result: ' + str(guessed_index == removed_index)
    return guessed_index == removed_index

def test(weights):
    total = 0
    expected_correct = 0.0
    correct = 0
    line_num = 1
    try:
        for l in testfile:
            if line_num > n: break
            line_num += 1
            if line_num % 1000 == 0: print line_num
            total += 1
            expected_correct += 1.0/(len(l.split()))
            if test_on(l,weights):
                correct += 1
    except KeyboardInterrupt:
        pass
    print 'Weights: ',weights
    acc = 1.0*correct/total
    print "Accuracy: ",acc
    print "Expected Accuracy: " + str(expected_correct/total)
    return acc

load_totals()
load_ldb_counts()
accs = []
for w in np.arange(0.9,1.001,.001):
    weights = [None,1-w,w]
    accs.append(test(weights))

plt.plot(np.arange(0.9,1.001,.001),accs)
plt.ylabel("Accuracy")
plt.xlabel("2-sep Long-Distance-Bigram Weight")
plt.show()


