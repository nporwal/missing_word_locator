import os
import shelve
import math

# Insert this word at random places in the sentences, and then calculate
# the probability of that sentence occurring, to look for possible places
# where a word could have been removed.
WILDCARD_WORD = ' * '

# How deep we've calculated the ldb's
depth = 2
depths = range(1,depth+1)

# Contains total count for each word in the vocabulary, as well as 
# the total number of words
totals = shelve.open("totals_shelf.d")

# A tuple of shelves, the ith index shelf corresponds to the counts of 
# ldb's of separation = i+1
ldb_count_s = tuple(shelve.open("s{}_shelf.d".format(str(s))) for s in depths)

vsize = len(totals)
total_words = totals['_total_']

# the number of times we counted this particular ldb
def count(w1,w2,sep):
    try:
        return ldb_count_s[sep-1]['{} , {}'.format(w1,w2)]
    except KeyError:
        return 0
# returns the frequency of w (as a fraction over total # words).
def frequency(w):
    return 1.0*totals[w]/total_words

# returns the probability of the word w2 occuring at position i given that 
# w1 occurred at position i-sep.
def conditional_probability(w1,w2,sep):
    # In this case, the probability is just the frequency of w2
    if w1 == WILDCARD_WORD:
        return frequency(w2)
    if w2 == WILDCARD_WORD:
        return 1.0
    return (count(w1,w2,sep) + 1.0)/(totals[w1] + vsize)

def log_prob(w1,w2,sep):
    return math.log(conditional_probability(w1,w2,sep))

# relies on a heavy approximation (from the article referenced in the progress 
# report). Right now I set lambda = 1; normalizing shouldn't matter.
def lp_sentence(word_list):
    prepend = ['_before_' + str(depth-i) for i in range(depth)]
    append = ['_after_' + str(i+1) for i in range(depth)]
    word_list = prepend + word_list + append
    lp = 0
    for i in range(len(word_list)-2):
        for s in depths:
            if i >= depth-s:
                lp += log_prob(word_list[i],word_list[i+s],s)
    return lp

# Returns the index where we suspect the missing word should be.
# Argument is a string s, hopefully with a missing word.
def index_mw(s):
    wl = s.lower().split()
    lps = [lp_sentence(wl[:i]+[WILDCARD_WORD]+wl[i:]) for i in range(len(wl))]
    return lps.index(max(lps))
            
    

