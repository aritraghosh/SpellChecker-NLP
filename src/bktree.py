"""
This module implements Burkhard-Keller Trees (bk-tree).  bk-trees
allow fast lookup of words that lie within a specified distance of a
query word.  For example, this might be used by a spell checker to
find near matches to a mispelled word.

The implementation is based on the description in this article:

http://blog.notdot.net/2007/4/Damn-Cool-Algorithms-Part-1-BK-Trees

Licensed under the PSF license: http://www.python.org/psf/license/

- Adam Hupp <adam@hupp.org>

"""
from itertools import imap, ifilter
import collections
import random, operator

class BKTree:
    def __init__(self, distfn, words):
        """
        Create a new BK-tree from the given distance function and
        words.
        
        Arguments:

        distfn: a binary function that returns the distance between
        two words.  Return value is a non-negative integer.  the
        distance function must be a metric space.
        
        words: an iterable.  produces values that can be passed to
        distfn
        
        """
        self.distfn = distfn

        it = iter(words)
        root = it.next()
        self.tree = (root, {})

        for i in it:
            self._add_word(self.tree, i)

    def _add_word(self, parent, word):
        pword, children = parent
        d = self.distfn(word, pword)
        if d in children:
            self._add_word(children[d], word)
        else:
            children[d] = (word, {})

    def query(self, word, n):
        """
        Return all words in the tree that are within a distance of `n'
        from `word`.  

        Arguments:
        
        word: a word to query on

        n: a non-negative integer that specifies the allowed distance
        from the query word.  
        
        Return value is a list of tuples (distance, word), sorted in
        ascending order of distance.
        
        """
        def rec(parent):
            pword, children = parent
            d = self.distfn(word, pword)
            results = []
            if d <= n:
                results.append( (d, pword) )
                
            for i in range(d-n, d+n+1):
                child = children.get(i)
                if child is not None:
                    results.extend(rec(child))
            return results

        # sort by distance
        return sorted(rec(self.tree))
    


def brute_query(word, words, distfn, n):
    """A brute force distance query

    Arguments:

    word: the word to query for

    words: a iterable that produces words to test

    distfn: a binary function that returns the distance between a
    `word' and an item in `words'.

    n: an integer that specifies the distance of a matching word
    
    """
    return [i for i in words
            if distfn(i, word) <= n]

def maxdepth(tree, count=0):
    _, children = t
    if len(children):
        return max(maxdepth(i, c+1) for i in children.values())
    else:
        return c


def levenshtein(s, t):
    m, n = len(s), len(t)
    d = [range(n+1)]
    d += [[i] for i in range(1,m+1)]
    for i in range(0,m):
        for j in range(0,n):
            cost = 1
            if s[i] == t[j]: cost = 0

            d[i+1].append( min(d[i][j+1]+1, # deletion
                               d[i+1][j]+1, #insertion
                               d[i][j]+cost) #substitution
                           )
    return d[m][n]

def damerau_levenshtein_distance(a, b):
    INF = len(a) + len(b)
    matrix = [[INF for n in xrange(len(b) + 2)]]
    matrix += [[INF] + range(len(b) + 1)]
    matrix += [[INF, m] + [0] * len(b) for m in xrange(1, len(a) + 1)]
    last_row = {}
    for row in xrange(1, len(a) + 1):
    	ch_a = a[row-1]
    	last_match_col = 0
    	for col in xrange(1, len(b) + 1):
    		ch_b = b[col-1]
    		last_matching_row = last_row.get(ch_b, 0)
    		cost = 0 if ch_a == ch_b else 1
    		matrix[row+1][col+1] = min(
    			matrix[row][col] + cost, # Substitution
    			matrix[row+1][col] + 1,  # Addition
    			matrix[row][col+1] + 1,  # Deletion
    			# Transposition
    			matrix[last_matching_row][last_match_col]
    				+ (row - last_matching_row - 1) + 1
    				+ (col - last_match_col - 1))
    		if cost == 0:
    			last_match_col = col
    	last_row[ch_a] = row
    return matrix[-1][-1]
    
def dict_words(dictfile="/usr/share/dict/american-english"):
    "Return an iterator that produces words in the given dictionary."
    return ifilter(len,
                   imap(str.strip,
                        open(dictfile)))

def timeof(fn, *args):
    import time
    t = time.time()
    res = fn(*args)
    print "time: ", (time.time() - t)
    return res

        