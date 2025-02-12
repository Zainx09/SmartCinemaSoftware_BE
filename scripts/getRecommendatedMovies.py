import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
user_collection = db["users"]
movie_collection = db["moviesDB"]
watched_movie_collection = db["watched_movies"]

def fetch_movies_data():
    """Fetch now_playing movies from movieDB and return genres and movie IDs."""
    movies = list(movie_collection.find({}, {"id": 1, "genres": 1}))
    # print("Movies ---- \n")
    # print(movies , "\n")
    movie_ids = [movie["id"] for movie in movies]
    genres = [movie["genres"] for movie in movies]
    return movie_ids, genres

def build_user_movie_matrix(user_id):
    """Create a user-movie matrix based on watched movies."""
    # Get all movies and watched movies
    movie_ids, genres = fetch_movies_data()
    user_watched_obj = watched_movie_collection.find_one({"user_id": user_id})

    watched_movies = []
    print("Watched Movies ---- \n")

    if user_watched_obj:
        watched_movies = user_watched_obj.get('watchList', [])
    
    print(watched_movies , "\n")
    # return
    # Initialize user-movie matrix (binary: 1 if watched, 0 otherwise)
    user_movie_matrix = np.zeros(len(movie_ids))
    watched_movie_ids = [wm["id"] for wm in watched_movies]
    
    # Mark watched movies in user-movie matrix
    for idx, movie_id in enumerate(movie_ids):
        if movie_id in watched_movie_ids:
            user_movie_matrix[idx] = 1
    
    return user_movie_matrix, movie_ids, genres

def calculate_genre_similarity_matrix(genres):
    """Calculate cosine similarity between movies based on genre overlap."""
    # Convert genres list to binary matrix for cosine similarity
    unique_genres = sorted(set(g for genre_list in genres for g in genre_list))
    genre_matrix = np.zeros((len(genres), len(unique_genres)))
    
    for i, genre_list in enumerate(genres):
        for genre in genre_list:
            genre_matrix[i][unique_genres.index(genre)] = 1
    
    # Calculate cosine similarity matrix for movies based on genres
    similarity_matrix = cosine_similarity(genre_matrix)
    return similarity_matrix


def get_recommendations(user_id, k=10, min_similarity=0.2):
    """Generate movie recommendations for a given user using KNN with a minimum similarity threshold."""
    user_movie_matrix, movie_ids, genres = build_user_movie_matrix(user_id)
    similarity_matrix = calculate_genre_similarity_matrix(genres)
    
    # Find indices of watched movies
    watched_indices = np.where(user_movie_matrix == 1)[0]
    
    # Store recommendations
    recommended_movies = set()
    
    for idx in watched_indices:
        # Find similar movies for each watched movie
        similar_indices = np.argsort(-similarity_matrix[idx])  # Sort by descending similarity
        count = 0
        for similar_idx in similar_indices:
            # Break if recommended movie count reaches k
            if count >= k:
                break
            
            # Only recommend movies that the user hasn't watched and meet similarity threshold
            if (user_movie_matrix[similar_idx] == 0 and 
                similar_idx not in recommended_movies and 
                similarity_matrix[idx][similar_idx] >= min_similarity):
                
                recommended_movies.add(movie_ids[similar_idx])
                count += 1
    
    # Fetch recommended movies details
    recommended_movies_details = list(movie_collection.find({"id": {"$in": list(recommended_movies)}, "now_playing": True}))
    return recommended_movies_details

def main(userId=""):
    try:
        if userId is None or userId == "":
            print(userId)
            return
        # Convert user_id to ObjectId for MongoDB
        user_oid = ObjectId(userId)
        recommended_movies = get_recommendations(user_oid)
        recommended_movies_list = []
        if(recommended_movies):

            for movie in recommended_movies:
                recommended_movies_list.append(
                    {
                        "title": movie["title"],
                        "genres": movie["genres"],
                        "poster_path" : movie['poster_path'],
                        "overview" : movie['overview'],
                        "release_date" : movie['release_date'],
                        "runtime" : movie['runtime'],
                        "vote_average" : movie['vote_average'],
                        "id" : movie['id'],
                    })
    
        # print(recommended_movies_list)
        return(recommended_movies_list)
    except Exception as e:
        print("Error ---- " , e)
