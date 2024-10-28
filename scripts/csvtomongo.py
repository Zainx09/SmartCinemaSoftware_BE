import pandas as pd
from pymongo import MongoClient

# Step 1: Read the CSV file using pandas
csv_file = 'E:\\2nd Sem\\ADT\\Project\\DeskApp\\scripts\\movies_metadata.csv'
data = pd.read_csv(csv_file)

# Step 2: Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if needed
db = client['cinema_kiosk']  # Replace with your database name
collection = db['movies_DB']  # Replace with your collection name

# Step 3: Convert the DataFrame to a list of dictionaries
data_dict = data.to_dict('records')

# Step 4: Insert the data into the MongoDB collection
collection.insert_many(data_dict)

print("Data uploaded successfully!")
