import pickle
import sys
import pymongo

# Call with the first argument separation, the second argument the percent of the 
# training data to use.

# Total number of lines in the file. Might be off by one or two but who cares.
NUM_LINES = 30301027

''' This program is used to pickle a dictionary of the frequencies
of long-distance bigrams in the training set. It takes two arguments:
the separation of the bigrams and the number of lines to train on and
save in one step. Counting and pickling in more than one step 
speeds up the process.  '''

# The separation between the two words in the bigram. The number of 
# other words between the end words in a bigram of separation s is s-1.
s = int(sys.argv[1])

# The percent of the training data to train on. Must be greater than 0 and
# less than or equal to 100.
percent = float(sys.argv[2])

# Database stuff
# Database!
client = pymongo.MongoClient()
db = client.main_db
# Make the collection for this seperation 
col_name = 'sep' + str(s) + '_collection'
# Initialize collection
collection = db[col_name]

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
print 'Reading lines...'
line_num = 0;
try:
    for l in train:
        if 1.0*line_num/NUM_LINES > percent: break
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
        for i in range(len(word_list)-s):
            first_word = word_list[i]
            if s==1: # Increment total count of this word.
                try: totals[first_word] += 1
                except KeyError: totals[first_word] = 1
            second_word = word_list[i + s]
            try:
                # increment bigram count by one
                d[(first_word,second_word)] += 1
            except KeyError:
                d[(first_word,second_word)] = 1
except KeyboardInterrupt:
    pass

i = 0
print 'Writing to database...'
print 'Entries to save: ' + str(len(d))
#print 'Making bulk operation:'
#bulk = collection.initialize_unordered_bulk_op()
for bigram in d.keys():
    if (i % 10000 == 0):
        print 'Entry number: ' + str(i)
    i += 1;
    collection.insert({'w1':bigram[0],'w2':bigram[1],'c':d[bigram]})
#print 'Calling bulk.execute...'
#bulk.execute()
d.clear() 
print 'Done!'

# The totals dictionary is small enough that it doesn't have to
# be updated in steps.
if s==1:
    print 'Saving totals:'
    # Need to save the total counts into a collection
    totals_collection = db.totals
    
    print 'Total number of words:'
    print len(totals.keys())
    i = 0
    for w in totals.keys():
        if (i % 5000 == 0):
            print 'Word number: ' + str(i)
        i += 1;
        totals_collection.insert({'word':w, 'count':totals[w]})
