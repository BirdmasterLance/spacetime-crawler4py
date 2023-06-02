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
from simhash import Simhash

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
project_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py"

# IMPORTANT -> Edit json_dir to the path of your DEV (containing JSON) folder <- IMPORTANT
json_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\DEV"


class InvertedIndexer:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_index_dict = {}
        self.urls_visited = set()

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
                if link in self.urls_visited:
                    continue
                else:
                    self.urls_visited.add(link)

                soup = BeautifulSoup(content, 'html.parser')

                for section in soup.find_all(text=True):
                    if section.parent.name not in self.blacklist:
                        text = section.string

                        tokens = re.finditer(r'\b\w+\b', text.lower())
                        for tokenMatch in tokens:
                            token = ps.stem(tokenMatch.group())

                            if len(token) == 1:
                                continue

                            # Write to index as a Posting object
                            posting = Posting()
                            posting.setId(docId)
                            posting.setPosition(tokenMatch.start())
                            posting.setImportantScore(section.parent.name)
                            self.index[token].append(posting)

                with open(self.doc_index_file, 'a') as f:
                    f.write(str(docId) + ';' + filename + '\n')
                self.doc_index_dict[docId] = filename
                docId += 1

                endTime = time.time()
                print('Execution time for', filename, ': ', str(endTime - startTime))

                # Offload index to disk if the count reaches the limit
                if len(self.index) >= 100000:
                    folder_path = pathlib.Path(
                        "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\partial_indexes")
                    self.savePartialIndex(folder_path)
                    self.index.clear()
                    self.partial_index_count += 1

        print('ran out of files to index through')
        totalEndTime = time.time()
        print('Total execution time:', str(totalEndTime - totalStartTime))

    def savePartialIndex(self, folder_path):
        self.partial_index_count += 1
        partial_index_path = folder_path / ('partial' + str(self.partial_index_count))
        partial_index_path.mkdir()

        writeStartTime = time.time()

        for token in sorted(self.index.keys()):
            with open(
                    partial_index_path / ('index' + token[0].upper() + '.txt'),
                    'a', encoding='utf-8'
            ) as f:
                numPostings = len(self.index[token])
                progress = 0

                output = token + ' '
                for posting in self.index[token]:
                    output += '{0},{1},{2}|'.format(
                        str(posting.getId()), str(posting.getPosition()), str(posting.getImportantScore())
                    )

                    progress += 1
                    print(token + ';' + str(progress) + '/' + str(numPostings) + self.blank_space, end='\r')

                output = output[:-1] + '\n'
                f.write(output)

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
        self.doc_index_file = project_dir + "\\docIndexFile.txt"
        self.index_limits = indexLimits

    def getWordPostingFromFile(self, startingWord):
        output = dict()
        startingWord = startingWord.lower()
        startingLetter = startingWord[0].upper()
        postingList = list()

        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                for line in f:
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
                        break

        except FileNotFoundError:
            pass
        except UnicodeDecodeError:
            pass

        output[startingWord] = postingList
        return output

    def getDocFrequencyFromPosting(self, postingDict):
        output = dict()
        for word, postings in postingDict.items():
            if len(postings) == 0:
                continue  # Skip if no postings available for the word
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
                        with open(lineParse[1].strip('\n'), 'r') as f2:
                            data = json.load(f2)
                            link = data['url']
                            defraggedURL = urldefrag(link)[0]
                            urls.add(defraggedURL)
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
            postingFreq = self.getDocFrequencyFromPosting(postingDict)
            test2 = list()
            for freqList in postingFreq.values():
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
    # index.indexDocuments(indexLimits[0])
    # index.mergeIndexes()
    # Comment out above after index creation

    search_gui = SearchEngineGUI()
    search_gui.run()
