import sys
from collections import defaultdict
import csv
from nltk.stem import PorterStemmer

ps = PorterStemmer()
csv.field_size_limit(100000000)


def get_top_five_of(indexes):
    top_five = []
    while len(top_five) < 5 and len(indexes) > 0:
        # the maximum frquency and name in the current index
        max_freq = 0
        max_name = ""
        max_index = -1
        # loop through indexes to find the maximum
        for i in range(len(indexes)):
            if max_freq < indexes[i]['frequency']:
                max_freq = indexes[i]['frequency']
                max_name = indexes[i]['name']
                # maximum identified
                max_index = i
        # no max
        if max_freq == 0:
            break
        elif len(max_name) > 0 and max_index > -1:
            top_five.append({"name": max_name, "frequency": max_freq})
            # remove from indexes
            del indexes[max_index]
    # return the top 5 or less results
    return top_five


# returns the top 5 results in a list that match the query
def search_for(query):
    indexes = defaultdict(list)
    csv_reader = csv.reader(open('frequencies.csv', "r"), delimiter="|", quoting=csv.QUOTE_NONE)
    for row in csv_reader:
        if query == row[0]:
            #info = ''.join([column for column in row[1:]])
            indexes = list(eval(row[1]))
            break
    return get_top_five_of(indexes)


def main():
    while True:
        query = input("Enter a query (q to quit): ")
        if query == 'q':
            break
        # stem the query terms
        stemmed_query = ps.stem(query.lower())
        print(search_for(stemmed_query))


if __name__ == "__main__":
    main()
