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

def word_check(word,correct_words):
    
    if len(correct_words) == 0:
        return 0

    for correct_word in correct_words: 
        if correct_word not in vocabulary:
            return 0
    #if len(correct_word.split()) != 1 or correct_word not in vocabulary:   #If the correct word has spaces or not in dictionary, ignore!
    #    return 0
    final_results = candidates(word,no_of_results = 20)
    final_results = refine_results(word,final_results)
    final_results = final_results[0:min(5,len(final_results))]

    if len(final_results) == 0:
        print word,correct_words," No candidates returned"
        return -1
    final_words = [word for (word,score) in final_results]
    if any(word in final_words for word in correct_words):
    #if final_results[0][0] in correct_words:
        return 1
    else:
        print word,correct_words,final_results[0][0]
        return -1

def word_check_accuracy(input_file):
    f = open(input_file)
    lines = f.readlines()
    f.close()
    correct = 0
    wrong = 0
    for i in xrange(len(lines)):
        
        if i % 100 == 0 and (correct+wrong)!=0:
            print i
            print "Accuracy : ", (correct+0.)/(correct+wrong)
            print "Correct : ",correct
            print "Wrong : ",wrong
            
        line = lines[i]
        [wrong_word,correct_words] = line.strip().split("\t")
        wrong_word = convert_to_alpha(wrong_word)
        correct_words = correct_words.split(",")
        for i in xrange(len(correct_words)):
            correct_words[i] = convert_to_alpha(correct_words[i].strip())
        #print wrong_word,correct_words
        r = word_check(wrong_word, correct_words)
        if r == 1:
            correct += 1
        elif r == -1:
            wrong += 1

    print "FINAL RESULTS:"
    print "Accuracy : ", (correct+0.)/(correct+wrong)
    print "Correct : ",correct
    print "Wrong : ",wrong
