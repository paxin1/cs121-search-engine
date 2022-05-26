import sys
from collections import defaultdict
import bisect
from nltk.stem import PorterStemmer
import generate_index as gi
import time
import re

ps = PorterStemmer()


def get_top_five_of(indexes, length):
    #get modifier from first element in indexes
    modifier = indexes.pop(0)
    top_five = []

    min_top_five = {'frequency': 0}

    sorted_dict_list = sorted(indexes[0].items(), key = lambda x:x[1], reverse = True)
    #handle search with no booleans
    if modifier is None:
        #term_indexes = indexes[0]
        
        #iterates through indexes and inserts current index in descending order by frequency
        #for i in range(1, len(term_indexes)):
            #removes lowest element if needed
            #if len(top_five) == 5:
                #if min_top_five['frequency'] < term_indexes[i]['frequency']:
                    #top_five.append(term_indexes[i]["url"])
                    #top_five.remove(min(top_five, key=lambda x: x['frequency']))
                    #min_top_five = min(top_five, key=lambda x: x['frequency'])
            #else:
                #top_five.append(term_indexes[i]["url"])
        count  =0
        for url in sorted_dict_list:
            if count == 5:
                break
            top_five.append(url)
            count += 1;
        
    #handle search with and boolean
    elif modifier == 'and':
        """ print(indexes)
        running = True
        while running:
            docs = []

            #generates list of first doc urls from each term's indexes
            for term_indexes in indexes:
                if len(term_indexes) < 2:
                    running = False
                else:
                    docs.append(term_indexes[1]['name'])
            if not running:
                break
            if len(docs) == 0:
                break
            #if all indexes on same url handle adding url index to top_five return list
            if all(x == docs[0] for x in docs):
                current_freq = sum([term_indexes[1]['frequency'] for term_indexes in indexes])
                if len(top_five) == 5:
                    if min_top_five['frequency'] < current_freq:
                        top_five.append({'name': docs[0], 'frequency': current_freq})
                        top_five.remove(min(top_five, key=lambda x: x['frequency']))
                        min_top_five = min(top_five, key=lambda x: x['frequency'])
                else:
                    top_five.append({'name': docs[0], 'frequency': current_freq})
                for term_indexes in indexes:
                    del term_indexes[1]

            #if doc urls different iterate lowest url
            else:
                min_list_pos = docs.index(min(docs))
                del indexes[min_list_pos][1] """
       
        count  =0
        close_match = length // 2
        for url in sorted_dict_list:
            if count == 5:
                break
            if url[1] >= length:
                top_five.append(url)
                count += 1; 
    # return the top 5 or less results
    return [url[0] for url in top_five]


def search_for(stemmed_queries, key_word=None):
    query_indexes = []
    query_len = len(stemmed_queries)
    # dictionary that stores frequencies of query and link => {url:freq}
    top_urls = defaultdict(int)
    # split input into inidividual terms and boolean
    query_indexes.append(key_word)
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
            # Seek to the location in frequencies.txt where the first character of the query first appears
            first_character_location = bookkeeper[query[0]]
            f.seek(first_character_location)
            # If an entry is found, add the results to the top_urls dict
            entry = f.readline().rpartition('=')
            while entry[0][0] == query[0]:
                if entry[0] == query:
                    # Result is a list of dicts with keys 'name' (representing url) and 'frequency'
                    result = list(eval(entry[1]))
                    for f_dict in result:
                        top_urls[f_dict['name']] += f_dict['frequency']
                entry = f.readline().rpartition('=')
    query_indexes.extend([top_urls])
    result = get_top_five_of(query_indexes, query_len)
    return result

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
        stemmed_queries = [ps.stem(query.strip().lower()) for query in re.split(' and | ', queries)]

        # print top 5 links
        start = time.time()
        [print(link)for link in search_for(stemmed_queries, k_word)]
        end = time.time()
        print("Elapsed time: " + (str)(end-start))


if __name__ == "__main__":
    #gi.main() #uncomment if need to initialize index
    main()
