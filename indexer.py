import json
import re
import pathlib
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
	
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

json_dir = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV"

index_file1 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index0\\"
index_file2 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index1307\\"
index_file3 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index5367\\"
index_file4 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index7947\\"
index_file5 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index14306\\"
index_file6 = "C:\\Users\\huule\\Desktop\\School\\CS121\\index17739\\"
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


def indexDocuments():
    docId = 0
    numFiles = 0
    path = pathlib.Path(json_dir)
    totalStartTime = time.time()

    for filename in path.rglob("*"):
        numFiles += 1 # Keep track of the number of files
        trueFileName = filename.name
        filename = str(filename)

        #if(docId == 10):
        #    print("Limited reached, ending loop")
        #    break

        if filename.endswith(".json"):
            startTime = time.time()
            docId += 1 
            #if(docId == 16945):
            #    docId += 1

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
                
                if(not token.isnumeric() and len(token) == 1): continue
                
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
                f.write(str(docId) + ':' + filename + '\n')
            endTime = time.time()
            print('Execution time for', filename, ': ', str(endTime-startTime)) # For fun, print how long it took to complete the file
    print('ran out of files to index through')
    totalEndTime = time.time()
    print('Total execution time:', str(totalEndTime-totalStartTime))



    # Sort the index by most common word (might change later to just be sorted alphabetically)
    # sorted_index = sorted(index.items(), key=lambda x:x[1], reverse=True)
    # index = dict(sorted_index)

    # write the inverted index to the output file

    index_index = dict()

    writeStartTime = time.time()
    for token in sorted(index.keys()):
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
                print(token + ':' + str(progress) + '/' + str(numPostings))
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
def getWordPostingFromFile(word):
    output = dict()
    startingLetter = word[0].upper()
    for index_file in index_files:
        with open(index_file + 'index' + startingLetter + '.txt', 'r', encoding='utf-8') as f, open(index_file + 'index' + startingLetter + 'Index.txt', 'a', encoding='utf-8') as f2,:
            postingList = list()
            index_line = f2.readline()
            while index_line:
                indexPosition = int(index_line)
                f.seek(indexPosition)
                postingLine = f.readline()
                postingInfo = postingLine.strip(' ')
                if(postingInfo[0] == word):
                    wordInfo = postingInfo[1].split('|')
                    for word in wordInfo:
                        idAndPosition = word.split(',')
                        posting = Posting()
                        posting.setId = int(idAndPosition[0])
                        posting.setPosition = int(idAndPosition[1])
                        postingList.append(posting)
                    output[word] = postingList
                    break
                index_line = f2.readline()
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
                docFreqList = list()
            docFreq += 1
            lastDocId = posting.getId()
        output[word] = docFreqList
    return output
    
def intersect():
    pass


if __name__ == '__main__':
    getWordPostingFromFile('ACM')

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