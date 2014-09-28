import nltk
from nltk.corpus import brown
from utils import convert_to_alphanumeric

sents = brown.sents()


def words_vicinity_count(sents, k, output_file):
    """
        sents : list of sentences in the corpus
        k : The windows length for checking if a word occurs in the vicinity of another word. (Check in left k words and right k words)
        output_file : name of the file in which output should be written 
    """

    f = open(output_file,"w")
    result = {}
    for sent in sents:
        sent = [convert_to_alphanumeric(word) for word in sent if convert_to_alphanumeric(word)!=""]    #To remove everything except alphabets and numbers. 
        for i in xrange(len(sent)):
            bounds = range(max(0,i-k),min(i+k+1,len(sent)))
            bounds.remove(i)
            for j in bounds: 
                result[sent[i]+"\t"+sent[j]] = result.get(sent[i]+"\t"+sent[j],0) + 1  
    
    for key in result.keys():
        f.write(key+"\t"+str(result[key])+"\n")
    
    f.close()
    return result
