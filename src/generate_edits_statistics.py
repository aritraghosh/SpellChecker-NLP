 #To generate letter level statistics of errors i.e substitutions,deletions,insertions and transpositions 
from candidate_gen import *

f = open("spell-errors.txt","r")
lines = f.readlines()
edits = {}
for line in lines:
    [correct_word,typos] = line.split(":")
    typos = [convert_to_alpha(t.strip()) for t in typos.split(",")]
    correct_word = convert_to_alpha(correct_word)
    for t in typos:
		if t!= correct_word:
			#print t,correct_word
			all_paths = get_all_paths(t,correct_word,operation_matrix(t,correct_word),len(t),len(correct_word))	
			for path in all_paths:
				ops = path.split("+")
				for op in ops:
					edits[op] = edits.get(op,0) + 1
f.close()

f = open("new_edits","w")
for key in edits.keys():
	f.write(key+"\t"+str(edits[key])+"\n")

f.close()
