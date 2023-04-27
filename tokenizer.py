import builtins

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
                if(token.isalnum()): output.append(token) # Add token to output once we hit token's end
                token = ""
            c = file.read(1)
        if(token.isalnum()): output.append(token) # Add token to output once we hit token's end

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

