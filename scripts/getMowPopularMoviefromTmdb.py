import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import random  # Import random to generate random runtime

# MongoDB setup (replace with your MongoDB connection string)
client = MongoClient("mongodb://localhost:27017/")
db = client["cinema_kiosk"]  # Replace with your database name
movie_collection = db["moviesDB"]  # Replace with your collection name

# TMDB API URL
url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=5"

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

# Define the cutoff date for determining "now_playing"
cutoff_date = datetime(2024, 9, 1)

# Get tomorrow's date by adding one day to the current date
tomorrow = datetime.now() + timedelta(days=1)

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
        # Parse the release date
        release_date_str = movie.get('release_date', '')
        try:
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid release date format for movie: {movie['title']}")
            continue  # Skip this movie if release date is invalid
        
        # Only mark movies as now_playing if the release date is after the cutoff
        if release_date and cutoff_date < release_date < tomorrow:
            movie["now_playing"] = True
        
        # Decode genre_ids into genre names and create a 'genres' list
        genre_ids = movie.get("genre_ids", [])
        movie["genres"] = [genre_dict[genre_id] for genre_id in genre_ids if genre_id in genre_dict]
        
        movie["runtime"] = random.randint(100, 130)
        
        # Insert the updated movie object into MongoDB
        movie_collection.insert_one(movie)

        print(f"Inserted movie: {movie['title']} with release date: {movie['release_date']} with now_playing: {movie.get('now_playing', 'N/A')}, runtime: {movie['runtime']} minutes")

else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
