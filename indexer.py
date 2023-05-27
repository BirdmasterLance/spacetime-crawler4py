import json
import re
import pathlib
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import difflib
from urllib.parse import urldefrag
from simhash import Simhash
	
import time

# Special class for posting to hold information per website
# Needs some fixing so it can keep track of words PER document
# as well as score PER document
class Posting:
    def __init__(self):
        self.id = 0
        self.wordFrequency = 0
        # If the word in this URL is in header, bold, or strong, 
        # then this posting is a little more important
        self.importantScore = 0 
       
        # Save a list of what positions this word is at
        self.position = '0'
    
    def getWordFrequency(self):
        return self.wordFrequency

    def setWordFrequency(self, frequency):
        self.wordFrequency = frequency
    
    def setId(self, newId):
        self.id = newId
    
    def getId(self):
        return self.id
    
    def getImportantScore(self):
        return self.importantScore
    
    def setImportantScore(self, score):
        self.importantScore = score

    def getPosition(self):
        return self.position

    def setPosition(self, newPosition):
        self.position = newPosition

    def __eq__(self, other):
        return (self.importantScore == other.importantScore) and (self.wordFrequency == other.wordFrequency)

    def __lt__(self, other):
        return (self.importantScore < other.importantScore) or (self.wordFrequency < other.wordFrequency)
    
    def __le__(self, other):
        return (self.importantScore <= other.importantScore) or (self.wordFrequency <= other.wordFrequency)

# Set up the stemmer
ps = PorterStemmer()

indexLimits = [0, 1307, 5367, 7946, 16884, 20318]

json_dir = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV"
index_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\index"
doc_index_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\docIndexFile.txt"

index = dict()
doc_index_dict = dict()

output_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\output.txt"



blank_space = '                                                                   '


blacklist = [
    '[document]',
    'noscript',
    'html',
    'meta',
    'head', 
    'input',
    'script',
    'style',
    'font',
    'option'
]

important_tags = [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'header',
    'b',
    'title',
    'strong',
    'em'
]

urls_visited = set()

