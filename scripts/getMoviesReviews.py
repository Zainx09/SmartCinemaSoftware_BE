import requests
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
movies_collection = db['moviesDB']
watched_movies_collection = db['watched_movies']
reviews_collection = db['movie_reviews']

# TMDB API details
base_url = "https://api.themoviedb.org/3/movie/{}/reviews"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4YzBmYTY2ODJkOWFiMTE5NzQ2N2ZjYzEzMzA0YjYwNSIsIm5iZiI6MTcyODU5MTg0OC41MjEwNTQsInN1YiI6IjY2ZmM2MTJlMDJlMmUzZmE0YWE2OGJjOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.M1fatXyQx3wYDuzJAtcskM7BnOgbeqDb6NOKn82OoME"
}

# Function to get reviews for a specific movie from TMDB API
def fetch_reviews(movie_id):
    try:
        response = requests.get(base_url.format(movie_id), headers=headers)
        if response.status_code == 200:
            # Extract only 'content' and 'id' fields from each review
            reviews_data = [{"content": review["content"], "id": review["id"]} for review in response.json().get("results", [])]
            return reviews_data
        else:
            print(f"Failed to fetch reviews for movie ID {movie_id}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching reviews for movie ID {movie_id}: {e}")
        return []

# Function to store movie reviews in MongoDB
def store_reviews(movie_id, reviews):
   if movie_id and isinstance(reviews, list) and len(reviews) > 0:
       review_doc = {
           "id": movie_id,
           "reviews": reviews
       }

       # Insert or update reviews in movie_reviews collection
       reviews_collection.update_one(
           {"id": movie_id},
           {"$set": review_doc},
           upsert=True
       )

# Function to process now_playing movies
def process_now_playing_movies():

    # result = reviews_collection.delete_many({"reviews": {"$size": 0}})
    # print(f"Deleted {result.deleted_count} documents with empty reviews.")
    # return
    now_playing_movies = movies_collection.find({"now_playing": True})

    for movie in now_playing_movies:
        movie_id = movie.get("id")
        if movie_id:
            # reviews = fetch_reviews(movie_id)
            # store_reviews(movie_id, reviews)
            reviews = fetch_reviews(movie_id)
            if isinstance(reviews, list) and len(reviews) > 0:
                store_reviews(movie_id, reviews)
                print(f"Stored reviews for now_playing movie ID {movie_id}")

# Function to process watched movies for each user
def process_watched_movies():
    # Get all users' watched movies from watched_movies collection
    all_users_watched = watched_movies_collection.find()

    for user in all_users_watched:
        watched_movies = user.get("watchList", [])
        
        for movie in watched_movies:
            movie_id = movie.get("id")
            if movie_id:
                reviews = fetch_reviews(movie_id)
                store_reviews(movie_id, reviews)
                print(f"Stored reviews for watched movie ID {movie_id}")

# Main function to run both processes
def main():
    process_now_playing_movies()
    # process_watched_movies()

# Run the script
if __name__ == "__main__":
    main()
