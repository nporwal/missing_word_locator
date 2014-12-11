import os
import cPickle
import shelve
import math

# Insert this word at random places in the sentences, and then calculate
# the probability of that sentence occurring, to look for possible places
# where a word could have been removed.
WILDCARD_WORD = ' * '

# Contains total count for each word in the vocabulary, as well as 
# the total number of words
#totals = shelve.open("totals_shelf.d")
print "Unpickling totals..."
totals = cPickle.load(open("totals_pickle.d"))

print 'Unpickling 3grams'
threegrams = cPickle.load(open("3gram_pickle.d"))
print 'Unpickling 2grams'
twograms = cPickle.load(open("s1_pickle.d"))

print 'Unpickling 1-sep ldbs'
s2ldb = cPickle.load(open('s2_pickle.d'))
print 'done'

vsize = len(totals)
total_words = totals['_total_']

def count2(ngram):
    return twograms.get('{} , {}'.format(ngram[0],ngram[1]),0)
def freq2(ngram):
    return count2(ngram)/total_words
def count3(ngram):
    return threegrams.get('{} , {} , {}'.format(ngram[0],ngram[1],ngram[2]),0)
# returns the frequency of w (as a fraction over total # words).
def frequency(w):
    return 1.0*totals.get(w,1)/total_words

def conditional_probability(ngram):
    # In this case, the probability is just the frequency of w2
    if ngram[0] == WILDCARD_WORD:
        return (count2(ngram[1:]) + 1.0)/(totals.get(ngram[1],0) + vsize)
    if ngram[1] == WILDCARD_WORD:
        return (s2ldb.get('{} , {}'.format(ngram[0],ngram[2]),0) + 1.0)/(totals.get(ngram[0],0) + vsize)
    if ngram[2] == WILDCARD_WORD:
        return 1.0
    return (count3(ngram) + 1.0)/(count2(ngram[:2]) + vsize*vsize)

# relies on a heavy approximation (from the article referenced in the progress 
# report). Right now I set lambda = 1; normalizing shouldn't matter.
def lp_sentence(word_list):
    prepend = ['_before_' + str(2-i) for i in range(2)]
    append = ['_after_' + str(i+1) for i in range(2)]
    word_list = prepend + word_list + append
    lp = 0
    for i in range(len(word_list)):
        if i >= 2:
            lp += math.log(conditional_probability(word_list[i-2:i+1]))
    return lp

# Returns the index where we suspect the missing word should be.
# Argument is a string s, hopefully with a missing word.
def index_mw(s):
    wl = s.lower().split()
    lps = [lp_sentence(wl[:i]+[WILDCARD_WORD]+wl[i:]) for i in range(len(wl))]
    return lps.index(max(lps))
            
    

