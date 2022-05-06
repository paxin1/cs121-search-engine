import os
import json
import re
import sys
import csv
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from nltk.stem import PorterStemmer

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
            #lowercase and stem tokens for better textual matches
            dup_tokens = [ps.stem(token.lower()) for token in dup_tokens]

            #create frequency dict for tokens in current file
            cur_frequencies = {}
            for word in dup_tokens:
                
                try:
                    cur_frequencies[word] += 1
                except:
                    cur_frequencies[word] = 1

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


if __name__ == "__main__":
    count = process_directory()
    create_report(count)
    create_csv_report()


    #for writing to plain text file
    """
    f = open('frequencies.txt', 'w+')
    frequency_str = ''
    for k,v in frequencies.items():
        frequency_str += '{}={}\n'.format(k, v)
    f.write(frequency_str)
    f.close()
    """
