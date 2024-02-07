import json 
import os
freq_list = ['Availability', 'Category', 'ReleaseYear', 'Rating', 'ProductName' , 'Price ProductID']
search_query= {}


with open('inverted.json', 'r') as f:
    content = json.load(f)

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

# Example usage
query = {'Availability': 'In Stock', 'Category': 'Electronics', 'Rating': {'Below': '4.0'}, "ReleaseYear": {"Above":"2021"}}
filtered_rows = filter_by_attributes_with_numerical_conditions(content, query, freq_list)
print(filtered_rows)
