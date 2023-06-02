import json
import math
import os
import re
import pathlib
from collections import defaultdict
from tkinter import scrolledtext

from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from urllib.parse import urldefrag
import tkinter as tk
from simhash import Simhash, SimhashIndex
import difflib

import time


# IMPORTANT: PLEASE NAVIGATE TO LINES 133 and 136 TO CHANGE YOUR DIRECTORY PATHS
# IMPORTANT: PLEASE NAVIGATE TO LINE 464 FOR INSTRUCTIONS ON RUNNING THE PROGRAM

# Interface for the search engine
class SearchEngineGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Search Engine")

        # Create search query input
        self.query_label = tk.Label(self.window, text="Enter your query:")
        self.query_label.pack()
        self.query_entry = tk.Entry(self.window, width=50)
        self.query_entry.pack()

        # Create search button
        self.search_button = tk.Button(self.window, text="Search", command=self.process_search)
        self.search_button.pack()

        # Create results window
        self.results_window = scrolledtext.ScrolledText(self.window, width=160, height=30)
        self.results_window.pack()

        # Create label for query time
        self.time_label = tk.Label(self.window, text="Query Time: ")
        self.time_label.pack()

        # Query variable
        self.query = ""

        # List of webpages
        self.webpages = []

        # Search engine instance
        self.search_engine = SearchEngine()

        # Time elapsed to find relevant webpages
        self.query_time = 0.0

    def process_search(self):
        # Get the query from the entry field
        self.query = self.query_entry.get()

        # Reset the results window
        self.results_window.delete("1.0", tk.END)

        # Do not except empty strings
        if len(self.query.strip()) > 0:

            # Run the search engine
            search_results, self.query_time = self.search_engine.run_engine(self.query)

            # Display the search results in the results window
            for result in search_results:
                self.results_window.insert(tk.END, result + "\n")

        # Update the query time label
        self.time_label.config(text="Time to fetch webpages: " + str(self.query_time))

    def get_query(self):
        return self.query

    def run(self):
        self.window.mainloop()


# Special class for posting to hold information per website
# Needs some fixing so it can keep track of words PER document
# as well as score PER document
class Posting:
    def __init__(self):
        self.id = 0
        self.wordFrequency = 0
        # If the word in this URL is in header, bold, or strong,
        # then this posting is a little more important
        self.importantScore = 0.0

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


indexLimits = [0, 1307, 5367, 7946, 16884, 20318]
results = set()
ps = PorterStemmer()

# IMPORTANT -> Edit project_dir to the path of your project folder <- IMPORTANT
project_dir = "C:\\Users\\huule\\Desktop\\School\\CS121"

# IMPORTANT -> Edit json_dir to the path of your DEV (containing JSON) folder <- IMPORTANT
json_dir = "C:\\Users\\huule\\Desktop\\School\\CS121\\DEV"


