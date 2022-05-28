Assignment 3: M3 Instructions
Created by:
Jessica Sill
Alexander Rowlands
Patrick Xu
John Sun

How to run this program:
First you will need to generate your indexes. Run either the generate_index.py or search.py program, and make sure the DEV folder has the same parent directory as generate_index.py. 
This will build the indexes. these files are quite large, and can take some time to create, so patience is key.
Comment out line 157 in query_search if indexes have already been generated, as this line will cause indexes to generate again.
To change the number of files in each batch when generating indexes, modify the batch_size variable in generate_index.py.

Once the indexes are built, you can begin to search using the query_search.py file. Enter your query into the prompt and the results should appear in under 300 ms. The "and" keyword will count as a boolean search and be handled accordingly.
