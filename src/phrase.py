from nltk.corpus import stopwords as s
import pickle
from utils import *

stopwords = pickle.load(open("stop_words","r"))
word_freq = pickle.load(open(PATH+"words_freq_obj","r"))
#word_freq = pickle.load(open(PATH+"wiki_words_freq_obj","r"))
vicinity_freq = pickle.load(open(PATH+"words_vicinity_obj","r"))
#vicinity_freq = pickle.load(open(PATH+"wiki_words_vicinity_obj","r"))

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
    """
        Generate an object {word:frequency} where input file format is 
        <freq> \t <word1> \t <word2> \t ... <wordn>
    """
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


def words_freq_1w(input_file,output_file):
    """
        Generate an object {word:frequency} where input file format is 
        <word> \t <freq>
    """
    f = open(input_file,"r")
    result = {}
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.strip().split()
        freq = int(line[1])
        result[line[0]] = result.get(line[0],0)+freq

    pickle.dump(result,open(output_file+"_obj","w"))
    f = open(output_file,"w")
    for key in result.keys():
        f.write(key+"\t"+str(result[key])+"\n")

    f.close()
    return result

def vicinity_likelihood(c,w):
    """
        Returns P(c,w)
    """

    if vicinity_freq.has_key(c+"\t"+w):
        numerator = vicinity_freq[c+"\t"+w]
    elif vicinity_freq.has_key(w+"\t"+c):
        numerator = vicinity_freq[w+"\t"+c]
    else:
        numerator = 1

    if word_freq.has_key(w):
        denominator = word_freq[w]
    else:
        denominator = sum(word_freq.values())/len(word_freq)

    return (numerator+0.)

def prob_of_sentence(sent, replaced_index):
    """
        return P(W) = *(P(c,w))
    """
    context_words_indices = range(0,len(sent))
    context_words_indices.remove(replaced_index)
    product = 1
    #print context_words_indices
    for i in context_words_indices:
        if sent[i] not in stopwords:
            p = vicinity_likelihood(sent[i],sent[replaced_index])
            #print sent[i],sent[replaced_index], p
            if p > 0:
                product *= p
    return product
