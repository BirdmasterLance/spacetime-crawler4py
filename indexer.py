import json
import math
import os
import re
import pathlib
from collections import defaultdict
from tkinter import scrolledtext

import numpy as np
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import difflib
from urllib.parse import urldefrag
import tkinter as tk
from sklearn.feature_extraction.text import TfidfVectorizer
from simhash import Simhash

import time


def retrieve_search_results():
    # Placeholder function to simulate retrieving search results
    # Replace this with your actual search logic
    search_results = [
        "Processing... \n"
    ]
    return search_results


# noinspection PyArgumentList
class SearchEngineGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Search Engine")
        self.root = tk.Tk()
        self.root.title("Results")

        # Create search query input
        self.query_label = tk.Label(self.window, text="Enter your query:")
        self.query_label.pack()
        self.query_entry = tk.Entry(self.window, width=50)
        self.query_entry.pack()

        # Create search button
        self.search_button = tk.Button(self.window, text="Search", command=self.process_search)
        self.search_button.pack()

        # Create results window
        self.results_window = scrolledtext.ScrolledText(self.root, width=160, height=30)
        self.results_window.pack()

        # Query variable
        self.query = ""

        # List of webpages
        self.webpages = []

        # Search engine instance
        self.search_engine = SearchEngine()

    def process_search(self):
        # Get the query from the entry field
        self.query = self.query_entry.get()

        # Run the search engine
        search_results = self.search_engine.run_engine(self.query)

        self.results_window.delete("1.0", tk.END)

        # Display the search results in the results window
        for result in search_results:
            self.results_window.insert(tk.END, result + "\n")

    def update_results_window(self):
        # Clear the results window
        self.results_window.delete("1.0", tk.END)

        # Display the webpages in the results window
        for webpage in self.webpages:
            self.results_window.insert(tk.END, webpage + "\n")

        # Disable editing in the results window
        self.results_window.configure(state="disabled")

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
        self.importantScore = ""

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


# Used for testing partial indexes (faster time)
indexLimits = [0, 1307, 5367, 7946, 16884, 20318]

# Holds the results of the relevant websites
results = set()

ps = PorterStemmer()


