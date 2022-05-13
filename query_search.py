import sys
from collections import defaultdict
import csv
import bisect
from nltk.stem import PorterStemmer
import generate_index as gi
import json

ps = PorterStemmer()
csv.field_size_limit(100000000)


def get_top_five_of(indexes):
    #get modifier from first element in indexes
    modifier = indexes.pop(0)
    top_five = []

    #handle search with no booleans
    if modifier == 'none':
        term_indexes = indexes[0]
        for i in range(1, len(term_indexes)):
            if len(top_five) == 5:
                if top_five[-1]['frequency'] < term_indexes[i]['frequency']:
                    bisect.insort(top_five, term_indexes[i], key=lambda x: -x['frequency'])
                    del top_five[-1]
            else:
                bisect.insort(top_five, term_indexes[i], key=lambda x: -x['frequency'])

    #handle search with and boolean
    elif modifier == 'and':
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
                    if top_five[-1]['frequency'] < current_freq:
                        bisect.insort(top_five, {'name': docs[0], 'frequency': current_freq}, key=lambda x: -x['frequency'])
                        del top_five[-1]
                else:
                    bisect.insort(top_five, {'name': docs[0], 'frequency': current_freq}, key=lambda x: -x['frequency'])
                for term_indexes in indexes:
                    del term_indexes[1]

            #if doc urls different iterate lowest url
            else:
                min_list_pos = docs.index(min(docs))
                del indexes[min_list_pos][1]
    print('f')
    # return the top 5 or less results
    return top_five


# returns the top 5 results in a list that match the query
def search_for(input_string):
    query_indexes = []

    #split input into inidividual terms and boolean
    queries = [query.strip() for query in input_string.split("and")]
    queries = list(set(queries))
    if len(queries) > 1:
        query_indexes.append('and')
    else:
        query_indexes.append('none')

    #get indexes for each query term from frequencies csv
    indexes = defaultdict(list)
    data = open('frequencies.csv', "r")
    csv_reader = csv.reader(data, delimiter="|", quoting=csv.QUOTE_NONE)
    for query in queries:
        data.seek(0)
        found = False
        for row in csv_reader:
            if query == row[0]:
                #info = ''.join([column for column in row[1:]])
                indexes = list(eval(row[1]))
                query_indexes.append([query] + indexes)
                found = True
                break
        if not found:
            query_indexes.append([query])
    return get_top_five_of(query_indexes)


def main():
    while True:
        query = input("Enter a query (q to quit): ")
        if query == 'q':
            break
        # stem the query terms
        stemmed_query = ps.stem(query.lower())
        print(search_for(stemmed_query))


if __name__ == "__main__":
    #gi.main() #uncomment if need to initialize index
    main()
