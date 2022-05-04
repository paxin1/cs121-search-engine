import os
import json
import re
import sys
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict

directory = "DEV\\aiclub_ics_uci_edu" #directory path to recurse through

frequencies = defaultdict(list) #inverted index (word -> document posting)
file_count = 0

if __name__ == "__main__":

    #recursively iterate through all files in given directory
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
            dup_tokens = [token.lower() for token in dup_tokens]

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


    #write basic report numbers to file
    unique_tokens = len(frequencies)
    f = open('report.txt', 'w+')
    report_str = 'tokens: {}\ntotal_size: {}\nfile_count: {}'.format(unique_tokens, sys.getsizeof(frequencies), file_count)
    f.write(report_str)
    f.close()

    #write frequency dict to file for testing
    f = open('frequencies.txt', 'w+')
    frequency_str = ''
    for k,v in frequencies.items():
        frequency_str += '{}={}\n'.format(k, v)
    f.write(frequency_str)
    f.close()