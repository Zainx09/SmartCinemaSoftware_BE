import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
movies_collection = db['moviesDB']
watched_movies_collection = db['watched_movies']

# User object ID to add the watchlist for
# user_id = "671851c4fcc86bd7fdca568f"
user_id = ObjectId("67340e1831af83c3da467f26")

# Function to generate a random past date within the last year
def random_past_date():
    days_in_past = random.randint(1, 200)  # Random day within the past year
    return datetime.now() - timedelta(days=days_in_past)

# Get all movies with 'now_playing' = False or where 'now_playing' key does not exist
movies = list(movies_collection.find({"$or": [{"now_playing": False}, {"now_playing": {"$exists": False}}]}))

# Select 5-6 random movies from the filtered list
if len(movies) >= 5:  # Ensure there are enough movies to choose from
    selected_movies = random.sample(movies, random.randint(5, 6))

    # Prepare the watchlist
    watchList = [
        {
            "id": movie["id"],
            "watched_on": random_past_date()
        }
        for movie in selected_movies
    ]

    # Insert the watchlist into the watched_movies collection
    watched_movies_collection.insert_one({
        "user_id": user_id,
        "watchList": watchList
    })

    print("Watchlist successfully added for user.")
else:
    print("Not enough movies available to create a watchlist.")
