import requests
from pymongo import MongoClient
import random

# MongoDB setup (replace with your MongoDB connection string)
client = MongoClient("mongodb://localhost:27017/")
db = client["cinema_kiosk"]  # Replace with your database name
movie_collection = db["moviesDB"]  # Replace with your collection name

# TMDB API URL
url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=10"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4YzBmYTY2ODJkOWFiMTE5NzQ2N2ZjYzEzMzA0YjYwNSIsIm5iZiI6MTcyODQ0NTIyMi4wNzAzNDcsInN1YiI6IjY2ZmM2MTJlMDJlMmUzZmE0YWE2OGJjOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nvxhFkm9d4bBTHB_Q2eZKgvBqcH7BzLa29IMWrR29iE"
}

# Genre decoding dictionary
genres_list = [ 
    {"id": 28, "name": "Action"},
    {"id": 12, "name": "Adventure"},
    {"id": 16, "name": "Animation"},
    {"id": 35, "name": "Comedy"},
    {"id": 80, "name": "Crime"},
    {"id": 99, "name": "Documentary"},
    {"id": 18, "name": "Drama"},
    {"id": 10751, "name": "Family"},
    {"id": 14, "name": "Fantasy"},
    {"id": 36, "name": "History"},
    {"id": 27, "name": "Horror"},
    {"id": 10402, "name": "Music"},
    {"id": 9648, "name": "Mystery"},
    {"id": 10749, "name": "Romance"},
    {"id": 878, "name": "Science Fiction"},
    {"id": 10770, "name": "TV Movie"},
    {"id": 53, "name": "Thriller"},
    {"id": 10752, "name": "War"},
    {"id": 37, "name": "Western"}
]

# Create a dictionary for fast lookup
genre_dict = {genre["id"]: genre["name"] for genre in genres_list}

# Make the API request to fetch now-playing movies
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Access the 'results' key which contains the list of movies
    movies = data.get('results', [])
    
    # Loop through each movie and add the "now_playing" key and "genres" list
    for movie in movies:
        movie["now_playing"] = True  # Add the "now_playing" key
        
        # Decode genre_ids into genre names and create a 'genres' list
        genre_ids = movie.get("genre_ids", [])
        movie["genres"] = [genre_dict[genre_id] for genre_id in genre_ids if genre_id in genre_dict]
        movie["runtime"] = random.randint(100, 130)
        # Insert the updated movie object into MongoDB
        # movie_collection.insert_one(movie)

        try:
            # print(movie)
            result = movie_collection.update_one(
                {"id": movie["id"]},  # filter/query to find existing movie
                {"$set": movie},      # update/insert data
                upsert=True           # create new document if not found
            )
            
            if result.upserted_id:
                print(f"Movie with ID {movie['id']} was inserted")
            else:
                print(f"Movie with ID {movie['id']} was updated")
                
        except Exception as e:
            print(f"Error: {e}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
