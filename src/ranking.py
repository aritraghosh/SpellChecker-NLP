from operator import mul
from candidate_gen import *


class Ranking(dict):
    def __init__(self,word_freq_file="count_1w.txt",bigrams_freq="bigrams.txt",unigrams_file="unigrams.txt",edits_file="new_edits.txt"):
        """
            A class which stores all the statisitics required for ranking like
            unigram counts, bigram counts,edit counts
        """
        self.word_freq = self.readfile(word_freq_file)
        self.bigrams_freq = self.readfile(bigrams_freq)
        self.unigrams_freq = self.readfile(unigrams_file)
        self.edits = self.readfile(edits_file)
        self.word_count = sum(self.word_freq.values())
        self.bigrams_count = sum(self.bigrams_freq.values())
        self.p_spell_error = 1./20

        #Adding " " manually
        self.unigrams_freq[" "] = sum(self.unigrams_freq.values())/26
        self.unigrams_count = sum(self.unigrams_freq.values())

        
    def readfile(self,file_name):
        f = open(file_name)
        lines = f.readlines()
        result = {}
        for line in lines:
            [word,freq] = line.split("\t")
            freq = freq.strip()
            result[word] = int(freq)
        f.close()
        return result 
    
    def prior(self,word):
        """
            Returns the Prior of word
        """    
        if(self.word_freq.has_key(word)):
            return (self.word_freq[word]+1.)/(self.word_count)
        else:
            return 1./self.word_count
    
    def single_edit_likelihood(self,op):
        """
            Returns the likelihood of a single edit like x|xy 
        """
        [correction,typo] = op.split("|")
        numerator = self.edits.get(typo+"|"+correction,1.0) #Searching for reverse of operation
        if len(correction) == len(typo) == 1 and correction.isalpha() and typo.isalpha(): 
            denominator = self.unigrams_freq[correction] 
        elif len(correction) < len(typo):   #Insertion  "x"|"xy"
            denominator = self.unigrams_freq[correction]
        elif correction == " " and typo.isalpha():  #Insertion " "|"x"
            #numerator = self.edits.get(">"+typo+"|>",1.0)
            denominator = self.unigrams_freq[correction]
        elif len(correction) > len(typo):   #Deletion   "xy"|"x"
            denominator = self.bigrams_freq[correction]
        elif typo == " " and correction.isalpha():  #Deletion "x"|" "
            #numerator = self.edits.get(">|>"+correction,1.0)
            denominator = self.unigrams_freq[correction]
        elif len(correction) == len(typo) == 2:  #Transposition    "xy"|"yx"
            denominator = self.bigrams_freq[correction]
        else:
            print "ERROR IN SINGLE_EDIT_LIKELIHOOD"
        #denominator = sum(self.edits.itervalues())
        #print op,numerator,denominator
        return (numerator+0.)/denominator


    def likelihood(self,ops_list):
        """
            Returns the likelihood of all the edits combined
        """
        total_cost = 0.0
        for op in ops_list:
            if op == "":
                cost = (1-self.p_spell_error)
            else:
                op = op.split("+")
                cost = 1.0
                for o in op:
                    cost *= self.single_edit_likelihood(o)
            total_cost += cost
        return total_cost

    def posterior(self,correction,typo):
        """
            Returns the posterior by multiplying 
            the prior and likelihood
        """
        prior = self.prior(correction)
        likelihood = self.likelihood([get_edits(correction,typo)])
        return prior*likelihood

    def posterior_using_all_paths(self,correction,typo):
        """
            Returns the posterior using all paths i.e of there are more than one
            paths to convert the correction to typo
        """
        prior = self.prior(correction)
        likelihood = self.likelihood(get_all_paths(correction,typo,operation_matrix(correction,typo),len(correction),len(typo)))
        #print correction,typo,prior*likelihood
        return prior*likelihood

    
            
            

