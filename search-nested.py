import json 
import os
freq_list = ['Availability', 'Category', 'ReleaseYear', 'Rating', 'ProductName' , 'Price ProductID']
search_query= {}

def filter_elements():
    return 

with open('inverted.json', 'r') as f:
    content = json.load(f)
print(content.keys())


    