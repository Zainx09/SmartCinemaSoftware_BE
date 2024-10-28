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
    """Fetch movies from movieDB and return genres and movie IDs."""
    movies = list(movie_collection.find({}, {"id": 1, "genres": 1}))
    print("Movies ---- \n")
    print(movies , "\n")
    movie_ids = [movie["id"] for movie in movies]
    genres = [movie["genres"] for movie in movies]
    return movie_ids, genres

def build_user_movie_matrix(user_id):
    """Create a user-movie matrix based on watched movies."""
    # Get all movies and watched movies
    movie_ids, genres = fetch_movies_data()
    watched_movies = list(watched_movie_collection.find({"user_id": user_id}, {"movie_id": 1}))

    print("Watched Movies ---- \n")
    print(watched_movies , "\n")
    # Initialize user-movie matrix (binary: 1 if watched, 0 otherwise)
    user_movie_matrix = np.zeros(len(movie_ids))
    watched_movie_ids = [wm["movie_id"] for wm in watched_movies]
    
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

def get_recommendations(user_id, k=5):
    """Generate movie recommendations for a given user using KNN."""
    user_movie_matrix, movie_ids, genres = build_user_movie_matrix(user_id)
    similarity_matrix = calculate_genre_similarity_matrix(genres)
    
    # Find indices of watched movies
    watched_indices = np.where(user_movie_matrix == 1)[0]
    
    # Store recommendations
    recommended_movies = set()
    
    for idx in watched_indices:
        # Find k most similar movies for each watched movie
        similar_indices = np.argsort(-similarity_matrix[idx])  # Sort by descending similarity
        count = 0
        for similar_idx in similar_indices:
            if count >= k:
                break
            # Only recommend movies that the user hasn't watched
            if user_movie_matrix[similar_idx] == 0 and similar_idx not in recommended_movies:
                recommended_movies.add(movie_ids[similar_idx])
                count += 1
    
    # Fetch recommended movies details
    recommended_movies_details = list(movie_collection.find({"id": {"$in": list(recommended_movies)}}))
    return recommended_movies_details



try:
    # Convert user_id to ObjectId for MongoDB
    user_oid = ObjectId("671851c4fcc86bd7fdca568f")
    recommended_movies = get_recommendations(user_oid)
    
    # Format the recommended movies for the response
    recommended_movies_list = [
        {
            "title": movie["title"],
            "genres": movie["genres"],
            # "poster_path": movie["poster_path"],
            # "release_date": movie["release_date"],
            # "runtime": movie["runtime"],
            # "vote_average": movie["vote_average"]
        }
        for movie in recommended_movies
    ]
 
    print(recommended_movies_list)
except Exception as e:
    print("Error ---- " , e)

# Flask API to get recommended movies for a user
# from flask import Flask, jsonify

# app = Flask(__name__)

# @app.route('/user/<user_id>/recommended_movies', methods=['GET'])
# def recommend_movies(user_id):
#     try:
#         # Convert user_id to ObjectId for MongoDB
#         user_oid = ObjectId("671851c4fcc86bd7fdca568f")
#         recommended_movies = get_recommendations(user_oid)
        
#         # Format the recommended movies for the response
#         recommended_movies_list = [
#             {
#                 "title": movie["title"],
#                 "genres": movie["genres"],
#                 "poster_path": movie["poster_path"],
#                 "release_date": movie["release_date"],
#                 "runtime": movie["runtime"],
#                 "vote_average": movie["vote_average"]
#             }
#             for movie in recommended_movies
#         ]
        
#         return jsonify({
#             "status": "success",
#             "recommended_movies": recommended_movies_list
#         })
    
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
