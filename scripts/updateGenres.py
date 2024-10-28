from pymongo import MongoClient

# Step 1: Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if needed
db = client['cinema_kiosk']  # Replace with your database name
collection = db['movies_DB']  # Replace with your collection name

# Step 2: Fetch all documents from the collection, except the first one
movies = list(collection.find())

if len(movies) > 1:
    for movie in movies[1:]:  # Skip the first document
        # Step 3: Check if 'genres' exists and is in a string format that can be evaluated
        if 'genres' in movie and isinstance(movie['genres'], str):
            try:
                # Convert the string representation of objects to a list of genre names
                genres_list = [genre['name'] for genre in eval(movie['genres'])]  # Extract only the genre names

                # Step 4: Update the document with the new plain list of genre names
                collection.update_one(
                    {'_id': movie['_id']},  # Match by _id
                    {'$set': {'genres': genres_list}}  # Set the updated genres field as a list
                )

                print(f"Document with _id: {movie['_id']} updated successfully! New genres: {genres_list}")
            except (SyntaxError, NameError, TypeError) as e:
                print(f"Error processing genres for document with _id: {movie['_id']}: {e}")
else:
    print("Not enough documents to update.")
