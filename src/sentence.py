import nltk
import pickle

def prob_of_sentence(sent): #Send the sentence split by " "
    """
        Returns the probability of the sentence
    """
    tag_set = nltk.pos_tag(sent)
    tag_set = [(word,nltk.tag.map_tag("en-ptb","universal",tag)) for word,tag in tag_set]
    tag_sequence = [tag for word,tag in tag_set]
    
    p_tags = prob_of_tags(tag_sequence)
    p_words_tags = prob_of_words_tags(tag_set)
    #print tag_sequence
    #print "prob_of_tags ", p_tags
    #print tag_set
    #print "prob_of_words_tags", p_words_tags
    return p_tags*p_words_tags


def prob_of_tags(tag_sequence):
    """
        Returns the probability of the tag sequence to occur by considering
        trigrams
    """
    tag_trigrams = pickle.load(open("tag_trigrams_obj","r"))
    tag_bigrams = pickle.load(open("tag_bigrams_obj","r"))
    
    result = 1
    for i in xrange(0,len(tag_sequence)-2):
        
        numerator = tag_trigrams.get("\t".join(tag_sequence[i:i+3]),1)  #Taking 3 tags starting from the ith position
        denominator = tag_bigrams["\t".join(tag_sequence[i:i+2])]
        #print numerator,denominator
        result *= (numerator+0.)/denominator
    return result

def prob_of_words_tags(words_tags_list):
    """
        word_tags : A list of tuples of (word,tag) where tag is a universal tag
        Returns the product of the probability of the word sequence to occur given 
        the tag sequence

    """
    words_tags_obj = pickle.load(open("words_tags_obj","r")) 
    tag_unigrams = pickle.load(open("tag_unigrams_obj","r"))

    result = 1
    for word,tag in words_tags_list:
        numerator = words_tags_obj.get(word+"\t"+tag,1)
        denominator = tag_unigrams[tag]
        result *= (numerator+0.)/denominator

    return result
