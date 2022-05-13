import collections
import os
import json
import re
import sys
import csv
import bisect
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from nltk.stem import PorterStemmer
import time

#directory = "D:\\APP_Downloads\\DEV" #directory path to recurse through
directory = "BRUH"

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

            url = data["url"]

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
                bisect.insort(frequencies[item[0]], {"name": url, "frequency": item[1]}, key=lambda x:x["name"])
    return file_count

#create a analytic report
def create_report(file_count):
    #write basic report numbers to file
    unique_tokens = len(frequencies)
    f = open('report.txt', 'w+')
    report_str = 'tokens: {}\ntotal_size: {}\nfile_count: {}\nword frequencies'.format(unique_tokens, sys.getsizeof(frequencies), file_count)
    f.write(report_str)
    f.close()


#write words and frequencies into a csv file
def create_csv_report():
    #write frequency dict to csv file for testing
    f = open('frequencies.csv', 'w+', newline='')
    csv_writer = csv.writer(f, delimiter='|')
    csv_writer.writerows(frequencies.items())
    f.close()

def main():
    count = process_directory()
    create_report(count)
    create_csv_report()

if __name__ == "__main__":
    #start = time.time()
    main()
    #end = time.time()
    #print("Elapsed time: " + (str)(end-start))
    #for writing to plain text file
    """
    f = open('frequencies.txt', 'w+')
    frequency_str = ''
    for k,v in frequencies.items():
        frequency_str += '{}={}\n'.format(k, v)
    f.write(frequency_str)
    f.close()
    """
