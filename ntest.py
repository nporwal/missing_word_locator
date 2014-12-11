from random import randrange
import sys
from ngram_probs import index_mw
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

def test_on(l):
    wl = l.split()
    removed_index = randrange(len(wl))
    wl.pop(removed_index)
    guessed_index = index_mw(' '.join(wl))
    if verbosity == 1:
        print 'Testing on:'
        print ' '.join(wl)
        print 'Result: ' + str(guessed_index == removed_index)
    return guessed_index == removed_index

def test():
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
            if test_on(l):
                correct += 1
    except KeyboardInterrupt:
        pass
    acc = 1.0*correct/total
    print "Accuracy: ",acc
    print "Expected Accuracy: " + str(expected_correct/total)
    return acc

acc = test()



