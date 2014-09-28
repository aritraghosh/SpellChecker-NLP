from nltk.corpus import stopwords as s
import pickle
from ..utils import *

stopwords = s.words("english")
word_freq = pickle.load(open(PATH+"ngrams_info/words_freq_obj","r"))
vicinity_freq = pickle.load(open(PATH+"ngrams_info/words_vicinity_obj","r"))

def words_vicinity_obj(input_file,output_file):
    """
        Assuming each lines is of the format : freq\tword_1\t,...,\tword_n\n
    """
    f = open(input_file,"r")
    result = {}
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.strip().split()
        freq = int(line[0])
        for i in xrange(1,len(line)):
            for j in xrange(i+1,len(line)):

                if result.has_key(line[i]+"\t"+line[j]):
                    result[line[i]+"\t"+line[j]] += freq

                elif result.has_key(line[j]+"\t"+line[i]):
                    result[line[j]+"\t"+line[i]] += freq

                else:
                    result[line[i]+"\t"+line[j]] = freq
    
    pickle.dump(result,open(output_file+"_obj","w"))

    f = open(output_file,"w")
    for key in result.keys():
        f.write(key+"\t"+str(result[key])+"\n")

    f.close()
    return result

def words_freq(input_file,output_file):
    f = open(input_file,"r")
    result = {}
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.strip().split()
        freq = int(line[0])
        for i in xrange(1,len(line)):
            result[line[i]] = result.get(line[i],0)+freq

    pickle.dump(result,open(output_file+"_obj","w"))
    f = open(output_file,"w")
    for key in result.keys():
        f.write(key+"\t"+str(result[key])+"\n")

    f.close()
    return result

def vicinity_likelihood(c,w):

    #TODO : Adjust the smoothing functions
    if vicinity_freq.has_key(c+"\t"+w):
        numerator = vicinity_freq[c+"\t"+w]
    elif vicinity_freq.has_key(w+"\t"+c):
        numerator = vicinity_freq[w+"\t"+c]
    else:
        numerator = 1

    if word_freq.has_key(w):
        denominator = word_freq[w]
    else:
        denominator = 1

    print numerator,denominator
    return (numerator+0.)#/denominator

def prob_of_sentence(sent, replaced_index):
    context_words_indices = range(0,len(sent))
    context_words_indices.remove(replaced_index)
    product = 1
    print context_words_indices
    for i in context_words_indices:
        if sent[i] not in stopwords:
            print sent[i],sent[replaced_index] 
            product *= vicinity_likelihood(sent[i],sent[replaced_index])
    return product
