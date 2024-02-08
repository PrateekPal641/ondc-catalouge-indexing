import logging
import sys

import pandas as pd
from llama_index.query_engine import PandasQueryEngine


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

df = pd.read_csv('catalog.csv')
query_engine = PandasQueryEngine(df=df, verbose=True)
response = query_engine.query(
    "How many products have rating greater than 3.6?",
)
print(f"<b>{response}</b>")