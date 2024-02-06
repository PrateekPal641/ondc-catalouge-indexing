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

def hash_term(term, hash_size):
    return hash(term) % hash_size

def build_hashed_inverted_index(df, attributes_to_index, hash_size=1000):
    hashed_inverted_index = {}

    for attribute in attributes_to_index:
        for index, row in df.iterrows():
            value = str(row[attribute]).lower()
            words = value.split()

            for word in words:
                hashed_index = hash_term(word, hash_size)
                if hashed_index not in hashed_inverted_index:
                    hashed_inverted_index[hashed_index] = set()
                hashed_inverted_index[hashed_index].add(index)

    return hashed_inverted_index

def search_hashed_inverted_index(df, hashed_inverted_index, search_terms, hash_size=1000):
    matching_indices = None

    for term in search_terms:
        term = term.lower()
        hashed_index = hash_term(term, hash_size)

        if hashed_index not in hashed_inverted_index:
            return pd.DataFrame()

        if matching_indices is None:
            matching_indices = hashed_inverted_index[hashed_index]
        else:
            matching_indices = matching_indices.intersection(hashed_inverted_index[hashed_index])

    matching_rows = df.loc[list(matching_indices)]
    return matching_rows

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("catalog.csv")

    attributes_to_index = ["Product_Name", "Color", "Category"]

    hashed_inverted_index = build_hashed_inverted_index(df, attributes_to_index)
    start_time = time()
    search_terms = ["red", "electronics"]

    results = search_hashed_inverted_index(df, hashed_inverted_index, search_terms)

    # Filter the rows to ensure all search terms are present
    for term in search_terms:
        term = term.lower()
        results = results[results.apply(lambda row: term in ' '.join(map(str, row.values)).lower(), axis=1)]
    end_time = time()
    print(results, end_time-start_time)
