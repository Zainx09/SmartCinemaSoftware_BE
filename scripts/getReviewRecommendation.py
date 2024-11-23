import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
reviews_collection = db['movie_reviews']
watched_movies_collection = db['watched_movies']

def generate_recommendations(user_id, recommended_movies_id=[] , top_n=10):
    # Step 1: Fetch all watched movie IDs for the user
    user_watched_obj = watched_movies_collection.find_one({"user_id": user_id})
    watched_movie_ids = [movie['id'] for movie in user_watched_obj.get('watchList', [])] if user_watched_obj else []

    # print(watched_movie_ids)
    # Check if there are watched movies
    if not watched_movie_ids:
        print("No watched movies found for this user.")
        return []

    #merge with recommended Movies list
    watched_movie_ids = list(set(watched_movie_ids + recommended_movies_id))
    # print(watched_movie_ids)
    # Step 2: Fetch reviews for watched movies
    watched_reviews = []
    for movie_id in watched_movie_ids:
        movie_reviews = reviews_collection.find_one({"id": movie_id})
        if movie_reviews and movie_reviews.get('reviews'):
            watched_reviews.extend([review['content'] for review in movie_reviews['reviews']])

    # Step 3: Fetch reviews for all other movies (non-watched)
    other_reviews = []
    other_movie_ids = []
    other_movies = reviews_collection.find({"id": {"$nin": watched_movie_ids}})
    for movie in other_movies:
        if movie.get('reviews'):  # Ensure reviews list exists and is non-empty
            other_movie_ids.append(movie['id'])
            other_reviews.extend([review['content'] for review in movie['reviews']])

    # Check if we have enough reviews in both watched and other sets
    if not watched_reviews or not other_reviews:
        print("Insufficient data: either no watched movie reviews or no other movie reviews.")
        return []

    # Step 4: Combine watched and other reviews, and vectorize using TF-IDF
    all_reviews = watched_reviews + other_reviews
    vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
    review_vectors = vectorizer.fit_transform(all_reviews)

    # Validate vector lengths before slicing
    if review_vectors.shape[0] < len(watched_reviews) + len(other_reviews):
        print("Insufficient vectorization data.")
        return []

    # Step 5: Compute similarity between watched reviews and all other reviews
    watched_vectors = review_vectors[:len(watched_reviews)]
    other_vectors = review_vectors[len(watched_reviews):]
    similarity_matrix = cosine_similarity(watched_vectors, other_vectors)

    # Step 6: Identify top N recommended movies based on similarity scores
    if similarity_matrix.size == 0:
        print("Empty similarity matrix; no recommendations can be generated.")
        return []

    recommended_movie_indices = np.argsort(similarity_matrix.max(axis=0))[-top_n:]
    recommended_movie_ids = [other_movie_ids[i] for i in recommended_movie_indices if i < len(other_movie_ids)]

    # Step 7: Fetch movie details for recommended movie IDs
    recommended_movies = list(db['moviesDB'].find({"id": {"$in": recommended_movie_ids}, "now_playing":True}))

    # Convert ObjectId to string for JSON serialization
    for movie in recommended_movies:
        movie["_id"] = str(movie["_id"])  # Ensure ObjectId is converted to string

    return recommended_movies


