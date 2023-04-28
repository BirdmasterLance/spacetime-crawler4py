import re

# The time complexity is O(n), open = O(1) read = O(n) re.findall = O(n), O(1) + O(n) = O(n)
def tokenize(file_path):
    with open(file_path, encoding="utf_8") as f:
        text = f.read()

    tokens = re.findall(r'\b\w+\b', text.lower())

    return tokens


# The time complexity is O(n), all algorithms in the function are O(n) time
def computeWordFrequencies(tokens):
    word_counts = {}

    for token in tokens:
        if token not in word_counts:
            word_counts[token] = 1
        else:
            word_counts[token] += 1

    return word_counts


# The time complexity is O(n log(n)) because of the sorting algorithm used on the dict
def printTokens(frequency):
    for word, count in sorted(frequency.items(), key=lambda x: x[1], reverse=True):
        print(f'{word} => {count}')