class InvertedIndexer:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_index_dict = {}
        self.urls_visited = set()
        self.project_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py"
        self.json_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\ANALYST2"
        self.index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\index"
        self.doc_index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\docIndexFile.txt"
        self.merge_index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\mergeIndexFile.txt"
        self.document_vectors_file = os.path.join(self.project_dir, 'document_vectors.txt')
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
        self.total_docs = 0

    def indexDocuments(self, docId):
        self.startId = docId
        numFiles = 0
        path = pathlib.Path(self.json_dir)
        totalStartTime = time.time()

        partial_indexes_folder = os.path.join(self.project_dir, 'partial_indexes')
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

                        tokens = re.finditer(r'\b([a-zA-Z0-9]+)\b', text.lower())
                        for tokenMatch in tokens:
                            token = ps.stem(tokenMatch.group())

                            if len(token) == 1 or token in self.blacklist:
                                continue

                            posting = Posting()
                            posting.setId(docId)
                            posting.setPosition(tokenMatch.start())
                            posting.setImportantScore(section.parent.name)
                            self.index[token].append(posting)

                with open(self.doc_index_file, 'a') as f:
                    f.write(str(docId) + ';' + filename + '\n')

                self.doc_index_dict[docId] = filename
                docId += 1
                self.total_docs += 1  # Increment the total_docs counter

                endTime = time.time()
                # print('Execution time for', filename, ': ', str(endTime - startTime))

                # Offload index to disk if the count reaches the limit
                if len(self.index) >= 1000:
                    folder_path = pathlib.Path("C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py"
                                               "\\partial_indexes")
                    self.savePartialIndex(folder_path)
                    self.index.clear()
                    self.partial_index_count += 1

        print('Index completed...')
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
                    if posting.getImportantScore() in self.blacklist:
                        continue

                    output += '{0},{1},{2}|'.format(
                        str(posting.getId()), str(posting.getPosition()), str(posting.getImportantScore())
                    )

                    # progress += 1
                    # print(token + ';' + str(progress) + '/' + str(numPostings) + self.blank_space, end='\r')

                if len(output) > len(token) + 1:
                    output = output[:-1] + '\n'
                    f.write(output)

        writeEndTime = time.time()

        print('Time it took to write to file:', str(writeEndTime - writeStartTime))
        print('====== NEXT PARTITION ======')

    def mergeIndexes(self):
        partial_indexes_folder = os.path.join(self.project_dir, 'partial_indexes')

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
        self.project_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py"
        self.index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\mergeIndexFile.txt"
        self.doc_index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\docIndexFile.txt"
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

        return len(urls)

    def vectorize(self, text):
        corpus = []  # List to hold the documents for vectorization
        # Add your document text to the corpus list
        # For example, if you have a list of documents, you can append them to the corpus list

        # Initialize the TF-IDF vectorizer
        vectorizer = TfidfVectorizer()

        # Fit the vectorizer on the corpus to learn the vocabulary and IDF weights
        vectorizer.fit(corpus)

        # Transform the given text using the learned vectorizer
        vectorized_text = vectorizer.transform([text])

        # Create a dictionary where the keys represent the words and the values represent the TF-IDF weights
        feature_names = vectorizer.get_feature_names()
        vectorized_dict = {}
        for col in vectorized_text.nonzero()[1]:
            vectorized_dict[feature_names[col]] = vectorized_text[0, col]

        return vectorized_dict

    def calculateCosineSimilarity(self, query, document):
        print("hi")
        print(document)
        query_vector = self.vectorize(query)  # Function to convert query to a vector representation
        document_vector = self.vectorize(document)  # Function to convert document to a vector representation

        dot_product = sum(query_vector[word] * document_vector[word] for word in query_vector if word in document_vector)
        query_norm = math.sqrt(sum(query_vector[word] ** 2 for word in query_vector))
        document_norm = math.sqrt(sum(document_vector[word] ** 2 for word in document_vector))

        cosine_similarity = dot_product / (query_norm * document_norm) if (query_norm * document_norm) != 0 else 0
        return cosine_similarity

    def retrieveURLs(self, collection, limiter):
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

        return urls

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
            result_urls = self.retrieveURLs(test[0], 5)
        else:
            count = 1
            compare = list()
            while count < len(test):
                if count > 1:
                    compare = self.intersect(compare, test[count])
                else:
                    compare = self.intersect(test[0], test[1])
                count += 1
            compare_urls = self.retrieveURLs(compare, 5)
            if len(compare_urls) < 5:
                remaining_urls = self.retrieveURLs(test[0], 5 - len(compare_urls))
                result_urls = compare_urls.union(remaining_urls)
            else:
                result_urls = compare_urls

        # # results = []
        # for url in result_urls:
        #     similarity = self.calculateCosineSimilarity(query, url)
        #     results.append((url, similarity))
        #
        # endTime = time.time()
        # print("Query Time:", str((endTime - startTime) * 1000), 'ms')

        return result_urls

    # def returnURLs(self, collection, limiter):
    #     urls = set()
    #     for freq in sorted(collection, key=lambda a: a[1], reverse=True):
    #         if len(urls) == limiter:
    #             break
    #         with open(self.doc_index_file, 'r') as f:
    #             line = f.readline()
    #             while line != '':
    #                 lineParse = line.split(';')
    #                 if freq[0] == int(lineParse[0]):
    #                     with open(lineParse[1].strip('\n'), 'r') as f2:
    #                         data = json.load(f2)
    #                         link = data['url']
    #                         defraggedURL = urldefrag(link)[0]
    #                         urls.add(defraggedURL)
    #                 line = f.readline()
    #
    #     for url in urls:
    #         results.add(url)
    #
    #     return len(urls)

    # def run_engine(self, query):
    #     startTime = time.time()
    #     test = list()
    #     for word in query.split(' '):
    #         word = ps.stem(word)
    #         postingDict = self.getWordPostingFromFile(word)
    #         postingFreq = self.getDocFrequencyFromPosting(postingDict)
    #         test2 = list()
    #         for freqList in postingFreq.values():
    #             test2 += freqList
    #         test.append(test2)
    #     if len(test) == 1:
    #         self.returnURLs(test[0], 5)
    #     else:
    #         count = 1
    #         compare = list()
    #         while count < len(test):
    #             if count > 1:
    #                 compare = self.intersect(compare, test[count])
    #             else:
    #                 compare = self.intersect(test[0], test[1])
    #             count += 1
    #         limit = self.returnURLs(compare, 5)
    #         if limit < 5:
    #             self.returnURLs(test[0], 5 - limit)
    #
    #     endTime = time.time()
    #     print("Query Time:", str((endTime - startTime) * 1000), 'ms')
    #     return results


if __name__ == '__main__':
    # index = InvertedIndexer()
    # index.indexDocuments(indexLimits[0])
    #
    # # Merge the indexes
    # index.mergeIndexes()

    search_gui = SearchEngineGUI()
    search_gui.run()

