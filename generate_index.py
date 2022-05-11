import collections
import os
import json
import re
import sys
import csv
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from nltk.stem import PorterStemmer
import time

directory = "D:\\APP_Downloads\\DEV" #directory path to recurse through

frequencies = defaultdict(list) #inverted index (word -> document posting)

ps = PorterStemmer() #stemmer from nltk library

#recursively iterate through all files in given directory
def process_directory():
    file_count = 0
    for root, dirs, files in os.walk(directory):

        for file in files:
            file_count += 1

            #load json data from joined file path
            file_path = os.path.join(root, file)
            #print(os.path.join(root, file))
            f = open(file_path)
            data = json.load(f)

            #parse json content tag for tokens
            soup = BeautifulSoup(data["content"], features="html.parser")
            dup_tokens = re.findall('[a-zA-Z0-9]{1,}', soup.get_text())

            #create frequency dict for tokens in current file
            cur_frequencies = {}
            for word in dup_tokens:
                # lowercase and stem tokens for better textual matches
                stemmed_word = ps.stem(word.lower())
                try:
                    cur_frequencies[stemmed_word] += 1
                except:
                    cur_frequencies[stemmed_word] = 1

            #add words and document postings to inverted index
            for item in cur_frequencies.items():
                frequencies[item[0]].append({"name": file, "frequency": item[1]})
    return file_count


def create_report(file_count):
    #write basic report numbers to file
    unique_tokens = len(frequencies)
    f = open('report.txt', 'w+')
    report_str = 'tokens: {}\ntotal_size: {}\nfile_count: {}\nword frequencies'.format(unique_tokens, sys.getsizeof(frequencies), file_count)
    f.write(report_str)
    f.close()


def create_csv_report():
    #write frequency dict to csv file for testing
    f = open('frequencies.csv', 'w+', newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerows(frequencies.items())
    f.close()

def get_top_five_of(indexes):
    top_five = []
    while(len(top_five) < 5 and len(indexes) > 0):
        #the maximum frquency and name in the current index
        max_freq = 0
        max_name = ""
        max_index = -1
        #loop through indexes to find the maximum
        for i in range(len(indexes)):
            if max_freq < indexes[i]['frequency']:
                max_freq = indexes[i]['frequency']
                max_name = indexes[i]['name']
                #maximum identified
                max_index = i
        #no max
        if(max_freq == 0):
            break
        elif(len(max_name) > 0 and max_index > -1):
            top_five.append({"name": max_name, "frequency": max_freq})
            #remove from indexes
            del indexes[max_index]
    #return the top 5 or less results
    return top_five

#returns the top 5 results in a list that match the query
def search_for(query):
    indexes = defaultdict(list)
    for item in frequencies.items():
        #query match
        if query == item[0]:
            indexes = item[1]
            break
    return get_top_five_of(indexes)

if __name__ == "__main__":
    start = time.time()
    count = process_directory()
    create_report(count)
    create_csv_report()
    end = time.time()
    print("Elapsed time: " + (str)(end-start))
    #for writing to plain text file
    """
    f = open('frequencies.txt', 'w+')
    frequency_str = ''
    for k,v in frequencies.items():
        frequency_str += '{}={}\n'.format(k, v)
    f.write(frequency_str)
    f.close()
    """
