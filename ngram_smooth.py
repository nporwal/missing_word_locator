import sys
import shelve
import cPickle


# Total number of lines in the file. Might be off by one or two but who cares.
NUM_LINES = 30301027
# number of lines to train on
TRAIN_LINES = 20000000
# After this amount of lines, we forget all the ngrams that we have only seen once.
FORGET_LINES = 1000000

# The n in n-gram
n = int(sys.argv[1])

# an n-gram we don't have in save_dict is put into one_dict. When we see 
# an n-gram in one_dict again, it is moved to save_dict, and kept there
# forever more. One_dict is cleared every FORGET_LINES lines.
one_dict = {}
save_dict = {}

total_forgotten = 0

train = open('train_v2.txt')
print 'Reading lines...'
line_num = 1;
try:
    for l in train:
        if line_num > TRAIN_LINES: break
    
        # For our algorithm to take into account how close words are to
        # the beginning and the end of the sentence, we must prepend and
        # append placeholder words.
        prepend = ['_before_' + str(n-i) for i in range(n)]
        append = ['_after_' + str(i+1) for i in range(n)]
        word_list = prepend + l.lower().split() + append
        line_num += 1
        if line_num%100000 == 0:
            print 'reading line ' + str(line_num)
        # Here is where we 'forget' ngrams that we have only seen once in the last
        # FORGET_LINES lines. We do this to free up memory.
        if line_num%2000000 == 0:
            print 'Freeing memory...'
            f = len(one_dict)
            print '    Number of one-shot ldb\'s being forgotten: ' + str(f)
            one_dict.clear()
            total_forgotten += f
            print '    Forgetting finished. Continueing...'
        for i in range(len(word_list)-n):
            nwords = [word_list[x] for x in range(i,i+n)]
            # The key is just the ngram, each word separated by the string ' , '.
            key = ' , '.join(nwords)
            try:
                # increment ngram count by one
                save_dict[key] += 1
            # this means the ngram isn't in the permament dictionary.
            except KeyError:
                try:
                    # Check to see if it's in the one-shot dictionary:
                    # if so, move into the save_dict, now count is 2
                    save_dict[key] = one_dict.pop(key) + 1
                except KeyError:
                    # if not, put in one-shot dict.
                    one_dict[key] = 1
    print 'Done counting!'
except KeyboardInterrupt:
    pass

# forget the one-shot dict one last time...
one_dict.clear()
save_dict['_forgotten_'] = total_forgotten
print 'Pickly pickling into a pickle...'
picklefile = open("{}gram_pickle.d".format(str(n)), "w")
cPickle.dump(save_dict,picklefile)
print ('Done!')
