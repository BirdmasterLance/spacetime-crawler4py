import re
from urllib.parse import urlparse
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from sortedcontainers import SortedList, SortedSet, SortedDict

stopWords = list(stopwords.words('english'))

# Unique pages based on URLs only (not fragments)
uniquePages = set()
# The page that is longest, and its respective word count
longestPage = dict()
# The 50 most common words in the entire set of pages
commonWords = dict()
# The number of subdomains for ics.uci.edu
icsSubDomains = SortedDict()
# HTML information from the URLs we are downloading
# We are making this a global variable because we are not going to parse a URL twice
soup = None


def scraper(url, resp):
    links = extract_next_links(url, resp)

    # resp.raw_response can return None
    # That means there is nothing we can scrap from this page
    # So just return the links
    if(resp.raw_response is None): return [link for link in links if is_valid(link)]

    # Extracts the text from a given URL
    soupText = str(url) + '\n\n' + soup.get_text()
    length = len(soupText)
    # If a page is too long, we are not going to scrape it
    # Most pages do not exceed this many characters
    if(length > 100000):
        return [link for link in links if is_valid(link)]
    
    # Calculate the number of unique pages
    find_unique_pages(url)
    # Calculate the longest page in terms of words
    find_longest_page(url, soup)
    # Calculate the top 50 most common words
    find_common_words(soup)
    # Calculate all ICS subdomains
    find_ICS_subDomains(url, soup)

    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    output = list()

    match resp.status:
        case 200:
            pass
        case _:
            return output

    if(resp.raw_response is None): return output
    content = resp.raw_response.content
    if(content is None): return output

    global soup
    soup = BeautifulSoup(content, 'html.parser')

    for link in soup.find_all('a'):
        output.append(link.get('href'))

    return output

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # Compared the parsed result with a regular expression
        # We use parsed.netloc as that is the main domain of the URL
        # So if that matches our allowed URLs, it is good
        # The actual expression is r".*((\.ics\.uci\.edu)|(\.cs\.uci\.edu)|(\.informatics\.uci\.edu)|(\.stat\.uci\.edu)).*"
        if(re.match(
            r".*((\.ics\.uci\.edu)"
            + r"|(\.cs\.uci\.edu)"
            + r"|(\.informatics\.uci\.edu)"
            + r"|(\.stat\.uci\.edu)).*", parsed.netloc.lower())):

            # Part of the given code
            return not re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx)$", parsed.path.lower())
        

        # If the link was not valid,
        # return False
        return False

    except TypeError:
        print("TypeError for ", parsed)
        raise

        
# Calculate the number of unique pages, adding to the set if the URL is not already accounted for
def find_unique_pages(url):
    global uniquePages
    
    if url not in uniquePages:
        uniquePages.add(url)
    
    with open('uniquePages.txt', 'w') as file:
        file.write("The number of unique pages that have been found, solely based on URL: {}\n".format(len(uniquePages)))
        
        count = 1
        for URL in uniquePages:
            file.write("{}. {}\n".format(str(count), URL))
            file.write("\n")
            count += 1
        
        file.close()       
        
 
# Calculate the longest page in terms of words
def find_longest_page(url, info):
    global longestPage

    url = urlparse.urldefrag(url)   # removes the fragment from the url
    longest_length = 0    # variable for page's length
    total_words = []    # empty list that will hold all the words found on the page
    text = info.get_text(strip=True)    # returns the text as a single string
    total_words = re.findall("[a-zA-Z0-9]+", text)    # adds all the alphanumeric words from the page to the list
    longest_length = len(total_words)   # the length of the page
    for k, v in longestPage.items():
        if int(v) < longest_length and url not in longestPage:    # if the current url's page length is longer than what is being stored
            longestPage.clear()    # clear the dictionary since there can only be one entry
            longestPage[url] = longest_length    # add the new url as a key, and the length as its value
     
    with open('longestPage.txt', 'w') as file:
        file.write("The longest page and its length (in terms of word count): \n")
        
        for k, v in longestPage.items():
            file.write("URL: {} -> Word Count: {}".format(k, str(v)))
        
        file.write("\n")
        file.close()
        
        
def find_common_words(content):
    global commonWords
    totalWords = []

    for w in content.get_text(strip=True).split():
        if w.isnumeric() or (w.isalpha() and w.isupper() and len(w) > 1):
            totalWords.append(w)
        else:
            splitWords = re.findall('[A-Z][^A-Z]*', w)

        for w1 in splitWords:
            if w1.isnumeric():
                totalWords.append(w1)
            if len(w) > 1 and w.isalnum():
                totalWords.append(w1)

    for w2 in totalWords:
        if w2.lower() not in stopWords:
            if w2 not in commonWords:
                commonWords[w2] = 1
            else:
                commonWords[w2] += 1

    commonWords = sorted(commonWords.items(), key=lambda x: x[1], reverse=True)
    counter = 0

    with open("top50CommonWords.txt", "w") as f1:
        f1.write("Top 50 Common Words (ignoring stopwords): \n\n")

        for k, v in commonWords:
            if counter < 50:
                f1.write("'{}' : {}\n".format(k, str(v)))
                counter += 1

        f1.write("\nend")

    f1.close()
    

# Calculate ics.uci.edu subdomains
def find_ICS_subDomains(url, soup):

    # Check if the URL is actually a part of the ics.uci.edu domain
    if(re.match(r".*(\.ics\.uci\.edu).*", url)): # See if the URL regex matches for ics.uci.edu
        global icsSubDomains

        # When stopping the crawler and restarting it,
        # the list of icsSubDomains is reset,
        # so let's load it from a file
        if(len(icsSubDomains) == 0):
            with open('icsSubDomains.txt', 'r') as icsSubDomainsFile:
                lines = icsSubDomainsFile.readlines()
                if(len(lines) != 0): # if the file is empty, just skip adding anything into the dict
                    for line in lines:
                        lineSplit = line.split(', ') # Separate into URL and number of unique links
                        icsSubDomains[lineSplit[0]] = int(lineSplit[1])

        if(url not in icsSubDomains): # Add the number of links it has if not in the dict
            uniqueDomains = set() # Only get UNIQUE links (in case a site links to a page more than once)
            for domain in soup.find_all('a'): # Get all links
                uniqueDomains.add(domain) # Add them into the set
            icsSubDomains[url] = len(uniqueDomains)
        else: # Update the value if in dict
            uniqueDomains = set()
            for domain in soup.find_all('a'):
                uniqueDomains.add(domain)
            icsSubDomains[url] = icsSubDomains[url] + len(uniqueDomains)

        # For the Assignment, we're going to keep rewriting to the file
        # Since the order of URLs can change at any time
        with open('icsSubDomains.txt', 'w') as icsSubDomainsFile:
            fileText = ""
            for link in sorted(icsSubDomains.keys()):
                fileText += link + ', ' + str(icsSubDomains[link]) + '\n'
            icsSubDomainsFile.write(fileText)
