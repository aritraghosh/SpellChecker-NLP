import os
import sys
import bktree
import re
from utils import *
from Metaphone.metaphone import doublemetaphone

class metaphone_method(dict):
    def __init__(self,dict_file="dictionary"):
        """
            Generates codes for all words in dictionary  using the Metaphone algorithm
            Stored as a dictionary of word : Metaphone encoding 
        """
        f = open(dict_file)
        words = f.readlines()
        for word in words:
            word = word.strip()
            keys = doublemetaphone(word)
            keys = "+".join(keys)
            if not self.has_key(keys):
                self[keys] = set()
            self[keys].add(word)
 #Returns a setall the words with same Metaphone 
 #encoding as user_word.    
    def candidates(self,user_word):
        """
            Returns a set of all the words with same Metaphone 
            encoding as user_word.
        """  
        keys = doublemetaphone(user_word)
        result = set()
        keys = "+".join(keys)
        if self.has_key(keys):
            result = self[keys]
        return result


#N-gram inverted approach for candidate generation
class ngram_method(dict):
    """
        The dict object here has the inverted index of {trigram:(set,of,words,having,that,trigrams)}
        dict_file : File in which the words of the dictionary are stored
        n : granularity of n-grams
    """

    def __init__(self,n=3,dict_file="dictionary"):
        self.n = n
        f = open(dict_file)
        words = f.readlines()
        for word in words:
            word = word.strip()
            ngrams_list = self.ngrams(word)
            for ngram in ngrams_list:
                if(self.has_key(ngram)):
                    self[ngram].add(word)
                else:
                    self[ngram] = set()
                    self[ngram].add(word)
        
    def ngrams(self,word):
        """
            Returns ngrams of a given word
        """
        if(len(word) < self.n):
            return []
        else:
            n = set()
            for i in range(0,len(word)-(self.n-1)):
                n.add(word[i:i+self.n])
        return n
    def candidates_by_matching(self, user_word,matching_number):
        """
            Returns all words with atleast matching_number n-grams matching with user_word
        """
        user_word_ngrams = self.ngrams(user_word)
        candidate_set = set()
        candidates = {}
        final_result = set()
        for ngram in user_word_ngrams:
            if self.has_key(ngram):
                for word in self[ngram]:
                    if(candidates.has_key(word)):
                        candidates[word] += 1
                    else:
                        candidates[word] = 1
        for c in candidates:
            if(candidates[c] >= matching_number):
                final_result.add(c)
        return final_result
    def candidates_by_threshold(self, user_word,threshold):
        """
            Returns those words with Jaccard similarity of n-grams greater than equal to threshold

        """
        user_word_ngrams = self.ngrams(user_word)
        candidate_set = set()
        candidates = {}
        final_result = set()
        for ngram in user_word_ngrams:
            if self.has_key(ngram):
                for word in self[ngram]:
                    if(candidates.has_key(word)):
                        candidates[word] += 1
                    else:
                        candidates[word] = 1
        for c in candidates:
            if(candidates[c] >= threshold*(len(self.ngrams(user_word) | self.ngrams(c)))):
                final_result.add(c)
        return final_result



class misspelled_words_method(dict):
	#Commonly mispelled words
    def __init__(self,file_name="spell-errors.txt"):
	"""
	   A dictionary which stores for every wrong word(misspelt word) the correct word
	   These are taken from the commonly misspelt words list 
	"""
        f = open(file_name)
        lines = f.readlines()
        for line in lines:
            [correct_word,typos] = line.split(":")
            typos = [convert_to_alpha(t.strip()) for t in typos.split(",")]
            correct_word = convert_to_alpha(correct_word)
            for t in typos:
                if t in self:
                    self[t].add(correct_word)
                else:
                    self[t] = set()
                    self[t].add(correct_word)

    def candidates(self,user_word):
	"""
	    Returns the correct word corresponding to user_word if it exists else returns an empty set 
	"""
        if user_word in self:
            return self[user_word]
        else: 
            return set()




