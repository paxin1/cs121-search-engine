import sys
from collections import defaultdict
import bisect
from nltk.stem import PorterStemmer
import generate_index as gi
import time
import re
import math
import os
import itertools

ps = PorterStemmer()


def get_top_five_of(stemmed_queries, indexes, intersection):
    mathed_entries = {}
    top_five = []

    #iterate through url keys
    for url in intersection:
        total_hits = 0
        for query in stemmed_queries:
            total_hits += indexes[query][url][0]
        for query in stemmed_queries:
            # the weight of the search result is calculated by how far it is from the center of the total weight. So 4 querys for each AND is weighted heigher than 9 for one and 1 for the other.
            try:    
                mathed_entries[url] = math.sin((indexes[query][url][0] / total_hits) * math.pi) * total_hits
            except ZeroDivisionError as e:
                mathed_entries[url] = 0
    sorted_dict_list = sorted(mathed_entries.items(), key = lambda x:x[1], reverse = True)
    count = 0
    for url, weight in sorted_dict_list:
        if count == 5:
            break
        top_five.append(url)
        count += 1
    return top_five

def search_for(stemmed_queries, key_word=None):
    query_indexes = defaultdict(list)
    query_len = len(stemmed_queries)
    # get indexes for each query term from frequencies txt
    indexes = defaultdict(list)

    # Load frequencies_bookkeeper.txt into a dictionary
    bookkeeper = defaultdict(int)

    with open('frequencies_bookkeeper.txt', 'r') as b:
        for line in b:
            line = line.rsplit('=')
            bookkeeper[line[0]] = int(line[1])

    # Find entry for the query in frequencies.txt
    with open('frequencies.txt', 'r') as f:
        split_queries = [query.split(' ') for query in stemmed_queries]
        query_words = list(itertools.chain(*split_queries))
        for query in query_words:
            # dictionary that stores frequencies of query and link => {url:freq} for this specific query
            top_urls = defaultdict(list)

            # Seek to the location in frequencies.txt where the first character of the query first appears
            first_character_location = bookkeeper[query[0]]
            f.seek(first_character_location)
            # If an entry is found, add the results to the top_urls dict
            entry = f.readline().split('=', maxsplit=1)
            while entry and entry[0][0] == query[0]:
                if entry[0] == query:
                    # Result is a list of dicts with keys 'name' (representing url) and 'frequency'
                    result = list(eval(entry[1]))
                    for f_dict in result:
                        try:
                            top_urls[f_dict['name']][0] += f_dict['tfidf']
                            top_urls[f_dict['name']][1].extend(f_dict['positions'])
                        except:
                            top_urls[f_dict['name']].append(f_dict['tfidf'])
                            top_urls[f_dict['name']].append(f_dict['positions'])
                    break
                entry = f.readline().split('=', 1)
                if not entry[0]:
                    break
                if is_after_query(query, entry[0]):
                    break
            query_indexes[query] = top_urls
    intersection = None

    for individual_query in stemmed_queries:

        #handle phrased queries with multiple words
        if len(individual_query.split(' ')) > 1:
            query_words = individual_query.split(' ')
            split_query_keys = [query_indexes[word].keys() for word in query_words]
            potential_keys = set.intersection(*map(set,split_query_keys))
            valid_keys = []
            full_query = defaultdict(list)

            #get positions and keys for each query word, then check if they are next to each other. append as valid key if so
            for key in potential_keys:
                word_positions = [query_indexes[word][key][1] for word in query_words]
                full_matches = 0
                for i in range(0, len(word_positions[0])):
                    valid = True
                    start_pos = word_positions[0][i]
                    for j in range(1, len(query_words)):
                        if start_pos+j in word_positions[j]:
                            continue
                        else:
                            valid = False
                            break
                    if valid:
                        full_matches += 1
                if full_matches > 0:
                    valid_keys.append(key)
                    full_query[key].append(full_matches)
            query_indexes[individual_query] = full_query
        
        #append all keys as valid if single worded phrase
        else:
            valid_keys = list(query_indexes[individual_query].keys())

        #get intersection of valid keys
        if intersection is None:
            intersection = valid_keys
        else:
            intersection = list(set(intersection) & set(valid_keys))
    result = get_top_five_of(stemmed_queries, query_indexes, intersection)
    return result

def is_after_query(query, entry):
    if len(entry) >= len(query):
        for i, c in enumerate(query):
            if ord(entry[i]) <= ord(c):
                return False
        return True
    return False

def main():
    while True:
        queries = input("Enter a query (q to quit): ")
        if queries == 'q':
            break

        # set keyword for search_for function
        k_word = None
        if " and " in queries.lower():
            k_word = "and"

        # stem and split the query terms
        stemmed_queries = [' '.join([ps.stem(word) for word in query.strip().lower().split()]) for query in re.split(' and ', queries.lower())]

        # print top 5 links
        start = time.time()
        [print(link)for link in search_for(stemmed_queries, k_word)]
        end = time.time()
        print("Elapsed time: " + (str)(end-start))

if __name__ == "__main__":
    gi.main() #uncomment if need to initialize index
    main()
