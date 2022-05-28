import collections
import os
import json
import re
import sys
import csv
import math
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
from nltk.stem import PorterStemmer
import time


#directory = "DEV2\\aiclub_ics_uci_edu" #directory path to recurse through
directory = "DEV2"

batch_size = 500

file_count = 0

frequencies = defaultdict(list) #inverted index (word -> document posting)

document_word_count = defaultdict(int)

ps = PorterStemmer() #stemmer from nltk library

def process_directory():
    global file_count
    #recursively grabs all file names in target directory and sets global file_count
    file_names = []
    for root, dirs, files in os.walk(directory):
        file_names.extend([os.path.join(root, file) for file in files[0:len(files)]])
    file_count = len(file_names)

    #iterates through files in batches of batch_size # of files
    for x in range(0, -(len(file_names)//-batch_size)):
        current_batch = file_names[x*batch_size:(x+1)*batch_size]
        batch_frequencies = defaultdict(list)
        for file in current_batch:
            #load json data from joined file path
            #print(os.path.join(root, file))
            try:
                f = open(file)
                data = json.load(f)

                url = data["url"]

                #parse json content tags for tokens
                soup = BeautifulSoup(data["content"], features="html.parser")
                dup_tokens = re.findall('[a-zA-Z0-9]{1,}', soup.get_text())
                word_count = len(dup_tokens)
                document_word_count[url] = word_count
                bold_text = ""
                for tag in soup.find_all(['strong','b','h1','h2','h3','title']):
                    bold_text += tag.text + ' '
                bold_tokens = re.findall('[a-zA-Z0-9]{1,}', bold_text)

                #create frequency dict for tokens in current file
                cur_frequencies = {}

                #create position dict for tokens in current file
                word_positions = defaultdict(list)
            except Exception as e:
                continue
            #populate frequency dict using token list
            for i in range(0, len(dup_tokens)):
                # lowercase and stem tokens for better textual matches
                word = dup_tokens[i]
                stemmed_word = ps.stem(word.lower())
                word_positions[stemmed_word].append(i)
                try:
                    cur_frequencies[stemmed_word] += 1
                except:
                    cur_frequencies[stemmed_word] = 1

            #add extra frequency to bolded tokens to show importance
            for i in range(0, len(bold_tokens)):
                # lowercase and stem tokens for better textual matches
                word = bold_tokens[i]
                stemmed_word = ps.stem(word.lower())
                word_positions[stemmed_word].append(i)
                try:
                    cur_frequencies[stemmed_word] += 1
                except:
                    cur_frequencies[stemmed_word] = 1

    
            #add words and document postings to inverted index
            for item in cur_frequencies.items():
                batch_frequencies[item[0]].append({"name": url, "term_frequency": item[1]/word_count, "positions": word_positions[item[0]], 'tfidf': 0})
        
        #write batch postings to text file
        for item in batch_frequencies.items():
            batch_frequencies[item[0]] = [posting for posting in sorted(item[1], key=lambda x: x['name'])]
        freq_filename = 'frequencies{}-{}.txt'.format(x*batch_size+1,(x+1)*batch_size)
        with open(freq_filename, 'w+') as f:
            for k, v in sorted(batch_frequencies.items()):
                f.write('{}={}\n'.format(k, v))
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
    global file_count
    batch_files = []

    #open all batch frequency files
    for file in os.listdir("."):
        if re.match("^frequencies[0-9]+-[0-9]+.*$", file):
            batch_files.append(file)
    frequency_files = [open(file, 'r') for file in batch_files]
    current_lines = [f.readline() for f in frequency_files]

    #write to main frequency file
    with open('frequencies.txt', 'w+') as f:

        #loop through batch frequency files in order of current lowest term and write postings to main frequency file
        while frequency_files:
            min_term = min(current_lines, key=lambda x: x.split('=', maxsplit=1)[0]).split('=', maxsplit=1)[0]
            min_term_indexes = [current_lines.index(l) for l in current_lines if l.split('=', maxsplit=1)[0]==min_term]

            #combine multiple postings for same term and calculate tfidf
            if len(min_term_indexes) > 1:
                min_term_postings = [list(eval(current_lines[index].split('=', maxsplit=1)[1])) for index in min_term_indexes]
                combined_posting = []
                [combined_posting.extend(posting) for posting in min_term_postings]
                for posting in combined_posting:
                    tfidf = posting['term_frequency'] * math.log(file_count/(len(combined_posting)/document_word_count[posting['name']]+1))
                    posting['tfidf'] = tfidf
                f.write('{}={}\n'.format(min_term, sorted(combined_posting, key=lambda x: x['name'])))

            #write single posting for term and calculate tfidf
            else:
                min_term_posting = list(eval(current_lines[min_term_indexes[0]].split('=', maxsplit=1)[1]))
                for posting in min_term_posting:
                    tfidf = posting['term_frequency'] * math.log(file_count/(len(min_term_posting)/document_word_count[posting['name']]+1))
                    posting['tfidf'] = tfidf
                f.write(current_lines[min_term_indexes[0]])
            
            #retrieve files with no more lines
            to_close = []
            for min_term_index in min_term_indexes:
                line = frequency_files[min_term_index].readline()
                if not line:
                    to_close.append(min_term_index)
                else:
                    current_lines[min_term_index] = line
            
            #close and delete files with no more lines
            for index in sorted(to_close, reverse=True):
                frequency_files[index].close()
                del frequency_files[index]
                del current_lines[index]
        [os.remove(file) for file in batch_files]

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
    create_txt_report()
    create_txt_bookkeeper()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("Elapsed time: " + (str)(end-start))
