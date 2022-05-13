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
            #else:
                #bisect.insort(top_five, term_indexes[i], key=lambda x: -x['frequency'])

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
    # return the top 5 or less results
    return top_five

#convert a list of string dicts into actually dictionary
#return a dict ->{url:freq}
def convert_string_dict(string):
    result_dict = defaultdict(int)
    for char in row[1]:
        if char == "}":
            temp += char
            temp = temp.replace("'", '"')
            temp_dict = json.loads(temp)
            result_dict[temp_dict["url"]] += 1;
            temp = ""
        elif char == "{":
            temp += char
        else:
            if "{" in temp:
                temp += char
    return result_dict
# returns the top 5 results in a list that match the query
def search_for(input_string):
    query_indexes = []
    #dictionary that stores frequencies of query and link => {url:freq}
    top_urls = defaultdict(int)
    #split input into inidividual terms and boolean
    queries = [query.strip() for query in input_string.lower().split("and")]
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
        #check each row in the csv
        #find the matching query key word
        #add it to the top_urls dict
        for row in csv_reader:
            if query.lower() == row[0].lower():
                temp = convert_string_dict(row[1])
                top_urls.update(temp)
            break
        #if not found:
                #query_indexes.append([query])
    query_indexes.append([query]+ [top_urls])
    print(query_indexes)
    #for r in query_indexes:
        #print(r)
    return get_top_five_of(query_indexes)


def main():
    while True:
        queries = input("Enter a query (q to quit): ")
        if queries == 'q':
            break
        #stem the query terms
        print(queries)
        stemmed_queries = [ps.stem(query) for query in queries]
        print(search_for(stemmed_queries))


if __name__ == "__main__":
    #gi.main() #uncomment if need to initialize index
    main()
