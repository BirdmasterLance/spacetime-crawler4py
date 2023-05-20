import json
import re
import pathlib
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import difflib
from urllib.parse import urldefrag
	
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
        self.position = 0
    
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

json_dir1 = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV0"
json_dir2 = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV1308"
json_dir3 = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV5368"
json_dir4 = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV7947"
json_dir5 = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV16885"
json_dir6 = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV20319"

index_file1 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index0\\"
index_file2 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index1308\\"
index_file3 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index5368\\"
index_file4 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index7947\\"
index_file5 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index16885\\"
index_file6 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index20319\\"
index_files = [index_file1, index_file2, index_file3, index_file4, index_file5, index_file6]

output_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\output.txt"

emergency_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\emergency.txt"

emergency2_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\emergency2.txt"

doc_index_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\docIndexFile.txt"

index = dict()

doc_index_dict = dict()

def checkHeaderForWord(soup, header, word):
    for section in soup.find_all(header):
        if(section.get_text() is None): continue
        if(word in section.get_text()): return True
    return False


def indexDocuments(docId):
    numFiles = 0
    path = pathlib.Path(json_dir6)
    totalStartTime = time.time()

    for filename in path.rglob("*"):
        numFiles += 1 # Keep track of the number of files
        filename = str(filename)

        if filename.endswith(".json"):
            startTime = time.time()
            docId += 1 

            # read in the JSON data from the file
            with open(filename, "r") as f:
                data = json.load(f)

            # extract the text from the JSON data
            content = data["content"]
            link = data['url']
            soup = BeautifulSoup(content, 'html.parser') # Parse the HTML content

            # tokenize the text and build the inverted index
            text = soup.get_text()
            tokens = re.finditer(r'\b\w+\b', text.lower()) # Changed to find iter so we can save position of match
            for tokenMatch in tokens:
                token = ps.stem(tokenMatch.group()) # Stem the word to reduce repeated words
                
                if(len(token) == 1 or token.isnumeric()): continue
                
                if token not in index:
                    index[token] = list() # Initialize a new list of postings
                
                posting = Posting()
                posting.setId(docId)
                posting.setPosition(tokenMatch.start())
                index[token].append(posting)
                # foundPosting = False
                # if(len(index[token]) != 0):
                #     for posting in index[token]:
                #         if(posting.getId() == docId):
                #             posting.setWordFrequency(posting.getWordFrequency()+1)
                #             posting.getPositions().append(tokenMatch.start())
                #             foundPosting = True
                #             break
                # if(foundPosting is False):
                #     posting = Posting()
                #     posting.setId(docId)
                #     posting.setWordFrequency(1)
                #     posting.getPositions().append(tokenMatch.start())
                #     index[token].append(posting)

                    # Check if the word is important
                    # if(soup.find(re.compile('^h[1-6]$'), string=token) != None): posting.setImportantScore(posting.getImportantScore()+1)
                    # elif(soup.find('b', string=token) != None): posting.setImportantScore(posting.getImportantScore()+1)
                    # elif(soup.find('strong', string=token) != None): posting.setImportantScore(posting.getImportantScore()+1)
                    # elif(soup.find('title', string=token) != None): posting.setImportantScore(posting.getImportantScore()+1)

            with open(doc_index_file, 'a') as f:
                f.write(str(docId) + ';' + filename + '\n')
            endTime = time.time()
            print('Execution time for', filename, ': ', str(endTime-startTime)) # For fun, print how long it took to complete the file
    print('ran out of files to index through')
    totalEndTime = time.time()
    print('Total execution time:', str(totalEndTime-totalStartTime))

    index_index = dict()

    writeStartTime = time.time()
    for token in sorted(index.keys()):
        index_file = index_file6
        with open(index_file + 'index' + token[0].upper() + '.txt', 'a', encoding='utf-8') as f, open(index_file + 'index' + token[0].upper() + 'Index.txt', 'a', encoding='utf-8') as f2:
            print('saving ' + token + ' to file')
            if(token[0].upper() not in index_index):
                index_index[token[0].upper()] = 0

            output = token + ' '
            numPostings = len(index[token])
            progress = 0
            for posting in index[token]:
                output += '{0},{1}|'.format(str(posting.getId()), str(posting.getPosition()))
                progress += 1
                print(token + ';' + str(progress) + '/' + str(numPostings))
                print ("\033[A                             \033[A")
            output = output[:-1] + '\n'
            f.write(output)

            f2.write(str(index_index[token[0].upper()]) + '\n')
            index_index[token[0].upper()] = index_index[token[0].upper()] + len(output)
            print ("\033[A                                                                                                   \033[A")
    writeEndTime = time.time()
    print('Time it took to write to file:', str(writeEndTime-writeStartTime))
    print('Writing doc ids to docs')
    print('====== END ======')

# Returns the posting information from a word based on its info in the index file
def getWordPostingFromFile(startingWord):
    output = dict()
    startingWord = startingWord.lower()
    startingLetter = startingWord[0].upper()
    postingList = list()
    for index_file in index_files:
        try:
            with open(index_file + 'index' + startingLetter + '.txt', 'r', encoding='utf-8') as f, open(index_file + 'index' + startingLetter + 'Index.txt', 'r', encoding='utf-8') as f2:
                if(f is None or f2 is None): continue
                index_line = f2.readline()
                limit = 0
                while index_line:
                    indexPosition = int(index_line)
                    if(indexPosition != 0):
                        indexPosition += limit
                    limit += 1
                    f.seek(indexPosition)
                    postingLine = f.readline()
                    postingInfo = postingLine.split(' ')
                    notABC = (char for char in postingInfo[0] if char not in 'abcdefghijklmnopqrstuvwxyz0123456789|,\n-_\'')
                    for char in notABC: limit += 1
                    if(difflib.get_close_matches(startingWord, [postingInfo[0]], cutoff=0.85)):
                        wordInfo = postingInfo[1].split('|')
                        for word in wordInfo:
                            idAndPosition = word.split(',')
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

def getDocFrequencyFromPosting(postingDict):
    output = dict()
    for word,postings in postingDict.items():
        lastDocId = postings[0].getId()
        docFreq = 0
        docFreqList = list()
        for posting in postings:
            if lastDocId != posting.getId():
                docFreqList.append((lastDocId, docFreq))
                docFreq = 0
            docFreq += 1
            lastDocId = posting.getId()
        docFreqList.append((lastDocId, docFreq))
        output[word] = docFreqList
    return output
    
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
    for freq in sorted(collection, key=lambda a: a[1], reverse=True):
        if(len(urls) == limiter): break
        with open(doc_index_file, 'r') as f:
            line = f.readline()
            while line != '':
                lineParse = line.split(';')
                if(freq[0] == int(lineParse[0])):
                    with open(lineParse[1].strip('\n'), 'r') as f2:
                        data = json.load(f2)
                        link = data['url']
                        defraggedURL = urldefrag(link)[0]
                        urls.add(defraggedURL)
                line = f.readline()
    for url in urls:
        print(url)
    return len(urls)

if __name__ == '__main__':
    query = input("Please enter a query: ")
    test = list()
    for word in query.split(' '):
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