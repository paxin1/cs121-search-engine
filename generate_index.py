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


#directory = "DEV2\\aiclub_ics_uci_edu" #directory path to recurse through
directory = "D:\\APP_Downloads\\DEV"


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
            try:
                f = open(file_path)
                data = json.load(f)

                url = data["url"]
                #parse json content tag for tokens
                soup = BeautifulSoup(data["content"], features="html.parser")
                dup_tokens = re.findall('[a-zA-Z0-9]{1,}', soup.get_text())

                #create frequency dict for tokens in current file
                cur_frequencies = {}
            except Exception as e:
                continue
            for word in dup_tokens:
                # lowercase and stem tokens for better textual matches
                stemmed_word = ps.stem(word.lower())
                try:
                    cur_frequencies[stemmed_word] += 1
                except:
                    cur_frequencies[stemmed_word] = 1

    
            #add words and document postings to inverted index
            for item in cur_frequencies.items():
                frequencies[item[0]].append({"name": url, "frequency": item[1]})
    for item in frequencies.items():
        frequencies[item[0]] = [posting for posting in sorted(item[1], key=lambda x: x['name'])]
    return file_count

#create a analytic report
def create_report(f_count):
    #write basic report numbers to file
    unique_tokens = len(frequencies)
    f = open('report.txt', 'w+')
    report_str = 'tokens: {}\ntotal_size: {}\nfile_count: {}\nword frequencies'.format(unique_tokens, sys.getsizeof(frequencies), f_count)
    f.write(report_str)
    f.close()


#write words and frequencies into a csv file
def create_json_report():

    f  = open("frequencies.json", "w")
    json_object = json.dumps(frequencies, indent=4)
    f.write(json_object)

    f.close()

def create_csv_report():
    #write frequency dict to csv file for testing
    f = open('frequencies.csv', 'w+', newline='')
    csv_writer = csv.writer(f, delimiter='|')
    csv_writer.writerows(list(frequencies.items()))

def create_txt_report():
    with open('frequencies.txt', 'w+') as f:
        for k, v in sorted(frequencies.items()):
            f.write('{}={}\n'.format(k, v))

def create_txt_bookkeeper():
    current_character = ''
    with open('frequencies.txt', 'r') as f, open('frequencies_bookkeeper.txt', 'w+') as b:
        location = f.tell()
        line = f.readline()
        while line:
            if line[0] > current_character:
                current_character = line[0]
                b.write(current_character + '=' + str(location) + '\n')
            location = f.tell()
            line = f.readline()


def main():
    count = process_directory()
    create_report(count)
    #create_csv_report()
    create_txt_report()
    create_txt_bookkeeper()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Elapsed time: " + (str)(end-start))
