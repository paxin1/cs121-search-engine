import sys
from collections import defaultdict
import bisect
from nltk.stem import PorterStemmer
import generate_index as gi
import time
import re
import math

ps = PorterStemmer()


def get_top_five_of(indexes, intersection):
    mathed_entries = {}
    top_five = []
    for url in intersection:
        total_hits = 0
        for query in indexes:
            total_hits += indexes[query][url]
        for query in indexes:
            # the weight of the search result is calculated by how far it is from the center of the total weight. So 4 querys for each AND is weighted heigher than 9 for one and 1 for the other.
            mathed_entries[url] = math.sin((indexes[query][url] / total_hits) * math.pi) * total_hits
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
        for query in stemmed_queries:
            # dictionary that stores frequencies of query and link => {url:freq} for this specific query
            top_urls = defaultdict(int)

            # Seek to the location in frequencies.txt where the first character of the query first appears
            first_character_location = bookkeeper[query[0]]
            f.seek(first_character_location)
            # If an entry is found, add the results to the top_urls dict
            entry = f.readline().split('=', maxsplit=1)
            while entry[0][0] == query[0]:
                if entry[0] == query:
                    # Result is a list of dicts with keys 'name' (representing url) and 'frequency'
                    result = list(eval(entry[1]))
                    for f_dict in result:
                        top_urls[f_dict['name']] += f_dict['frequency']
                    break
                entry = f.readline().split('=', 1)
                if is_after_query(query, entry[0]):
                    break
            query_indexes[query] = top_urls
    #query_indexes.extend([top_urls])

    #result = get_top_five_of(query_indexes, query_len)
    #return result
    intersection = None
    for individual_query in query_indexes:
        if intersection is None:
            intersection = query_indexes[individual_query].keys()
        else:
            intersection = intersection & query_indexes[individual_query].keys()
    return get_top_five_of(query_indexes, intersection)

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
        stemmed_queries = [ps.stem(query.strip().lower()) for query in re.split(' and ', queries.lower())]

        # print top 5 links
        start = time.time()
        [print(link)for link in search_for(stemmed_queries, k_word)]
        end = time.time()
        print("Elapsed time: " + (str)(end-start))


if __name__ == "__main__":
    #gi.main() #uncomment if need to initialize index
    main()
