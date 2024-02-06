import pandas as pd
import mmh3  # MurmurHash3 library for hashing
from pybloom_live import BloomFilter  # Bloom filter library

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

def build_bloom_filter(df, attributes_to_index):
    bloom_filter = BloomFilter(capacity=100000, error_rate=0.001)  # Adjust capacity and error rate as needed

    for attribute in attributes_to_index:
        for _, row in df.iterrows():
            value = str(row[attribute]).lower()
            words = value.split()

            for word in words:
                bloom_filter.add(word)

    return bloom_filter

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

def is_term_probably_present(bloom_filter, term):
    term = term.lower()
    return term in bloom_filter

# Example usage:
if __name__ == "__main__":
    df = pd.read_csv("catalog.csv")

    attributes_to_index = ["Product_Name", "Color", "Category"]

    inverted_index = build_inverted_index(df, attributes_to_index)
    bloom_filter = build_bloom_filter(df, attributes_to_index)

    search_terms = ["red", "electronics"]

    results = []

    for term in search_terms:
        if is_term_probably_present(bloom_filter, term):
            results.extend(list(search_inverted_index(df, inverted_index, [term])))

    # Filter the rows to ensure all search terms are present
    for term in search_terms:
        term = term.lower()
        results = [row for row in results if term in ' '.join(map(str, row)).lower()]
    print(results)
