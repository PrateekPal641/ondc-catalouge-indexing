import streamlit as st
import pandas as pd
import csv
from collections import defaultdict, Counter
import json
import logging 
import numpy as np
import logging
import sys

import pandas as pd
from llama_index.query_engine import PandasQueryEngine



# Function to prepare DataFrame
def prepare_dataframe():
    np.random.seed(0)  # For reproducible results

    # Define 7 different attributes for the catalogue
    attributes = {
        'ProductID': np.arange(1, 10001),
        'ProductName': np.random.choice([f"Product {i}" for i in range(1, 500)], size=10000),
        'Category': np.random.choice(['Electronics', 'Home & Kitchen', 'Fashion', 'Beauty & Personal Care', 'Toys & Games'], size=10000),
        'Price': np.random.uniform(10, 500, size=10000).round(2),
        'Rating': np.random.uniform(1, 5, size=10000).round(1),
        'Availability': np.random.choice(['In Stock', 'Out of Stock', 'Backorder'], size=10000),
        'ReleaseYear': np.random.randint(2015, 2023, size=10000)
    }

    # Create a DataFrame
    df = pd.DataFrame(attributes)

    # Save the DataFrame to a CSV file
    csv_file_path = 'catalog.csv'
    df.to_csv(csv_file_path, index=False)
    st.write("DataFrame created and saved as 'catalog.csv'")

# Function to build nested inverted index
def build_nested_inverted_index(csv_file_path):
    freq_list = []
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
    for i in range(0, 7):
        freq_list.append(features_sorted_by_frequency[i][0])
    
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

    return nested_index, freq_list


# Function to apply filters
def apply_filters(filters, inverted_index, freq_list):
    query = {}
    for key, value in filters.items():
        if key == 'Rating' or key == 'ReleaseYear':
            if value['condition'] == 'Below':
                query[key] = {'Below': str(value['value'])}
            elif value['condition'] == 'Above':
                query[key] = {'Above': str(value['value'])}
        else:
            query[key] = value
    print(query)
    filtered_rows = filter_by_attributes_with_numerical_conditions(inverted_index, query, freq_list)
    return filtered_rows

    
def filter_by_attributes_with_numerical_conditions(nested_index, query, freq_list):
    """
    Filters rows in the nested inverted index based on given attributes, including special handling for numerical
    features with conditions ('Above' or 'Below').

    :param nested_index: The nested inverted index.
    :param query: A dictionary with attribute names as keys. For numerical features, the value should be a dictionary
                  specifying 'Above' or 'Below' and the corresponding value.
    :param freq_list: A list of attribute names sorted by their frequency.
    :return: A list of rows that match the filtering criteria.
    """
    def is_match(value, condition):
        if isinstance(condition, dict):
            if 'Above' in condition and float(value) > float(condition['Above']):
                return True
            elif 'Below' in condition and float(value) < float(condition['Below']):
                return True
            return False
        else:
            return value == condition

    def filter_recursive(current_index, remaining_freq_list, current_query):
        if not remaining_freq_list or 'rows' in current_index:
            return current_index
        
        next_attribute = remaining_freq_list[0]
        if next_attribute in current_query:
            condition = current_query[next_attribute]
            if isinstance(condition, dict):
                # Handle numerical conditions by aggregating results that match the condition
                aggregated_results = []
                for value, sub_index in current_index.items():
                    if is_match(value, condition):
                        result = filter_recursive(sub_index, remaining_freq_list[1:], current_query)
                        if 'rows' in result:
                            aggregated_results.extend(result['rows'])
                        else:
                            aggregated_results.extend(result)
                return aggregated_results
            elif condition in current_index:
                # For categorical attributes, proceed as before
                return filter_recursive(current_index[condition], remaining_freq_list[1:], current_query)
            else:
                return []
        else:
            aggregated_results = []
            for value in current_index.keys():
                aggregated_results.extend(filter_recursive(current_index[value], remaining_freq_list[1:], current_query))
            return aggregated_results
    
    results = filter_recursive(nested_index, freq_list, query)
    if isinstance(results, dict) and 'rows' in results:
        return results['rows']
    else:
        return results
    
