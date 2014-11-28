import pickle
import sys
import pymongo

# This right now ONLY counts word totals, and saves them to a database.
# Call with arguments 1 1.

# I think there's around 30 million lines.
# I'm going to try running this in line sections
# of 4 million, so it's divided into 10 parts.

''' This program is used to pickle a dictionary of the frequencies
of long-distance bigrams in the training set. It takes two arguments:
the separation of the bigrams and the number of lines to train on and
save in one step. Counting and pickling in more than one step 
speeds up the process.  '''


# The separation between the two words in the bigram. The number of 
# other words between the end words in a bigram of separation s is s-1.
s = int(sys.argv[1])

# The number of lines to process in each step (in each pickled dictionary)
step_size = int(sys.argv[2])

# At some point we need to count the total occurrences of all words.
# We only do this if s==1 so as to not waste time repeating it for all
# separations.
if s==1:
    # used to count the total occurrences of all words
    # '_total_' is a special entry that counts all words.
    totals = {'_total_':0} 
d = {} # This counts the bigrams

print 'Opening file...'
train = open('train_v2.txt')
print 'Successfully opened file'
print 'Reading lines...'
line_num = 0;
try:
    for l in train:
        # For our algorithm to take into account how close words are to
        # the beginning and the end of the sentence, we must prepend and
        # append placeholder words.
        prepend = ['_before_' + str(s-i) for i in range(s)]
        append = ['_after_' + str(i) for i in range(s)]
        word_list = prepend + l.lower().split() + append
        if s==1: 
            totals['_total_'] += len(l.split()) #update total count of all words
        line_num += 1
        if line_num%100000 == 0:
            print 'reading line ' + str(line_num)
        ##if line_num % step_size == 0:
        ##    print 'Saving progress as '
        ##    filename = 's' + str(s) + '_lines' + str(((line_num-1)/step_size)*step_size+1) + '_' + str(line_num)
        ##    pickle.dump(d,open(filename, "wb"))
        ##    d.clear()
        ##    print 'Done!'
        for i in range(len(word_list)-s):
            first_word = word_list[i]
            if s==1: # Increment total count of this word.
                try: totals[first_word] += 1
                except KeyError: totals[first_word] = 1
            ##if not first_word in d: # Initialize if necessary
            ##    d[first_word] = {}
            ### Get the word at the correct separation from this word (the bigram)
            ##second_word = word_list[i + s]
            ##try:
            ##    # increment count of][second_word] += 1 #this distance-pair happening
            ##    d[first_word][second_word] += 1
            ##except KeyError:
            ##    d[first_word][second_word] = 1
except KeyboardInterrupt:
    pass

client = pymongo.MongoClient()
db = client.main_db
totals_collection = db.totals

print 'Total number of words:'
print len(totals.keys())
i = 0
for w in totals.keys():
    if (i % 5000 == 0):
        print 'Word number: ' + str(i)
    i += 1;
    totals_collection.insert({'word':w, 'count':totals[w]})







##print 'Final save of bigram count...'
##pickle.dump(d,open('s' + str(s) + '_lines' + str(step_size*(line_num/step_size)) + '_' + str(line_num) + '.d','wb'))
##print 'Done!'
##if s==1:
##    print 'Saving total counts...'
##    pickle.dump(totals,open('totals.d','wb'))
##    print 'Done!'


