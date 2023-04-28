import re

def tokenize(TextFilePath):
    try:        
        tokens = []
        with open(TextFilePath, "r") as file: 
            for line in file: \
                matching = re.findall("[a-zA-Z0-9]+", line) 
                tokens += matching 
        return tokens
    except FileNotFoundError:
        print("Error: The file name provided does not seem to exist.") 

def computeWordFrequencies(Token):
    wordFreq = {} 
    if type(Token) is not list:
        raise Exception("Error: The object provided is not a list.")
    for word in Token: 
        lowered = word.lower() 
        if lowered not in wordFreq: 
            wordFreq[word] = 1  
        else:
            wordFreq[word] += 1
    return wordFreq 

def print(Frequencies):
    if type(Frequencies) is not map or type(Frequencies) is not dict:
        raise Exception("Error: The parameter object provided is not a map/dictionary.") 
    organized = dict(sorted(Frequencies.items(), key=lambda x: (-x[1], x[0])))
    for k, v in organized:
        print(f"{k} => {v}")
