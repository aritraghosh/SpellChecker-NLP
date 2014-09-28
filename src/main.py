import os
import sys
import bktree
import re
import pickle
import nltk
from candidate_gen import *
from ranking import *
from utils import * 
from phrase import *
from damlevdist import damerau_levenshtein_distance
from Metaphone.metaphone import doublemetaphone as d

dict_file='dictionary'

dict_tree = pickle.load(open(PATH+"bktree_obj","r"))

wordlist = bktree.dict_words(dict_file)
vocabulary = []
for word in wordlist:
    vocabulary.append(word)

r = Ranking()
n = ngram_method()
m = misspelled_words_method()
metaph = metaphone_method()

def refine_results(word, initial_results):
    results = []
    word_metaphone = d(word)
    for result in initial_results:
        score = 0
        result_metaphone = d(result[0])
        if any(mm in word_metaphone for mm in result_metaphone if mm != ""):
            score += 1
        if result[0][0] == word[0]:
            score += 1
        results.append((result[0],score))
    
    #print "before sorting ", results

    sorted_scores = sorted(results,key=lambda x: x[1], reverse = True)
    
    #print "after sorting ", sorted_scores 
    final_results = []
    for i in xrange(len(sorted_scores)):
        mul = (i+1)*(results.index(sorted_scores[i])+1)
        final_results.append((sorted_scores[i][0],mul))

    final_results = sorted(final_results,key=lambda x: x[1])

    #print "after second sorting ",final_results
    
    return final_results


def candidates(word,options=[1,2,3,4],dist = 2, no_of_results = 10):
    """
        word: word for which possible candidates are to be generated
        dist : returns words within edit distance = dist
        options: send a list of 1,2,3,4 for using the methods
            1 : bktree_set
            2 : ngram_set
            3 : misspelled_set
            4 : metaphone_set
    """
    if word in vocabulary:
        #print "word already in vocabulary"
        return [(word,1)]
    
    bktree_set = set()
    metaphone_set = set()
    misspelled_set = set()
    ngram_set = set()

    if 1 in options:
        for (b_dist,b_word) in dict_tree.query(word,dist):
            bktree_set.add(b_word)

    if 2 in options:
        if len(word) > 5:
            ngram_set = n.candidates_by_threshold(word,0.5)
    
    if 3 in options:
        misspelled_set = m.candidates(word)

    if 4 in options:
        metaphone_set = metaph.candidates(word)


    final_results = bktree_set | ngram_set | misspelled_set | metaphone_set
    final_results = list(final_results)

    scores = []
    for result in final_results:
        score = r.posterior_using_all_paths(result,word)
        scores.append((result,score))

    sorted_scores = sorted(scores,key=lambda x: x[1], reverse = True)

    return sorted_scores[0:min(no_of_results,len(final_results))]

def context_method(window_size=3, no_of_results=5):
    sentence = (str(raw_input("Enter the sentence to be corrected: \n")))
    sentence = nltk.word_tokenize(sentence)
    #Pre-processing of the string
    
    sentence = [convert_to_alphanumeric(word) for word in sentence if convert_to_alphanumeric(word) != ""]
    wrong_word_indices = []
    wrong_word = ""
    #print sentence
    candidate_list = []
    for i in xrange(len(sentence)):
        if sentence[i] not in vocabulary:
            c = candidates(sentence[i],no_of_results = 10)
            c = [word for (word,score) in c]
            candidate_list.append(c)
            wrong_word_indices.append(i)

    if len(candidate_list) == 0:
        print "No mistakes found in the input"
        return

    #For each wrongly spelt word in the input, suggest top <no_of_results> words
    for wrong_word_index in wrong_word_indices:
        wrong_word = sentence[wrong_word_index]
        left_set = []
        right_set = []
        i = wrong_word_index-1
        #Constructing the context words set for the wrongly spelt word
        while len(left_set) < window_size and i >= 0:
            if sentence[i] not in stopwords and sentence[i] in vocabulary:
            #if sentence[i] in vocabulary:
                left_set.append(sentence[i])
            i -= 1
        i = wrong_word_index+1    
        while len(right_set) < window_size and i <= len(sentence)-1:
            if sentence[i] not in stopwords and sentence[i] in vocabulary:
            #if sentence[i] in vocabulary:
                right_set.append(sentence[i])
            i += 1
        left_set.reverse()
        
        sentence_to_be_sent = left_set+[sentence[wrong_word_index]]+right_set
        #print sentence_to_be_sent
        
        scores = []
        for candidate in candidate_list[wrong_word_indices.index(wrong_word_index)]:
            if candidate not in stopwords:
                sentence_to_be_sent[len(left_set)] = candidate
                #print sentence_to_be_sent,wrong_word,candidate
                prob = prob_of_sentence(sentence_to_be_sent,len(left_set))
                prob = prob*pow(0.5,damerau_levenshtein_distance(wrong_word, candidate)-1)
                scores.append((candidate,prob))
    
        sorted_scores = sorted(scores,key=lambda x: x[1], reverse = True)
        final_results = refine_results(wrong_word,sorted_scores)

        print "Suggestions for ",wrong_word
        for i in range(0,min(5,len(final_results))):
            print final_results[i][0]#, sorted_scores[i][1]



#Only for word spell check
while True:
        choice=raw_input("Enter \n 1 for word \n 2 for phrase \n 3 for sentence \n 0 to exit\n")
	if int(choice)==0:
	    break
        elif int(choice) == 1:  #Word Correction
	    word_user = (str(raw_input("Enter the word to check spelling : \n"))).lower()
            word_user = convert_to_alphanumeric(word_user)
                
            final_results = candidates(word_user,no_of_results = 20)

            final_results = refine_results(word_user,final_results)
            print "suggestions for ",word_user
            for i in range(0,min(5,len(final_results))):
                print final_results[i][0]
            
        elif int(choice) == 2:  #for phrase
            context_method(10,20)   #sending large number as context_window to consider the whole phrase as context

        elif int(choice) == 3:  #for sentences
            context_method(3,20) 
