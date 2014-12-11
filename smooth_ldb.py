import sys
import shelve
import cPickle

#note: ldb stands for long-distance-bigram
# number of forgotten sep=3: 73241462

# Total number of lines in the file. Might be off by one or two but who cares.
NUM_LINES = 30301027
# number of lines to train on
TRAIN_LINES = 20000000
# After this amount of lines, we forget all the bigrams that we have only seen once.
FORGET_LINES = 2000000

# The separation between the two words in the bigram. The number of 
# other words between the end words in a bigram of separation s is s-1.
s = int(sys.argv[1])

# At some point we need to count the total occurrences of all words.
# We only do this if s==1 so as to not waste time repeating it for all
# separations.
if s==1:
    # used to count the total occurrences of all words
    # '_total_' is a special entry that counts all words.
    totals = {'_total_':0} 

# When we encounter a bigram for the first time, it is put into one_dict.
# Then when we encounter the same bigram again, it is moved into save_dict.
# After a bigram has been moved into save_dict, it is remembered forever.
# All entries in one_dict are forgotten every FORGET_LINES lines.
one_dict = {}
save_dict = {}

# counts the number of bigrams we have forgotten.
total_forgotten = 0

train = open('train_v2.txt')
print 'Reading lines...'
line_num = 1;
for l in train:
    if line_num > TRAIN_LINES: break

    # For our algorithm to take into account how close words are to
    # the beginning and the end of the sentence, we must prepend and
    # append placeholder words.
    prepend = ['_before_' + str(s-i) for i in range(s)]
    append = ['_after_' + str(i+1) for i in range(s)]
    word_list = prepend + l.lower().split() + append
    if s==1: 
        totals['_total_'] += len(l.split()) #update total count of all words
    line_num += 1
    if line_num%100000 == 0:
        print 'reading line ' + str(line_num)
    # Here is where we 'forget' bigrams that we have only seen once in the last
    # FORGET_LINES lines. We do this to free up memory.
    if line_num%2000000 == 0:
        print 'Freeing memory...'
        f = len(one_dict)
        print '    Number of one-shot ldb\'s being forgotten: ' + str(f)
        one_dict.clear()
        total_forgotten += f
        print '    Forgetting finished. Continueing...'
    for i in range(len(word_list)-s):
        first_word = word_list[i]
        if s==1: # Increment total count of this word.
            try: totals[first_word] += 1
            except KeyError: totals[first_word] = 1
        second_word = word_list[i + s]
        key = "{} , {}".format(first_word, second_word)
        try:
            # increment bigram count by one
            save_dict[key] += 1
        # this means the bigram isn't in the permament dictionary.
        except KeyError:
            try:
                # Check to see if it's in the one-shot dictionary:
                # if so, move into the save_dict, now count is 2
                save_dict[key] = one_dict.pop(key) + 1
            except KeyError:
                # if not, put in one-shot dict.
                one_dict[key] = 1

print 'Done counting!'
# forget the one-shot dict one last time...
one_dict.clear()
save_dict['_forgotten_'] = total_forgotten
picklefile = open("s{}_pickle.d".format(str(s)), "w")
cPickle.dump(save_dict,picklefile)

if s==1:
    print 'Saving totals:'
    print 'Total number of words:'
    print len(totals.keys())
    totals_shelf = shelve.open('totals_shelf.d')
    totals_shelf.clear()
    totals_shelf.update(totals)

print ('Done!')
