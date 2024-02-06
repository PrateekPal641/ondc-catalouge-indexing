import pandas as pd
import numpy as np

# Create a sample dataset for a real-world product catalogue
np.random.seed(0)  # For reproducible results

# Define 7 different attributes for the catalogue
attributes = {
    'ProductID': np.arange(1, 10001),
    'ProductName': np.random.choice([f"Product {i}" for i in range(1, 500)], size = 10000),
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

csv_file_path
