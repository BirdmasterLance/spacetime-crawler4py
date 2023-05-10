import json
import os
import re

json_dir = "D:\PyCharm Community Edition 2023.1.1\crawler\TESTDEV"

index_file = "D:\PyCharm Community Edition 2023.1.1\crawler\indexer.txt"

index = {}

for root, dirs, files in os.walk(json_dir):
    for filename in files:
        if filename.endswith(".json"):
            # read in the JSON data from the file
            with open(os.path.join(root, filename), "r") as f:
                data = json.load(f)

            # extract the text from the JSON data
            text = data["content"]

            # tokenize the text and build the inverted index
            tokens = re.findall(r'\b\w+\b', text.lower())
            for token in tokens:
                if token not in index:
                    index[token] = set()
                index[token].add(filename)

# write the inverted index to the output file
with open(index_file, "w") as f:
    for token in index:
        f.write(token + " " + " ".join(index[token]) + "\n")

