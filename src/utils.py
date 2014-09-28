import re

PATH = "/home/kiriti/acads/NLP/SpellChecker/"

def convert_to_alpha(word):
    return re.sub('[\W_0-9]+','',word).lower()

def convert_to_alphanumeric(word):
    return re.sub('[\W_]+','',word).lower()