def operation_matrix(a, b):
    """
       Returns a matrix consisting of the possible operations at each position in changing  a to b
	   
    """
    matrix = [[i for i in xrange(len(b)+1)]]
    matrix += [[m] + [0] * len(b) for m in xrange(1, len(a) + 1)]
    
    d= [[[""] for n in xrange(len(b)+1)] for m in xrange(len(a)+1)]
    for i in range(1,len(b)+1):
        if i==1:
            d[0][i] = [" |"+b[i-1]]
        else:
            d[0][i] = [d[0][i-1][0]+"+ |"+b[i-1]]
    
    for j in range(1,len(a)+1):
        if j==1:
            d[j][0] = [a[j-1]+"| "]
        else:
            d[j][0] = [d[j-1][0][0]+"+ |"+a[j-1]]

    ops = ["S","I","D","T"]
    operation = [[[] for n in xrange(len(b)+1)] for m in xrange(len(a)+1)]
    operation[0] = [['S']]+len(b)*[['I']]
    for i in range(1,len(a)+1):
        operation[i][0] = ['D']

    for row in range(1,len(a)+1):
        for col in range(1,len(b)+1):
            cost = 0 if a[row-1] == b[col-1] else 1
            possible_ops = [
	    	matrix[row-1][col-1] + cost, # Substitution
	    	matrix[row][col-1] + 1,  # Insertion
	    	matrix[row-1][col] + 1]  # Deletion

            if row>1 and col>1 and a[row-1]==b[col-2] and a[row-2] == b[col-1]: #Check possibility of Transposition
                possible_ops.append(matrix[row-2][col-2]+1)

	    matrix[row][col] = min(possible_ops)
            #Find all possible operations
            operation[row][col]+= [ops[i] for i,x in enumerate(possible_ops) if x == matrix[row][col]]
    return operation


def get_edits(a,b):
    """
        The edits made in converting a to b.This returns only one of the many possible ways
    """
    matrix = operation_matrix(a,b)
    operations = []
    col = len(b)
    row = len(a)
    while row != 0 or col != 0:
        if(matrix[row][col][0] == "S"):  #substitution
            if(a[row-1] != b[col-1]):    #if the corresponding letters are not equal
                operations.append(a[row-1]+"|"+b[col-1])
            row -= 1
            col -= 1
        elif matrix[row][col][0] == "D": #Deletion
            if a[row-2] == b[col-1] and row > 1 and col>0:
                operations.append(a[row-2]+a[row-1]+"|"+b[col-1])
            else:
                operations.append(a[row-1]+"| ")
            row -= 1
        elif matrix[row][col][0] == "I": #Insertion
            if b[col-2] == a[row-1] and col > 1 and row>0:
                operations.append(a[row-1]+"|"+b[col-2]+b[col-1])
            else:
                operations.append(" |"+b[col-1])
            col -= 1
        else:   #Transposition
            operations.append(a[row-2]+a[row-1]+"|"+b[col-2]+b[col-1])
            row -= 2
            col -= 2
    return "+".join(operations)

def get_all_paths(a,b,operation_matrix,row,col):
    """
	Returns all possible paths in converting a to b
    """
    if row  ==  0 and col == 0:
        return [""]
    else:
        paths = []
        for op in operation_matrix[row][col]:
            new_op = ""
            if  op == 'S':
                paths_till_now = get_all_paths(a,b,operation_matrix,row-1,col-1)
                if a[row-1] != b[col-1] :
                    new_op = a[row-1] + "|" + b[col-1]

            if  op == 'D':
                paths_till_now = get_all_paths(a,b,operation_matrix,row-1,col)
                if a[row-2] == b[col-1] and row > 1 and col > 0:
                    new_op = a[row-2] + a[row-1] + "|" + b[col-1]
                else:
                    new_op = a[row-1] + "| "

            if op == 'I':
                paths_till_now = get_all_paths(a,b,operation_matrix,row,col-1)
                if b[col-2] == a[row-1] and col > 1 and row>0:
                    new_op = a[row-1]+"|"+b[col-2]+b[col-1] 
                else:
                    new_op = " |"+b[col-1]

            if op == 'T':
                paths_till_now = get_all_paths(a,b,operation_matrix,row-2,col-2)
                new_op = a[row-2]+a[row-1]+"|"+b[col-2]+b[col-1]

            for i in range(0,len(paths_till_now)):
                if new_op!="":
                    if paths_till_now[i]!="":
                        paths_till_now[i] = new_op + "+" + paths_till_now[i]
                    else:
                        paths_till_now[i] = new_op

            paths += paths_till_now
        
        return paths
