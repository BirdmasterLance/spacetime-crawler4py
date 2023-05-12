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
        self.wordURLs = set()
        self.totalWordFrequency = 0
        self.docWordCount = dict()
    
    def getTotalWordFrequency(self):
        return self.totalWordFrequency

    def setTotalWordFrequency(self, frequency):
        self.totalWordFrequency = frequency
    
    def getWordURLs(self):
        return self.wordURLs

    def __eq__(self, other):
        return self.wordFrequency == other.wordFrequency

    def __lt__(self, other):
        return self.wordFrequency < other.wordFrequency
    
    def __le__(self, other):
        return self.wordFrequency <= other.wordFrequency

json_dir = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV"

index_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\indexer.txt"

output_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\output.txt"

emergency_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\emergency.txt"

emergency2_file = "C:\\Users\\huule\\Desktop\\School\\CS121\\emergency2.txt"
index = dict()

limiter = 0

numFiles = 0

path = pathlib.Path(json_dir)
totalStartTime = time.time()

# Set up the stemmer
ps = PorterStemmer()

for filename in path.rglob("*"):
    numFiles += 1 # Keep track of the number of files
    filename = str(filename)
    if filename.endswith(".json"):
        startTime = time.time()
        limiter += 1 # Originally was how many JSONs before stopping, now its just the number of JSONs
        # read in the JSON data from the file
        with open(filename, "r") as f:
            data = json.load(f)

        # extract the text from the JSON data
        content = data["content"]
        link = data['url']
        soup = BeautifulSoup(content, 'html.parser') # Parse the HTML content

        # TODO: put emphasis on headers, bold, and strong text
        # print('===== h1 headers =====')
        # for heading1 in soup.find_all('h1'):
        #     print(heading1.string)
        # print('\n===== h2 headers =====')
        # for heading2 in soup.find_all('h2'):
        #     print(heading2.string)
        # print('\n===== h3 headers =====')
        # for heading3 in soup.find_all('h3'):
        #     print(heading3.string)
        # print('\n===== bold =====')
        # for bold in soup.find_all('b'):
        #     print(bold.string)
        # print('\n===== strong =====')
        # for strong in soup.find_all('strong'):
        #     print(strong.string)


        # tokenize the text and build the inverted index
        text = soup.get_text()
        tokens = re.findall(r'\b\w+\b', text.lower())
        for token in tokens:
            token = ps.stem(token) # Stem the word to reduce repeated words
            if token not in index:
                index[token] = Posting() # Initialize a new posting
            index[token].getWordURLs().add(link) # Add the link in the set of URLs in the posting
            index[token].setTotalWordFrequency(index[token].getTotalWordFrequency()+1) # Increase the number of times the word has appeared
        endTime = time.time()
        print('Execution time for', filename, ': ', str(endTime-startTime)) # For fun, print how long it took to complete the file

# Write to the output file
output = ''
with open(output_file, 'w') as f:
    output += 'Number of Files: ' + str(numFiles) + '\n'
    output += 'Number of JSONs: ' + str(limiter) + '\n'
    output += 'Number of unique words: ' + str(len(index)) + '\n'
    f.write(output)

print('ran out of files to index through, writing output to file now')
totalEndTime = time.time()
print('Total execution time:', str(totalEndTime-totalStartTime))

writeStartTime = time.time()

# Sort the index by most common word (might change later to just be sorted alphabetically)
sorted_index = sorted(index.items(), key=lambda x:x[1], reverse=True)
index = dict(sorted_index)

# write the inverted index to the output file
with open(index_file, "w", encoding="utf-8") as f:
    output = ''
    for token in index:
        # Write to file as:
        # Token number_of_times_word_appears===list_of_documents_word_appears_in
        output = token + ' ' + str(index[token].getWordFrequency()) + '===' 
        for link in index[token].getWordURLs():
            output += link + ', '
        output += '\n\n'
        f.write(output)
writeEndTime = time.time()
print('Time it took to write to file:', str(writeEndTime-writeStartTime))

print('====== END ======')