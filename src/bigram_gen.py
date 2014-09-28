from candidate_gen import *

b = ngram_method(2)
u = ngram_method(1)

f = open("count_big.txt")
#f = open("words_freq_new","r")
lines = f.readlines()
bigrams = {}
unigrams = {}
for line in lines:
    [word,freq] = line.strip().split("\t")
    freq = int(freq)
    BS = b.ngrams(word)
    for B in BS:
        bigrams[B] = bigrams.get(B,0)+freq
    US = u.ngrams(word)
    for U in US:
        unigrams[U] = unigrams.get(U,0)+freq

b_f = open("bigrams.txt","w")
u_f = open("unigrams.txt","w")
for key in bigrams.keys():
    b_f.write(key+"\t"+str(bigrams[key])+"\n")
for key in unigrams.keys():
    u_f.write(key+"\t"+str(unigrams[key])+"\n")