# Function to build the index
# Set docID to change the starting ID for the documents
def indexDocuments(docId):
    startId = docId
    numFiles = 0
    path = pathlib.Path(json_dir + str(docId))
    totalStartTime = time.time()

    for filename in path.rglob("*"): # Look through all files and directories from a single path
        numFiles += 1 # Keep track of the number of files
        filename = str(filename) # Get the string version of the file name

        if filename.endswith(".json"): # Check if the file is actually a JSON file
            startTime = time.time()

            # Read in the JSON data from the file
            with open(filename, "r") as f:
                data = json.load(f)

            # Extract the text from the JSON data
            content = data["content"]
            
            # TODO: Implement SimHash

            # Defrag the URL and compare it with future URLs to see if there are the same links down the line
            link = data['url'] 
            link = urldefrag(link)
            if link in urls_visited: continue
            else: urls_visited.add(link)
            
            soup = BeautifulSoup(content, 'html.parser') # Parse the HTML content

            # Tokenize the text and build the inverted index
            for section in soup.find_all(text=True): # Find all the text and their HTML tags in the file
                if section.parent.name not in blacklist: # If the tag is in our blacklisted section, skip it
                    text = section.get_text() # Get the text

                    tokens = re.finditer(r'\b\w+\b', text.lower()) # Changed to find iter so we can save position of match
                    for tokenMatch in tokens: # For every token that matched our regex expression
                        token = ps.stem(tokenMatch.group()) # Stem the word to reduce repeated words
                        
                        if(len(token) == 1): continue # Don't save single letters and numbers
                        
                        if token not in index:
                            index[token] = list() # Initialize a new list of postings
                        
                        # Create posting that holds document information
                        posting = Posting()
                        posting.setId(docId) # Set the posting's document ID
                        posting.setPosition(tokenMatch.start()) # Save the position of the word in the 
                        posting.setImportantScore(section.parent.name) # Save the tag the word is in
                        index[token].append(posting) # Append the posting to hte list

            # Save the document to the index of documents and document IDs
            with open(doc_index_file, 'a') as f:
                f.write(str(docId) + ';' + filename + '\n')
            docId += 1 

            # For fun, print how long it took to complete the file
            endTime = time.time()
            print('Execution time for', filename, ': ', str(endTime-startTime))
    
    # For fun, print how long it took to index the given documents
    print('ran out of files to index through')
    totalEndTime = time.time()
    print('Total execution time:', str(totalEndTime-totalStartTime))



    writeStartTime = time.time() # For fun, start time
    indexLength = len(index) # For fun, get the current length of our index to see saving progress
    tokenCount = 0 # For fun, get the number of tokens that need to be saved to show progress
    
    index_index = dict() # Create an index for our index
    if(not pathlib.Path(index_file + str(startId)).exists()): pathlib.Path.mkdir(index_file + str(startId)) # Create folder if it does not exist

    for token in sorted(index.keys()): # For every token in our index
        # Open both the associated index (where the postings are stored) and index of index (where the position of the posting list is) file
        with open(index_file + str(startId) + '\\index' + token[0].upper() + '.txt', 'a', encoding='utf-8') as f, open(index_file + str(startId) + '\\index' + token[0].upper() + 'Index.txt', 'a', encoding='utf-8') as f2:
            tokenCount += 1 # For fun, get the current token we are on
            print('saving ' + token + ' to file ({0} / {1})'.format(tokenCount, indexLength) + blank_space) # Print the saving progress

            # If the letter/number is NOT in the index of index, initialize it in the dict
            if(token[0].upper() not in index_index):
                index_index[token[0].upper()] = 0

            # For fun, get the number of postings for progress
            numPostings = len(index[token]) 
            progress = 0

            # Initialize the output we will be writing to file
            # NOTE: The output of the posting is as follow:
            # token docID,wordPosition,tag|docID,wordPosition,tag|docID,wordPosition,tag|...
            output = token + ' ' 
            for posting in index[token]:
                output += '{0},{1},{2}|'.format(str(posting.getId()), str(posting.getPosition()), str(posting.getImportantScore()))

                # For fun, output progress
                progress += 1
                print(token + ';' + str(progress) + '/' + str(numPostings) + blank_space, end='\r')
            
            output = output[:-1] + '\n'
            f.write(output)

            f2.write(token + ':' + str(index_index[token[0].upper()]) + '\n')
            index_index[token[0].upper()] = index_index[token[0].upper()] + len(output)
            print('', end='\033[F')
    print()

    # For fun, output how long it took to save the index to a file
    writeEndTime = time.time()
    print('Time it took to write to file:', str(writeEndTime-writeStartTime))
    print('====== END ======')

# Returns the posting information from a word based on its info in the index file
def getWordPostingFromFile(startingWord):
    output = dict()
    startingWord = startingWord.lower() # Set the word to be all lower case
    startingLetter = startingWord[0].upper() # Get the first letter of the starting word
    postingList = list()
    for indexNum in indexLimits: # For the all index files we have
        index_file2 = index_file + str(indexNum)
        try:
            # Open both the index file and the index of the index file
            with open(index_file2 + '\\index' + startingLetter + '.txt', 'r', encoding='utf-8') as f, open(index_file2 + '\\index' + startingLetter + 'Index.txt', 'r', encoding='utf-8') as f2:
                if(f is None or f2 is None): continue # If the file doesn't exist, continue

                index_line = f2.readline() # Read the line of the index of the index file
                limit = 0
                while index_line: # While there is a line to read
                    indexSplit = index_line.split(':')
                    indexWord = indexSplit[0]
                    indexPosition = int(indexSplit[1]) # Get the position of where the word starts in the index file
                    # Temporary fix because index of index is wrong
                    indexPosition += limit
                    limit += 1
                    # print(indexPosition)
                    
                    # Use this library to get the nearest similarity to the word
                    if(difflib.get_close_matches(startingWord, [indexWord], cutoff=0.85)):
                        f.seek(indexPosition) # Get the position of the word in the index file
                        postingLine = f.readline() # Read where the word line is
                        
                        postingInfo = postingLine.split(' ') # Split it so we have the word and its posting
                        
                        # Because special letters have a length greater than 1
                        # We need to adjust the position so the seek is correct
                        notABC = (char for char in postingInfo[0] if char not in 'abcdefghijklmnopqrstuvwxyz0123456789|,\n-_\'')
                        for char in notABC: limit += 1

                        wordInfo = postingInfo[1].split('|') # The postings are split with '|' 
                        for word in wordInfo:
                            idAndPosition = word.split(',') # The document ID and word position is split with ','
                            if(len(idAndPosition) != 3): continue # Sometimes we get values that are not what we want, so skip them
                            # Create and populate the postings
                            posting = Posting() 
                            posting.setId(int(idAndPosition[0]))
                            posting.setPosition(int(idAndPosition[1]))
                            postingList.append(posting)
                        break
                    index_line = f2.readline()
        except FileNotFoundError:
            pass
        except UnicodeDecodeError:
            pass
    output[startingWord] = postingList
    return output

