import builtins

# From the first default stopWord list
# found at https://www.ranks.nl/stopwords
stopWords = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
    'any', 'are', 'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'below'
    'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'couldn\'t', 'did', 'didn\'t', 'do',
    'does', 'doesn\'t', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
    'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s',
    'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s',
    'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it',
    'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my',
    'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t',
    'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than',
    'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s',
    'these', 'they', 'they\'d', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too',
    'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve',
    'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which', 'while',
    'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you',
    'you\'d', 'you\'ll', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
    ]

def tokenize(TextFilePath):
    output = list() # Initialize list
    try:
        file = open(TextFilePath) # Open file in try catch in case files does not exist
        c = file.read(1) # Read individual character
        token = "" 
        while(c != ''):
            c = c.lower() # All tokens are same, so we just convert it to lower
            if(c.isalnum() == True): # If it is alpha-numeric, add char to string
                token = token + c
            else:
                if(token.isalnum() and token not in stopWords): output.append(token) # Add token to output once we hit token's end
                token = ""
            c = file.read(1)
        if(token.isalnum() and token not in stopWords): output.append(token) # Add token to output once we hit token's end

        file.close() # Close file!
    except FileNotFoundError: # Catch exception
        builtins.print("That file does not exist!")
    return output

def computeWordFrequencies(tokenList):
    output = dict()
    for s in tokenList: # Loop through tokenList
        if s not in output: # Don't add it in dictionary if it is already in it
            output[s] = tokenList.count(s) # Update the dictionary with the frequency
    return output

def print(frequencies):
   keysAsList = list(frequencies.keys()) # Turn the keys of the dictionary into a list so we can use it
   frequencies2 = insertionSort(keysAsList) # Sort this list so tis alphabetical
   for s in frequencies2: # Loop through all elements so that it prints the token and frequency
       builtins.print(s + "\t" + str(frequencies[s]))

# Classic Insertion Sort Algorithm
def insertionSort(list):
    initialCount = 0
    while(initialCount < len(list)):
        initialCountClone = initialCount
        while(initialCountClone > 0):
            if(list[initialCountClone-1] > list[initialCountClone]):
                copyElem = list[initialCountClone-1]
                list[initialCountClone-1] = list[initialCountClone]
                list[initialCountClone] = copyElem
            initialCountClone -= 1
        initialCount += 1
    return list

