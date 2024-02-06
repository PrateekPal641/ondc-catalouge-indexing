import pandas as pd
from time import time

def build_inverted_index(df, attributes_to_index):
    inverted_index = {}

    for attribute in attributes_to_index:
        for index, row in df.iterrows():
            value = str(row[attribute]).lower()
            words = value.split()

            for word in words:
                if word not in inverted_index:
                    inverted_index[word] = set()
                inverted_index[word].add(index)

    return inverted_index

def search_inverted_index(df, inverted_index, search_terms):
    matching_indices = set()

    for term in search_terms:
        term = term.lower()
        
        if term in inverted_index:
            if not matching_indices:
                matching_indices = inverted_index[term]
            else:
                matching_indices = matching_indices.intersection(inverted_index[term])

    matching_rows = df.loc[list(matching_indices)]
    return matching_rows

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("catalog.csv")

    attributes_to_index = ["Product_Name", "Color", "Category"]

    inverted_index = build_inverted_index(df, attributes_to_index)
    start_time = time()
    search_terms = ["red", "electronics"]

    results = search_inverted_index(df, inverted_index, search_terms)

    # Filter the rows to ensure all search terms are present
    for term in search_terms:
        term = term.lower()
        results = results[results.apply(lambda row: term in ' '.join(map(str, row.values)).lower(), axis=1)]
    end_time=time()
    print(results, end_time-start_time)