# Streamlit App
def main():
    st.title("Catalog INDEXING !!")
    tab1, tab2 = st.tabs(["Catalog Indexing", "CSV Operations"])
   
    with tab1:
        # Button to create DataFrame
        if 'data_generated' not in st.session_state or st.session_state['data_generated'] == False:
            st.session_state['data_generated'] = True
            prepare_dataframe()
            csv_file_path = 'catalog.csv'
            nested_inverted_index, freq_list = build_nested_inverted_index(csv_file_path)
            with open('inverted.json', 'w') as f:
                json.dump(nested_inverted_index, f)
            st.success("Inverted Index created and saved as 'inverted.json'")

        inverted_index = {}
        with open('inverted.json', 'r') as f:
            inverted_index = json.load(f)

        # Define filter options
        filter_options = {
            'Availability': sorted(['In Stock', 'Out of Stock', 'Backorder']),
            'Category': sorted(['Electronics', 'Home & Kitchen', 'Fashion', 'Beauty & Personal Care', 'Toys & Games']),
            'Rating': ['Below', 'Above'],
            'ReleaseYear': ['Below', 'Above']
        }

        # Sidebar for filters
        st.sidebar.title("Filters")
        filters = {}
        for key, values in filter_options.items():
            if key == 'Rating':
                condition = st.sidebar.selectbox(f"Select condition for {key}", ['Below', 'Above'])
                if condition:
                    value = st.sidebar.number_input(f"Enter value for {key}")
                    filters[key] = {'condition': condition, 'value': value}
            elif key == 'ReleaseYear':
                condition = st.sidebar.selectbox(f"Select condition for {key}", ['Below', 'Above'])
                if condition:
                    value = st.sidebar.number_input(f"Enter value for {key}", step=1)
                    filters[key] = {'condition': condition, 'value': value}
            else:
                value = st.sidebar.selectbox(f"Select {key}", values)
                filters[key] = value

        # Apply button
        if st.sidebar.button("Apply Filters"):
            with st.spinner("Applying Filters..."):
                freq_list = ['Availability', 'Category', 'ReleaseYear', 'Rating', 'ProductName' , 'Price ProductID']
                filtered_rows = apply_filters(filters, inverted_index, freq_list)
                if len(filtered_rows) == 0:
                    st.warning("No data found")
                else:
                    st.success("Filters Applied Successfully!")
                    # Read the original CSV file
                    original_df = pd.read_csv('catalog.csv')
                    # Fetch all data of filtered indexes
                    filtered_df = original_df.iloc[filtered_rows]
                    # Sort the data according to the index
                    filtered_df = filtered_df.sort_index()
                    # Display the DataFrame with horizontal and vertical scroll options
                    st.dataframe(filtered_df.style.set_properties(**{'max-width': '1000px', 'overflow-x': 'auto', 'overflow-y': 'auto'}))

    with tab2:
        st.subheader("Upload CSV and Execute Pandas Commands")
        # File uploader
        uploaded_file = st.file_uploader("Choose a CSV file", type='csv')
        if uploaded_file is not None:
            # Read the uploaded CSV file
            df = pd.read_csv(uploaded_file)
            st.write("CSV File Uploaded Successfully!")

            # Pandas Command Execution
            try:
                pandas_command = st.text_area("Write your Query here.....", height=150)
                if st.button("Execute Command"):
                    if pandas_command:
                        query_engine = PandasQueryEngine(df=df, verbose=True)
                        response = query_engine.query(
                            pandas_command,
                        )
                        st.write("Command Executed Successfully. See the results below:")
                        st.write(response.response)
                    else:
                        st.error("Please enter a valid command to execute.")
            except Exception as e:
                st.error(f"Error executing command: {e}")


if __name__ == "__main__":

    main()