class InvertedIndexer:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_index_dict = {}
        self.urls_visited = set()
        self.simhashIndex = SimhashIndex([], k=3)
        self.index_file = project_dir + "\\index"
        self.doc_index_file = project_dir + "\\docIndexFile.txt"
        self.merge_index_file = project_dir + "\\mergeIndexFile.txt"

        self.blacklist = [
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
        self.blank_space = '                                                                   '
        self.startId = None
        self.partial_index_count = 0

    def indexDocuments(self, docId):
        self.startId = docId
        numFiles = 0
        path = pathlib.Path(json_dir)
        totalStartTime = time.time()

        partial_indexes_folder = os.path.join(project_dir, 'partial_indexes')
        os.makedirs(partial_indexes_folder, exist_ok=True)  # Create partial_indexes folder if it doesn't exist

        for filename in path.rglob("*"):
            numFiles += 1
            filename = str(filename)

            if filename.endswith(".json"):
                startTime = time.time()

                with open(filename, "r") as f:
                    data = json.load(f)

                content = data["content"]

                link = data['url']
                link = urldefrag(link)
                if link[0] in self.urls_visited:
                    continue
                else:
                    self.urls_visited.add(link[0])

                soup = BeautifulSoup(content, 'html.parser')


                simhashValue = Simhash(soup.get_text())
                if len(self.simhashIndex.get_near_dups(simhashValue)) == 0:
                    self.simhashIndex.add(numFiles, simhashValue)
                else:
                    print("================= SKIPPED {0} BECAUSE OF SIMILARITY ===============\n".format(filename))
                    continue


                # for section in soup.find_all(text=True):
                #     if section.parent.name not in self.blacklist:
                #         text = section.string

                #         tokens = re.finditer(r'\b(\d+)|(([a-z]+)|([A-Z]))\b', text.lower())
                #         for tokenMatch in tokens:
                #             token = ps.stem(tokenMatch.group())

                #             if len(token) == 1:
                #                 continue

                #             posting = Posting()
                #             posting.setId(docId)
                #             posting.setPosition(tokenMatch.start())
                #             posting.setImportantScore(section.parent.name)
                #             self.index[token].append(posting)

                with open(self.doc_index_file, 'a') as f:
                    f.write(str(docId) + ';' + filename + ';' + str(link[0]) + '\n')
                self.doc_index_dict[docId] = filename
                docId += 1

                endTime = time.time()
                print('Execution time for', filename, ': ', str(endTime - startTime))

                # Offload index to disk if the count reaches the limit
        #         if len(self.index) >= 1000:
        #             folder_path = pathlib.Path(
        #                 project_dir + "\\partial_indexes")
        #             self.savePartialIndex(folder_path)
        #             self.index.clear()
        #             self.partial_index_count += 1
        # folder_path = pathlib.Path(
        #                 project_dir + "\\partial_indexes")
        # self.savePartialIndex(folder_path)
        print('ran out of files to index through')
        totalEndTime = time.time()
        print('Total execution time:', str(totalEndTime - totalStartTime))

    def savePartialIndex(self, folder_path):
        self.partial_index_count += 1
        partial_index_path = folder_path / ('partial' + str(self.partial_index_count))
        partial_index_path.mkdir()

        writeStartTime = time.time()

        indexPos = 0
        with open(
                    partial_index_path / ('index' + '.txt'),
                    'a', encoding='utf-8'
            ) as f, open(
                    partial_index_path / ('index' + 'Index.txt'),
                    'a', encoding='utf-8'
            ) as f2:
            for token in sorted(self.index.keys()):
                progress = 0
                numPostings = len(self.index[token])

                output = token + ' '
                for posting in self.index[token]:
                    output += '{0},{1},{2}|'.format(
                        str(posting.getId()), str(posting.getPosition()), str(posting.getImportantScore())
                    )

                    progress += 1
                    print(token + ';' + str(progress) + '/' + str(numPostings) + self.blank_space, end='\r')

                output = output[:-1] + '\n'
                f.write(output)

                f2.write(token + ':' + str(indexPos) + '\n')
                indexPos += len(output)
                print('', end='\033[F')

        writeEndTime = time.time()

        print('Time it took to write to file:', str(writeEndTime - writeStartTime))
        print('====== NEXT PARTITION ======')

    def mergeIndexes(self):
        partial_indexes_folder = os.path.join(project_dir, 'partial_indexes')

        # Get a list of all the partial index files
        partial_index_files = [f for f in os.listdir(partial_indexes_folder) if f.startswith('partial')]

        # Sort the partial index files based on their numeric suffix
        partial_index_files.sort(key=lambda x: int(x[7:]))

        # Open the merge index file
        with open(self.merge_index_file, 'w', encoding='utf-8') as merge_file:
            # Merge the partial indexes into the merge index file
            for partial_index_file in partial_index_files:
                partial_index_path = os.path.join(partial_indexes_folder, partial_index_file)

                if os.path.isfile(partial_index_path):
                    with open(partial_index_path, 'r', encoding='utf-8') as partial_file:
                        merge_file.write(partial_file.read())
                else:
                    # Iterate over files in the partial index directory
                    for filename in os.listdir(partial_index_path):
                        file_path = os.path.join(partial_index_path, filename)
                        if os.path.isfile(file_path):
                            with open(file_path, 'r', encoding='utf-8') as partial_file:
                                # Iterate over lines in the partial index file
                                for line in partial_file:
                                    # Write each line to the merge index file
                                    merge_file.write(line)

        print('Merge indexes completed.')


# noinspection PyMethodMayBeStatic
class SearchEngine:
    def __init__(self):
        self.index_file = project_dir + "\\mergeIndexFile.txt"
        self.index_of_index_file = project_dir + "\\mergeIndexIndexFile.txt"
        self.doc_index_file = project_dir + "\\docIndexFile.txt"
        self.index_limits = indexLimits

    def getWordPostingFromFile(self, startingWord):
        output = dict()
        startingWord = startingWord.lower()
        postingList = list()

        try:
            indexPosition = 0
            with open(self.index_of_index_file, 'r', encoding='utf-8') as f:
                limit = 0
                for line in f:
                    indexSplit = line.split(':')
                    indexWord = indexSplit[0]
                    indexPosition = int(indexSplit[1])  # Get the position of where the word starts in the index file
                    # Temporary fix because index of index is wrong
                    indexPosition += limit
                    limit += 1

                    # Use this library to get the nearest similarity to the word
                    if difflib.get_close_matches(startingWord, [indexWord], cutoff=0.95): 
                        break
            with open(self.index_file, 'r', encoding='utf-8') as f:
                f.seek(indexPosition)
                line = f.readline()
                indexSplit = line.strip().split(' ')
                indexWord = indexSplit[0]
                if indexWord == startingWord:
                    postingsInfo = indexSplit[1].split('|')
                    for postingInfo in postingsInfo:
                        postingParts = postingInfo.split(',')
                        if len(postingParts) != 3:
                            continue
                        posting = Posting()
                        posting.setId(int(postingParts[0]))
                        posting.setPosition(int(postingParts[1]))
                        posting.setImportantScore(postingParts[2])
                        postingList.append(posting)

        except FileNotFoundError:
            pass
        except UnicodeDecodeError:
            pass

        output[startingWord] = postingList
        return output
    
    def getTermFrequencyFromPosting(self, postingDict):
        output = dict()
        termFreqList = list() # We are saving the term frequencies as a pair of (docID, termFreq)
        for word, postings in postingDict.items(): # For every posting associated with a specific word
            if len(postings) == 0:
                output[word] = termFreqList
                return output  # Skip if no postings available for the word
            lastDocId = postings[0].getId() # Get the current document ID we are on
            termFreq = 0 # Get the number of times the term shows up in a specific document
            for posting in postings: # For every posting
                # If the current document ID we are on right now is NOT the same as the one before,
                # then we are finished with that document
                if lastDocId != posting.getId(): 
                    termFreqList.append((lastDocId, 1 + math.log(termFreq,10))) # Save the score and the document in the list
                    termFreq = 0
                termFreq += 1 # Increment the number of times this term appears in by 1
                lastDocId = posting.getId() # Update hte last document ID saved
            termFreqList.append((lastDocId, 1 + math.log(termFreq,10)))
        #termFreqList.sort(key=lambda x:x[1], reverse=True) # Sort termFrequencies in descending order (best scores on top)
        output[word] = termFreqList
        return output

    def getInverseDocFrequencyFromPosting(self, postingDict):
        output = dict() # the dictionary that will be returned, with 
        docCount = 40140 # number of valid documents being looked at
        relevantDocs = list() # going to hold the docs the term appears in (a set is used to avoid duplicate docIDs being counted twice)
        inverseFreq = 0 # going to hold the inverse document frequency value
        for word, postings in postingDict.items():
            for post in postings:
                relevantDocs.append(post)
            output[word] = len(relevantDocs)  # create the entry in the dictionary and the length of its associated value, representing
            # the number of docs it appears in
        
        for word, docFreq in output.items():
            inverseFreq = math.log(docCount/docFreq) # using the document frequency from before, taking log of all docs / this term's doc freq
            output[word] = inverseFreq # replace the document frequency value with the inverse doc frequency
        
        return output

    def intersect(self, list1, list2):
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
            elif elem1[1][0] < elem2[1][0]:
                elem1 = next(list1, None)
            else:
                elem2 = next(list2, None)
        return output

    def returnURLs(self, collection, limiter):
        urls = set()
        for freq in sorted(collection, key=lambda a: a[1], reverse=True):
            if len(urls) == limiter:
                break
            with open(self.doc_index_file, 'r') as f:
                line = f.readline()
                while line != '':
                    lineParse = line.split(';')
                    if freq[0] == int(lineParse[0]):
                            urls.add(lineParse[2])
                    line = f.readline()

        for url in urls:
            results.add(url)

        return urls

    # def vectorize(self, text):
    #     corpus = []  # List to hold the documents for vectorization
    #     # Add your document text to the corpus list
    #     # For example, if you have a list of documents, you can append them to the corpus list
    #
    #     # Initialize the TF-IDF vectorizer
    #     vectorizer = TfidfVectorizer()
    #
    #     # Fit the vectorizer on the corpus to learn the vocabulary and IDF weights
    #     vectorizer.fit(corpus)
    #
    #     # Transform the given text using the learned vectorizer
    #     vectorized_text = vectorizer.transform([text])
    #
    #     # Create a dictionary where the keys represent the words and the values represent the TF-IDF weights
    #     feature_names = vectorizer.get_feature_names()
    #     vectorized_dict = {}
    #     for col in vectorized_text.nonzero()[1]:
    #         vectorized_dict[feature_names[col]] = vectorized_text[0, col]
    #
    #     return vectorized_dict
    #
    # def calculateCosineSimilarity(self, query, document):
    #     query_vector = self.vectorize(query)  # Function to convert query to a vector representation
    #     document_vector = self.vectorize(document)  # Function to convert document to a vector representation
    #
    #     dot_product = sum(query_vector[word] * document_vector[word] for word in query_vector if word in document_vector)
    #     query_norm = math.sqrt(sum(query_vector[word] ** 2 for word in query_vector))
    #     document_norm = math.sqrt(sum(document_vector[word] ** 2 for word in document_vector))
    #
    #     cosine_similarity = dot_product / (query_norm * document_norm) if (query_norm * document_norm) != 0 else 0
    #     return cosine_similarity

    def run_engine(self, query):
        startTime = time.time()
        test = list()
        for word in query.split(' '):
            word = ps.stem(word)
            postingDict = self.getWordPostingFromFile(word)
            postingTermFreq = self.getTermFrequencyFromPosting(postingDict)
            postingDocFreq = self.getInverseDocFrequencyFromPosting(postingDict)
            
            # Delete later this is just how i see what values are in term and inverse doc frequency
            # for postingList in postingTermFreq.values():
            #     for posting in postingList:
            #         print('docID: {0} termFreq: {1}'.format(posting[0], posting[1]))
            # for term, freq in postingDocFreq.items():
            #     print('term: {0} InverseDocFreq: {1}'.format(term, freq))
            
            
            test2 = list()
            for freqList in postingTermFreq.values():
                test2 += freqList
            test.append(test2)
        if len(test) == 1:
            result_urls = self.returnURLs(test[0], 5)
        else:
            count = 1
            compare = list()
            while count < len(test):
                if count > 1:
                    compare = self.intersect(compare, test[count])
                else:
                    compare = self.intersect(test[0], test[1])
                count += 1
            compare_urls = self.returnURLs(compare, 5)
            if len(compare_urls) < 5:
                remaining_urls = self.returnURLs(test[0], 5 - len(compare_urls))
                result_urls = compare_urls.union(remaining_urls)
            else:
                result_urls = compare_urls

        # results = []
        # for url in result_urls:
        #     similarity = self.calculateCosineSimilarity(query, url)
        #     results.append((url, similarity))

        endTime = time.time()
        print("Query Time:", str((endTime - startTime) * 1000), 'ms')
        return result_urls, str((endTime - startTime))


# README:
# Step 1: Ensure that you have corrected the folder paths on lines 133 and 136
# Step 2: If this is your first time running the program (no index created yet), uncomment lines 469-471
# Step 3: The program will run on the DEV (or otherwise selected) folder, and will create an inverted index
# Step 4: The program will then launch an interface to search queries
# NOTE: Comment out lines 472-475 after the index creation
if __name__ == '__main__':
    # Comment out below after index creation
    # index = InvertedIndexer()
    # index.indexDocuments(0)
    # index.mergeIndexes()
    # Comment out above after index creation

    search_gui = SearchEngineGUI()
    search_gui.run()
