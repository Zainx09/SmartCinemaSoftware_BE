from pymongo import MongoClient
import random
import sys
import codecs

# Set the output encoding to UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Step 1: Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if needed
db = client['cinema_kiosk']  # Replace with your database name
collection = db['movies_DB']  # Replace with your collection name

# Step 2: Get total count of movies
# total_movies = collection.count_documents({})

# Step 3: Pick 10-20 random movies
# n = random.randint(10, 20)  # Random number between 10 and 20
# random_movies = list(collection.aggregate([{'$sample': {'size': n}}]))  # Get random movie docs

# # Step 4: Update selected movies by setting "in_cinemas" to True
# for movie in random_movies:
#     collection.update_one(
#         {'_id': movie['_id']},  # Match by _id
#         {'$set': {'in_cinemas': True}}  # Set in_cinemas key to True
#     )

# print(f"{len(random_movies)} movies updated with 'in_cinemas': true")

# Step 5: Retrieve and print all movies where "in_cinemas" is True
movies_in_cinemas = list(collection.find({'in_cinemas': True}))

print("\n" , len(movies_in_cinemas) , "Movies (with 'in_cinemas': True):")
for movie in movies_in_cinemas:
    print(str(movie))