# Calculate document frequencies from postings
def getDocFrequencyFromPosting(postingDict):
    output = dict()
    for word,postings in postingDict.items(): # For the word and its postings
        lastDocId = postings[0].getId()
        docFreq = 0
        docFreqList = list()
        for posting in postings: # For every posting in the list of postings
            if lastDocId != posting.getId(): # If the docID changed, then we need to add up how many times its appeared
                docFreqList.append((lastDocId, docFreq)) 
                docFreq = 0
            docFreq += 1
            lastDocId = posting.getId()
        docFreqList.append((lastDocId, docFreq))
        output[word] = docFreqList
    return output
    
# Calculate intersecting points across two different lists
# Based on the notes in class
def intersect(list1, list2):
    output = list()
    list1 = enumerate(list1)
    list2 = enumerate(list2)
    elem1 = next(list1, None)
    elem2 = next(list2, None)
    while elem1 is not None and elem2 is not None:
        if elem1[1][0] == elem2[1][0]:
            output.append(elem1[1])
            elem1 = next(list1, None)
            elem2 = next(list2, None)
        elif elem1[1][0] < elem2[1][0]: elem1 = next(list1, None)
        else: elem2 = next(list2, None)
    return output

# Returns how many URLs were printed
def printURLs(collection, limiter):
    urls = set()
    for freq in sorted(collection, key=lambda a: a[1], reverse=True): # Sort list by value (by Doc Frequency)
        if(len(urls) == limiter): break
        with open(doc_index_file, 'r') as f: 
            line = f.readline()
            while line != '': # Look through all the documents in the document to ID file
                lineParse = line.split(';')
                if(freq[0] == int(lineParse[0])):
                    with open(lineParse[1].strip('\n'), 'r') as f2:
                        data = json.load(f2)
                        link = data['url']
                        defraggedURL = urldefrag(link)[0] # Defrag the URL
                        urls.add(defraggedURL)
                line = f.readline()
    for url in urls:
        print(url)
    return len(urls)

if __name__ == '__main__':
    # indexDocuments(indexLimits[5])
    query = input("Please enter a query: ")
    startTime = time.time()
    test = list()
    for word in query.split(' '):
        word = ps.stem(word)
        postingDict = getWordPostingFromFile(word)
        postingFreq = getDocFrequencyFromPosting(postingDict)
        test2 = list()
        for freqList in postingFreq.values():
            test2 += freqList
        test.append(test2)
    if(len(test) == 1):
        printURLs(test[0], 5)
    else:
        count = 1
        compare = list()
        while count < len(test):
            if(count > 1):
                compare = intersect(compare, test[count])
            else:
                compare = intersect(test[0], test[1])
            count += 1
        limit = printURLs(compare, 5)
        if limit < 5: printURLs(test[0], 5-limit)
    endTime = time.time()
    print("Query Time:", str((endTime-startTime)*1000), 'ms')


# Write to the output file
#output = ''
#with open(output_file, 'w') as f:
#    output += 'Number of Files: ' + str(numFiles) + '\n'
#    output += 'Number of JSONs: ' + str(limiter) + '\n'
#    output += 'Number of unique words: ' + str(len(index)) + '\n'
#    f.write(output)

# for token in sorted(index.keys()):
#     with open(index_file + 'index' + token[0].upper() + '.txt', 'a', encoding='utf-8') as f:
#         # Write to file as
#         # word wordFrequency,importantScore,URL wordFrequency,importantScore,URL ...
#         output = token
#         for posting in index[token]:
#             output += ' {0},{1},{2} ['.format(str(posting.getId()), str(posting.getWordFrequency()), str(posting.getImportantScore()))
#             for positions in posting.getPositions():
#                 output += '{0},'.format(str(positions))
#             output = output[:-1] + ']'
#         output += '\n'
#         f.write(output)