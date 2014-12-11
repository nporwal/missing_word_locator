import os
import cPickle
import shelve
import math

# Insert this word at random places in the sentences, and then calculate
# the probability of that sentence occurring, to look for possible places
# where a word could have been removed.
WILDCARD_WORD = ' * '

# How deep we've calculated the ldb's
depth = 3

# A tuple of shelves, the ith index shelf corresponds to the counts of 
# ldb's of separation = i+1
global ngram_counts
# Contains total count for each word in the vocabulary, as well as 
# the total number of words
global totals 
global vsize
global total_words

def load_totals():
    print "Unpickling totals..."
    global totals
    totals = cPickle.load(open("totals_pickle.d"))
    global vsize
    vsize = len(totals)
    global total_words
    total_words = totals['_total_']

def load_ngram_counts():
    global ngram_counts
    print 'Unpickling dictionary for s = ',s
    ngram_counts=(cPickle.load(open("{}gram_pickle.d".format(str(s)))))
    print "Done!"


# the number of times we counted this particular ldb
def count(ngram):
    try:
        return ngram_counts[ngram]
    except KeyError:
        return 0
# returns the frequency of w (as a fraction over total # words).
def frequency(w):
    return 1.0*totals.get(w,1)/total_words

# probability the last word in this ngram occurs after the first words in
# the ngram
def conditional_probability(ngram):
    # In this case, the probability is just the frequency of w2
    if w1 == WILDCARD_WORD:
        return frequency(w2)
    if w2 == WILDCARD_WORD:
        return 1.0
    return (count(w1,w2,sep) + 1.0)/(totals.get(w1,0) + vsize)

# if l = [w1,w2,w3,w4], i.e. , then this returns 
# the probability of w4 given [w1,w2,w3].
def cond_prob_list(l,weights):
    #print 'Finding conditional probability for ',l
    #print 'weights: ',weights
    w = l.pop(len(l)-1)
    #print 'last word: ',w
    prob_ave = 0
    for wordsep in range(1,len(l)+1):
        #print '  processing wordsep=',wordsep
        #print '  weight of this wordsep=',weights[wordsep]
        if weights[wordsep] > 0:
            w_at_sep = l[len(l)-wordsep]
            #print '  word at this separation from last word: ',w_at_sep
            #print 'w1: ',w_at_sep, ' w2: ',w, ' sep: ',wordsep
            prob_ave += weights[wordsep]*conditional_probability(w_at_sep,w,wordsep)
    return prob_ave

# relies on a heavy approximation (from the article referenced in the progress 
# report).
def lp_sentence(word_list, weights):
    prepend = ['_before_' + str(depth-i) for i in range(depth)]
    append = ['_after_' + str(i+1) for i in range(depth)]
    word_list = prepend + word_list + append
    lp = 0
    for i in range(len(word_list)-depth):
        words = word_list[i:i+depth+1]
        #print 'Words: ',words
        lp += math.log(cond_prob_list(words,weights))
    return lp

# Returns the index where we suspect the missing word should be.
# Argument is a string s, hopefully with a missing word.
def index_mw(s, weights):
    wl = s.lower().split()
    lps = [lp_sentence(wl[:i]+[WILDCARD_WORD]+wl[i:], weights) for i in range(len(wl))]
    if len(lps) >= 1:
        return lps.index(max(lps))
    else: 
        return 0
            
    

