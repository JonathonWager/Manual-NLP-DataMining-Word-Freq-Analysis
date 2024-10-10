#4400H Assignment 1 Part 3
#Jonathon Wager
#10/4/2023

#All packages that where used in the application being imported
import nltk
import requests
import pandas as pd
from nltk.corpus import stopwords

#This string represents the base structure of the url that will be used to get all the documents
baseurl = "https://www.gutenberg.org/cache/epub/"

#selects the amount of books to grab
bookamount = 70000
#loop counter for the amount of documents
i=1
#list to store all book names
booknames = []
#list to store all the top 10 most frequent word dictonarys from each document
topTens = []

#getting stop words and puncuation to be omited when preprocessing data
stop_words = set(stopwords.words('english'))
punc = '''‘!()-—[]{};:'"\,<>.--/?@#$%^n't's&*n.''``_~”“’'''

#varible to store the line in which the document starts
firstline = 0

#varibles to keep track of wether or not a title and start have been found
titlefound = False
startfound = False

#all starts to documents happen between line 25 and 35
#max start search is to save time on incomplete documents that dont have offical start
maxStartSearch = 40

#the same as maxStartSearch but this is sstoring the max line going up a document the end should be on to be valid
maxEndSearch = 400

print("Getting texts and processing words")

#main loop for each document
while i <= bookamount:
    #simple % counter 
    print(str(round((i/bookamount)*100,2)) + "%")

    #reseting the title storage varible
    title = ""
    #line counter to know what line we are on in the document
    linecount = 0
    #storage varible for what line the start of document was found on
    firstline = 0

    #editing url to grab current document
    useurl = baseurl + str(i) +"/pg" + str(i) + ".txt"
    #using requests to get the document
    r = requests.get(useurl)
    #putting the text in a varible 
    book = r.text

    #splitting the received document by each line
    lines = book.splitlines()
    #looping through each line
    for line in lines:
        #case for if the document is not valid make sure we did not get a title before moving to next document
        if(maxStartSearch < linecount):
            if(titlefound == True):
                 booknames.pop()
                 titlefound = False
            break

        #if the line starts with TItle the this is the title line and we need to scrape the title
        if line.startswith("Title:"):
            #title found
            titlefound = True
            #get rid of unwanted title:
            title = line.replace('Title: ', '')
            #add title to list of titles
            booknames.append(title)

        #if the line starts with the following is is the start of the offical document    
        if "*** START OF THE PROJECT GUTENBERG EBOOK" in line:
            #found start
            startfound = True
            #saving the line in which we started on
            firstline = linecount
            #grabing all text after the start of the document
            startSplit = book.split("\n",linecount+1)[linecount+1]
            #break this loop to save time complexity
            break
            
        linecount += 1
    #reset line count
    linecount = 0

    #case for if current document is not valid format
    #omit if not valid
    if startfound == True and titlefound == True:
        #if valid format reset title and start found varibles
        titlefound = False
        startfound = False
        #looping through lines of document again from the bottem this time to save time complexity
        for line in reversed(lines):
            #if we cant find the end of the document break the loop
            if(linecount > maxEndSearch):
                break

            # if found the end of the project
            if "*** END OF THE PROJECT" in line:
                #get all text between current line and the line the start was found on
                text = startSplit.split("\n",len(startSplit.splitlines())-linecount)[:-firstline]
                string = ' '.join(text)

                #reseting word frequency dictionary for current document
                word_freq = {}

                #taking the document and tokenizing it in to its specific words
                tokens = nltk.word_tokenize(string)

                #loop each token and remove it if it is a stop word or punctuation
                for word in tokens:
                    if not word.lower() in stop_words:
                        if word not in punc:
                            #if not a stop word or punctuation
                            #add that word to the word frequency dictionary or if allready exists incriment that value
                            if(word in word_freq):
                                word_freq[word] += 1
                            else:
                                word_freq[word] = 1

                #after creating frequency dictionary for current document sort it so the most frequents are first
                word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1], reverse=True))
                #triming the dictionary to just contain top 10 entries
                word_freq = dict(list(word_freq.items())[0: 10])
                #add dictionary to list of dictionarys 
                topTens.append(word_freq)
                #break because we are done with this document 
                break
            linecount += 1


    #document incriment
    i += 1



print("Creating dataframe")
#creating data frame with the dictionarys and booknames as the index
df = pd.DataFrame(topTens, index=booknames)

#getting sum of the data frame so it displays most frequent words in the first column
s = df.sum()

#sorting values and trimming everything exept the top 10
df = df[s.sort_values(ascending=False).index[:10]]
pd.set_option('display.max_columns', None)

#printing to textfile for better readablilty
df.to_csv('data.txt', sep='\t', index=False)

#printing dataframe to console
print(df)

