import nltk 
from nltk.corpus import brown
from utils import convert_to_alphanumeric
import pickle

#Edit this for using new corpus
#Send the arguments as follows
#tagged_sents = brown.tagged_sents(tagset = "universal")

invalid_tags = [".","X"]

def ngrams_of_tags(tagged_sents,n,output_file):
    """
        Stores the statistics of n-grams of tags
    """
    f = open(output_file,"w")
    f_obj = open(output_file+"_obj","w")
    result = {}
    for sent in tagged_sents:
        key = ""
        for i in xrange(len(sent)-n+1):
            tag_list = [tag for word,tag in sent[i:i+n]]

            if any(tag in tag_list for tag in invalid_tags):
                key = ""
                continue
            else:
                key = "\t".join([tag for word,tag in sent[i:i+n]])
                result[key] = result.get(key,0)+1

    pickle.dump(result,f_obj)
    for key in result.keys():
        f.write(key+"\t"+str(result[key])+"\n")
    f.close()
    f_obj.close()
    return result

def words_tags(tagged_words,output_file):
    """
        Stores the statistics of a word occuring with a tag
    """
    f = open(output_file,"w")
    f_obj = open(output_file+"_obj","w")
    result = {}
    for word,tag in tagged_words:
        word = convert_to_alphanumeric(word)
        if tag not in invalid_tags and word!="":
            result[word+"\t"+tag] = result.get(word+"\t"+tag,0) + 1

    pickle.dump(result,f_obj)
    for key in result.keys():
        f.write(key+"\t"+str(result[key])+"\n")

    f.close()
    f_obj.close()
    return result
