import pickle
import os

# This doesn't work, too slow. The pickles dictionaries
# that I try to load are too large.

# Insert this word at random places in the sentences, and then calculate
# the probability of that sentence occurring, to look for possible places
# where a word could have been removed.
WILDCARD_WORD = ' * '

# list of dictionaries of counts for a separation of 1
s1l = []
# list of dictionaries of counts for a separation of 2
s2l = []
i = 1
for fs in os.listdir(os.getcwd() + '/sep_1'):
    print 'sep 1: loading dict ' + str(i)
    s1l.append(pickle.load(open('sep_1/' + fs)))
    i += 1
i = 1
for fs in os.listdir(os.getcwd() + '/sep_2'):
    print 'sep 2: loading dict ' + str(i)
    s2l.append(pickle.load(open('sep_2/' + fs)))
    i += 1
i = 1

total = pickle.load(open('totals.d'))
vsize = len(total)

# returns the total count of occurrences of the long distance bigram
# w1,w2 with separation sep. If sep = 1, then this is a normal 2-gram.
def count(w1,w2,sep):
    c = 0
    if sep == 1:
        for d in s21:
            try:
                count += d[w1][w2]
            except KeyError:
                pass

def prob_bigram(w1,w2,sep):
    if w1 == WILDCARD_WORD or w2 == WILDCARD_WORD:
        return 1.0
    return (1.0*count(w1,w2,sep) + 1)/(total[w1] + vsize)

# relies on a heavy approximation (from the article referenced in the progress 
# report). Right now I set lambda = 1; normalizing shouldn't matter.
def prob_sentence(s):
    prob = 1.0;
    prepend = ['_before_' + str(i) for i in range(2)]
    append = ['_after_' + str(i) for i in range(2)]
    sl = prepend + s.split() + append
    for i in range(len(sl)-2):
        prob *= prob_bigram(sl[i],sl[i+1],1)
        prob *= prob_bigram(sl[i],sl[i+2],2)
    return prob
        
            
    

