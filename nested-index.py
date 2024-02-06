import csv
from collections import defaultdict, Counter
import json
def build_nested_inverted_index(csv_file_path):
    # Read the CSV file and collect all values for each feature
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        feature_values = defaultdict(list)
        for row in reader:
            for feature, value in row.items():
                feature_values[feature].append(value)
    
    # Count the frequency of each value for each feature
    feature_frequencies = {feature: Counter(values) for feature, values in feature_values.items()}
    
    # Sort features by their most common value's frequency (descending)
    features_sorted_by_frequency = sorted(feature_frequencies.items(), key=lambda x: x[1].most_common(1)[0][1], reverse=True)
    for i in range(0,7):

        print(features_sorted_by_frequency[i][0])
    # Initialize the nested inverted index
    nested_index = {}
    
    # Helper function to recursively build the nested index
    def add_to_index(nested_index, features, row):
        if not features:
            return
        feature, remaining_features = features[0], features[1:]
        value = row[feature[0]]
        if value not in nested_index:
            nested_index[value] = {}
        if remaining_features:
            add_to_index(nested_index[value], remaining_features, row)
        else:
            # Leaf node: List of unique identifiers or the full row data
            if 'rows' not in nested_index[value]:
                nested_index[value]['rows'] = []
            nested_index[value]['rows'].append(row)
    
    # Re-read the CSV and build the nested index
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            add_to_index(nested_index, features_sorted_by_frequency, row)
    
    return nested_index

# Example usage
csv_file_path = 'catalog.csv'
nested_inverted_index = build_nested_inverted_index(csv_file_path)
with open('inverted.json', 'w') as f:
    json.dump(nested_inverted_index, f)