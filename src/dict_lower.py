from sets import Set

def dict_lower(file_name):
    """
        Converts all the words to lower
    """
    f = open(file_name)
    output = open("dictionary","w")
    lines = f.readlines()
    output_set = []
    for line in lines:
        output_set.append(line.lower().strip())
    output_set = Set(output_set)
    for word in output_set:
        output.write(word+"\n")	
    output.close()
    f.close()
