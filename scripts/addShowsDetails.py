import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']

movies_collection = db['moviesDB']
show_details_collection = db['showsDetails']

# Get all movies with now_playing = true
now_playing_movies = movies_collection.find({"now_playing": True})

# Parameters for generating random show data
num_shows = 20  # Number of shows per movie
capacity = 135  # Fixed capacity for each show
ticket_price_range = (10, 20)  # CAD dollars

# Generate random future date and time for each show
def generate_future_datetime():
    random_days = random.randint(10, 40)  # Up to 30 days in the future
    random_hours = random.randint(10, 22)  # Cinema hours (10 AM - 10 PM)
    date = datetime.now() + timedelta(days=random_days)
    date = date.replace(hour=random_hours, minute=0, second=0, microsecond=0)
    return date.isoformat()

# Insert show details for each movie
for movie in now_playing_movies:
    movie_id = movie['id']  # Get movie ID from moviesDB
    
    # Generate show details
    show_list = []
    for _ in range(num_shows):
        show = {
            "datetime": generate_future_datetime(),
            "capacity": capacity,
            "remaining_seats": capacity,
            "ticket_price": round(random.uniform(*ticket_price_range), 2)  # Random price in CAD
        }
        show_list.append(show)

    # Insert the movie's show details into the new collection
    show_details_collection.insert_one({
        "id": movie_id,
        "shows": show_list
    })

print("Show details added to showDetails collection.")