# HUU'S OLD CODE
#
# Set up the stemmer
# ps = PorterStemmer()
#
# indexLimits = [0, 1307, 5367, 7946, 16884, 20318]
#
# project_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py"
# json_dir = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\ANALYST"
# index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\index"
# doc_index_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\docIndexFile.txt"
#
# index = dict()
# doc_index_dict = dict()
# results = set()
#
# output_file = "C:\\Users\\Jeffrey Qin\\PycharmProjects\\spacetime-crawler4py\\output.txt"
#
# blank_space = '                                                                   '
#
# blacklist = [
#     '[document]',
#     'noscript',
#     'html',
#     'meta',
#     'head',
#     'input',
#     'script',
#     'style',
#     'font',
#     'option'
# ]
#
# important_tags = [
#     'h1',
#     'h2',
#     'h3',
#     'h4',
#     'h5',
#     'h6',
#     'header',
#     'b',
#     'title',
#     'strong',
#     'em'
# ]
#
# urls_visited = set()
#
#
# # Function to build the index
# # Set docID to change the starting ID for the documents
# # noinspection PyTypeChecker
# def indexDocuments(docId):
#     startId = docId
#     numFiles = 0
#     path = pathlib.Path(json_dir)
#     # path = pathlib.Path(json_dir + str(docId))
#     totalStartTime = time.time()
#
#     for filename in path.rglob("*"):  # Look through all files and directories from a single path
#         numFiles += 1  # Keep track of the number of files
#         filename = str(filename)  # Get the string version of the file name
#
#         if filename.endswith(".json"):  # Check if the file is actually a JSON file
#             startTime = time.time()
#
#             # Read in the JSON data from the file
#             with open(filename, "r") as f:
#                 data = json.load(f)
#
#             # Extract the text from the JSON data
#             content = data["content"]
#
#             # TODO: Implement SimHash
#
#             # Defrag the URL and compare it with future URLs to see if there are the same links down the line
#             link = data['url']
#             link = urldefrag(link)
#             if link in urls_visited:
#                 continue
#             else:
#                 urls_visited.add(link)
#
#             soup = BeautifulSoup(content, 'html.parser')  # Parse the HTML content
#
#             # Tokenize the text and build the inverted index
#             for section in soup.find_all(text=True):  # Find all the text and their HTML tags in the file
#                 if section.parent.name not in blacklist:  # If the tag is in our blacklisted section, skip it
#                     text = section.string  # Get the text
#
#                     tokens = re.finditer(r'\b\w+\b',
#                                          text.lower())  # Changed to find iter so we can save position of match
#                     for tokenMatch in tokens:  # For every token that matched our regex expression
#                         token = ps.stem(tokenMatch.group())  # Stem the word to reduce repeated words
#
#                         if len(token) == 1: continue  # Don't save single letters and numbers
#
#                         if token not in index:
#                             index[token] = list()  # Initialize a new list of postings
#
#                         # Create posting that holds document information
#                         posting = Posting()
#                         posting.setId(docId)  # Set the posting's document ID
#                         posting.setPosition(tokenMatch.start())  # Save the position of the word in the
#                         posting.setImportantScore(section.parent.name)  # Save the tag the word is in
#                         index[token].append(posting)  # Append the posting to hte list
#
#             # Save the document to the index of documents and document IDs
#             with open(doc_index_file, 'a') as f:
#                 f.write(str(docId) + ';' + filename + '\n')
#             docId += 1
#
#             # For fun, print how long it took to complete the file
#             endTime = time.time()
#             print('Execution time for', filename, ': ', str(endTime - startTime))
#
#     # For fun, print how long it took to index the given documents
#     print('ran out of files to index through')
#     totalEndTime = time.time()
#     print('Total execution time:', str(totalEndTime - totalStartTime))
#
#     writeStartTime = time.time()  # For fun, start time
#     indexLength = len(index)  # For fun, get the current length of our index to see saving progress
#     tokenCount = 0  # For fun, get the number of tokens that need to be saved to show progress
#
#     index_index = dict()  # Create an index for our index
#     # if not pathlib.Path(index_file + str(startId)).exists(): pathlib.Path.mkdir(
#     #     index_file + str(startId))  # Create folder if it does not exist
#
#     project_path = pathlib.Path(project_dir) / (index_file + str(startId))
#     project_path.mkdir()
#
#     for token in sorted(index.keys()):  # For every token in our index
#         # Open both the associated index (where the postings are stored) and index of index (where the position of the posting list is) file
#         with open(index_file + str(startId) + '\\index' + token[0].upper() + '.txt', 'a', encoding='utf-8') as f, open(
#                 index_file + str(startId) + '\\index' + token[0].upper() + 'Index.txt', 'a', encoding='utf-8') as f2:
#             tokenCount += 1  # For fun, get the current token we are on
#             print('saving ' + token + ' to file ({0} / {1})'.format(tokenCount,
#                                                                     indexLength) + blank_space)  # Print the saving progress
#
#             # If the letter/number is NOT in the index of index, initialize it in the dict
#             if token[0].upper() not in index_index:
#                 index_index[token[0].upper()] = 0
#
#             # For fun, get the number of postings for progress
#             numPostings = len(index[token])
#             progress = 0
#
#             # Initialize the output we will be writing to file
#             # NOTE: The output of the posting is as follow:
#             # token docID,wordPosition,tag|docID,wordPosition,tag|docID,wordPosition,tag|...
#             output = token + ' '
#             for posting in index[token]:
#                 output += '{0},{1},{2}|'.format(str(posting.getId()), str(posting.getPosition()),
#                                                 str(posting.getImportantScore()))
#
#                 # For fun, output progress
#                 progress += 1
#                 print(token + ';' + str(progress) + '/' + str(numPostings) + blank_space, end='\r')
#
#             output = output[:-1] + '\n'
#             f.write(output)
#
#             f2.write(token + ':' + str(index_index[token[0].upper()]) + '\n')
#             index_index[token[0].upper()] = index_index[token[0].upper()] + len(output)
#             print('', end='\033[F')
#     print()
#
#     # For fun, output how long it took to save the index to a file
#     writeEndTime = time.time()
#     print('Time it took to write to file:', str(writeEndTime - writeStartTime))
#     print('====== END ======')
#
#
# # Returns the posting information from a word based on its info in the index file
# # noinspection PyShadowingNames
# def getWordPostingFromFile(startingWord):
#     output = dict()
#     startingWord = startingWord.lower()  # Set the word to be all lower case
#     startingLetter = startingWord[0].upper()  # Get the first letter of the starting word
#     postingList = list()
#     for indexNum in indexLimits:  # For the all index files we have
#         index_file2 = index_file + str(indexNum)
#         try:
#             # Open both the index file and the index of the index file
#             with open(index_file2 + '\\index' + startingLetter + '.txt', 'r', encoding='utf-8') as f, open(
#                     index_file2 + '\\index' + startingLetter + 'Index.txt', 'r', encoding='utf-8') as f2:
#                 if f is None or f2 is None: continue  # If the file doesn't exist, continue
#
#                 index_line = f2.readline()  # Read the line of the index of the index file
#                 limit = 0
#                 while index_line:  # While there is a line to read
#                     indexSplit = index_line.split(':')
#                     indexWord = indexSplit[0]
#                     indexPosition = int(indexSplit[1])  # Get the position of where the word starts in the index file
#                     # Temporary fix because index of index is wrong
#                     indexPosition += limit
#                     limit += 1
#                     # print(indexPosition)
#
#                     # Use this library to get the nearest similarity to the word
#                     if difflib.get_close_matches(startingWord, [indexWord], cutoff=0.85):
#                         f.seek(indexPosition)  # Get the position of the word in the index file
#                         postingLine = f.readline()  # Read where the word line is
#
#                         postingInfo = postingLine.split(' ')  # Split it so we have the word and its posting
#
#                         # Because special letters have a length greater than 1
#                         # We need to adjust the position so the seek is correct
#                         notABC = (char for char in postingInfo[0] if
#                                   char not in 'abcdefghijklmnopqrstuvwxyz0123456789|,\n-_\'')
#                         for char in notABC: limit += 1
#
#                         wordInfo = postingInfo[1].split('|')  # The postings are split with '|'
#                         for word in wordInfo:
#                             idAndPosition = word.split(',')  # The document ID and word position is split with ','
#                             if (
#                                     len(idAndPosition) != 3): continue  # Sometimes we get values that are not what we want, so skip them
#                             # Create and populate the postings
#                             posting = Posting()
#                             posting.setId(int(idAndPosition[0]))
#                             posting.setPosition(int(idAndPosition[1]))
#                             postingList.append(posting)
#                         break
#                     index_line = f2.readline()
#         except FileNotFoundError:
#             pass
#         except UnicodeDecodeError:
#             pass
#     output[startingWord] = postingList
#     return output
#
#
# # Calculate document frequencies from postings
# def getDocFrequencyFromPosting(postingDict):
#     output = dict()
#     for word, postings in postingDict.items():  # For the word and its postings
#         lastDocId = postings[0].getId()
#         docFreq = 0
#         docFreqList = list()
#         for posting in postings:  # For every posting in the list of postings
#             if lastDocId != posting.getId():  # If the docID changed, then we need to add up how many times its appeared
#                 docFreqList.append((lastDocId, docFreq))
#                 docFreq = 0
#             docFreq += 1
#             lastDocId = posting.getId()
#         docFreqList.append((lastDocId, docFreq))
#         output[word] = docFreqList
#     return output
#
#
# # Calculate intersecting points across two different lists
# # Based on the notes in class
# def intersect(list1, list2):
#     output = list()
#     list1 = enumerate(list1)
#     list2 = enumerate(list2)
#     elem1 = next(list1, None)
#     elem2 = next(list2, None)
#     while elem1 is not None and elem2 is not None:
#         if elem1[1][0] == elem2[1][0]:
#             output.append(elem1[1])
#             elem1 = next(list1, None)
#             elem2 = next(list2, None)
#         elif elem1[1][0] < elem2[1][0]:
#             elem1 = next(list1, None)
#         else:
#             elem2 = next(list2, None)
#     return output
#
#
# # Returns how many URLs were printed
# def printURLs(collection, limiter):
#     urls = set()
#     for freq in sorted(collection, key=lambda a: a[1], reverse=True):  # Sort list by value (by Doc Frequency)
#         if len(urls) == limiter: break
#         with open(doc_index_file, 'r') as f:
#             line = f.readline()
#             while line != '':  # Look through all the documents in the document to ID file
#                 lineParse = line.split(';')
#                 if freq[0] == int(lineParse[0]):
#                     with open(lineParse[1].strip('\n'), 'r') as f2:
#                         data = json.load(f2)
#                         link = data['url']
#                         defraggedURL = urldefrag(link)[0]  # Defrag the URL
#                         urls.add(defraggedURL)
#                 line = f.readline()
#     for url in urls:
#         results.add(url)
#         print(url)
#     return len(urls)
#
#
# def run_engine(query):
#     startTime = time.time()
#     test = list()
#     for word in query.split(' '):
#         word = ps.stem(word)
#         postingDict = getWordPostingFromFile(word)
#         postingFreq = getDocFrequencyFromPosting(postingDict)
#         test2 = list()
#         for freqList in postingFreq.values():
#             test2 += freqList
#         test.append(test2)
#     if len(test) == 1:
#         printURLs(test[0], 5)
#     else:
#         count = 1
#         compare = list()
#         while count < len(test):
#             if count > 1:
#                 compare = intersect(compare, test[count])
#             else:
#                 compare = intersect(test[0], test[1])
#             count += 1
#         limit = printURLs(compare, 5)
#         if limit < 5:
#             printURLs(test[0], 5 - limit)
#
#     endTime = time.time()
#     print("Query Time:", str((endTime - startTime) * 1000), 'ms')
#
# Write to the output file
# output = ''
# with open(output_file, 'w') as f:
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
# OLD INDEXER
# def saveIndexes(self):
    #
    #     # Save the final merged index to disk
    #     tokenCount = 0
    #     indexLength = len(self.index)
    #
    #     index_index = defaultdict(int)
    #
    #     project_path = pathlib.Path(self.project_dir) / (self.index_file + str(self.startId))
    #     project_path.mkdir()
    #
    #     writeStartTime = time.time()
    #
    #     for token in sorted(self.index.keys()):
    #         tokenCount += 1
    #         print('saving ' + token + ' to file ({0} / {1})'.format(tokenCount, indexLength) + self.blank_space)
    #
    #         with open(
    #             self.index_file + str(self.startId) + '\\index' + token[0].upper() + '.txt',
    #             'a', encoding='utf-8'
    #         ) as f, open(
    #             self.index_file + str(self.startId) + '\\index' + token[0].upper() + 'Index.txt',
    #             'a', encoding='utf-8'
    #         ) as f2:
    #             numPostings = len(self.index[token])
    #             progress = 0
    #
    #             output = token + ' '
    #             for posting in self.index[token]:
    #                 output += '{0},{1},{2}|'.format(
    #                     str(posting.getId()), str(posting.getPosition()), str(posting.getImportantScore())
    #                 )
    #
    #                 progress += 1
    #                 print(token + ';' + str(progress) + '/' + str(numPostings) + self.blank_space, end='\r')
    #
    #             output = output[:-1] + '\n'
    #             f.write(output)
    #
    #             f2.write(token + ':' + str(index_index[token[0].upper()]) + '\n')
    #             index_index[token[0].upper()] += len(output)
    #             print('', end='\033[F')
    #     print()
    #
    #     writeEndTime = time.time()
    #
    #     print('Time it took to write to file:', str(writeEndTime - writeStartTime))
    #     print('====== END ======')