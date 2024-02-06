import json 
import os
freq_list = ['Availability', 'Category', 'ReleaseYear', 'Rating', 'ProductName' , 'Price ProductID']
search_query= {}

def filter_elements():
    return 

with open('inverted.json', 'r') as f:
    content = json.load(f)

def filter_by_attributes(nested_index, query, freq_list):
    """
    Filters rows in the nested inverted index based on given attributes.
    
    :param nested_index: The nested inverted index.
    :param query: A dictionary with attribute names as keys and desired attribute values as values.
    :param freq_list: A list of attribute names sorted by their frequency.
    :return: A list of rows that match the filtering criteria.
    """
    def filter_recursive(current_index, remaining_freq_list, current_query):
        # If we've processed all attributes in the freq_list or reached a leaf node, return the current index
        if not remaining_freq_list or 'rows' in current_index:
            return current_index
        
        next_attribute = remaining_freq_list[0]
        if next_attribute in current_query:
            # If the next attribute is in the query, dive into the corresponding value
            value = current_query[next_attribute]
            if value in current_index:
                return filter_recursive(current_index[value], remaining_freq_list[1:], current_query)
            else:
                # If the value is not present, return an empty result
                return []
        else:
            # If the next attribute is not in the query, we need to aggregate results across all possible values
            aggregated_results = []
            for value in current_index.keys():
                aggregated_results.extend(filter_recursive(current_index[value], remaining_freq_list[1:], current_query))
            return aggregated_results
    
    # Start the recursive filtering from the root of the nested index
    results = filter_recursive(nested_index, freq_list, query)
    
    # Extract rows from the final results
    if 'rows' in results:
        return results['rows']
    else:
        # If the final results are aggregated across multiple branches, return them directly
        return results

# Example usage
query = {'Availability': 'In Stock', 'Category': 'Electronics', 'Rating': '5.0'}
filtered_rows = filter_by_attributes(content, query, freq_list)
print(filtered_rows)



    