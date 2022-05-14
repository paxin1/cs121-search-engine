import sys
from collections import defaultdict
import csv
import bisect
from nltk.stem import PorterStemmer
import generate_index as gi
import json

ps = PorterStemmer()
csv.field_size_limit(100000000)


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
    return top_five


#return a dict ->{url:freq}
#convert a list of string dicts into actually dictionary
def convert_string_dict(string):
    result_dict = defaultdict(int)
    temp = ""
    for char in string:
        if char == "}":
            temp += char
            if temp.find('\"\"') >= 0:
                temp = temp.replace("\"\"", '\"')
                temp = temp.replace("\'name\'", "\"name\"")
                temp = temp.replace("\'frequency\'", "\"frequency\"")
                temp = temp.replace("\'file\'", "\"file\"")
            else:
                temp = temp.replace("'", '"')
            temp_dict = json.loads(temp)
            result_dict[temp_dict["name"]] = temp_dict["frequency"];
            temp = ""
        elif char == "{":
            temp += char
        else:
            if "{" in temp:
                temp += char
    return result_dict

# returns the top 5 results in a list that match the query
def search_for(stemmed_queries, key_word = None):
    query_indexes = []
    query_len = len(stemmed_queries)
    #dictionary that stores frequencies of query and link => {url:freq}
    top_urls = defaultdict(int)
    #split input into inidividual terms and boolean
    query_indexes.append(key_word)
    #get indexes for each query term from frequencies csv
    indexes = defaultdict(list)
    data = open('frequencies.csv', "r")
    csv_reader = csv.reader(data, delimiter="|", quoting=csv.QUOTE_NONE)
    for query in stemmed_queries:
        data.seek(0)
        #check each row in the csv
        #find the matching query key word
        #add it to the top_urls dict
        for row in csv_reader:
            if query.lower() == row[0].lower():
                result = convert_string_dict(row[1])
                for k in result.keys():
                    top_urls[k] +=  result[k]
        #if not found:
                #query_indexes.append([query])
    query_indexes.extend([top_urls])
    #print(query_indexes)
    return get_top_five_of(query_indexes, query_len)


def main():
    while True:
        queries = input("Enter a query (q to quit): ")
        if queries == 'q':
            break

        #stem the query terms
        #print(queries)
        #stemmed_queries = [ps.stem(query) for query in queries]

        # stem the query terms
        k_word = None
        if "and" in queries.lower():
            split_queries = [ps.stem(query.strip().lower()) for query in queries.split("and")]
            stemmed_queries = []
            for split_query in split_queries:
                stemmed_queries.extend([ps.stem(query.strip().lower()) for query in split_query.split(" ")])
            k_word = "and"
            print(stemmed_queries)
        else:
            stemmed_queries = [ps.stem(query.strip().lower()) for query in queries.split(" ")]
        print(search_for(stemmed_queries, k_word))


if __name__ == "__main__":
    gi.main() #uncomment if need to initialize index
    main()
