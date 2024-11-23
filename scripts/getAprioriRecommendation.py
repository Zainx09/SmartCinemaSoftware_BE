from pymongo import MongoClient
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
from bson import ObjectId

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
watched_movies_collection = db['watched_movies']
movies_collection = db['moviesDB']

def generate_apriori_recommendations(user_id, min_support=0.1, min_confidence=0.5, top_n=5):
    """
    Generate movie recommendations using the Apriori algorithm.
    Args:
        user_id: ObjectId of the user for whom recommendations are being generated.
        min_support: Minimum support for frequent itemsets.
        min_confidence: Minimum confidence for association rules.
        top_n: Number of recommendations to return.

    Returns:
        List of recommended movie details.
    """

    # Step 1: Fetch watched movies for the given user
    user_data = watched_movies_collection.find_one({"user_id": ObjectId(user_id)})
    user_watched_movies = {movie["id"] for movie in user_data.get("watchList", [])} if user_data else set()

    # Step 2: Fetch watched movies for all users and filter only now_playing movies
    all_users_data = watched_movies_collection.find({})
    transactions = []
    now_playing_movie_ids = set(
        movie["id"] for movie in movies_collection.find({}, {"id": 1})
    )

    for user in all_users_data:
        user_movie_ids = {movie["id"] for movie in user.get("watchList", [])}
        transactions.append(list(user_movie_ids & now_playing_movie_ids))  # Only consider now_playing movies

    # If no valid transactions exist, return an empty list
    if not transactions:
        print("No valid transactions found.")
        return []

    # Step 3: Create a one-hot encoded DataFrame for Apriori
    all_movie_ids = sorted(now_playing_movie_ids)  # Sorted IDs for consistent columns
    one_hot_data = []

    for transaction in transactions:
        row = {movie_id: 1 if movie_id in transaction else 0 for movie_id in all_movie_ids}
        one_hot_data.append(row)

    df = pd.DataFrame(one_hot_data)

    # Step 4: Apply Apriori algorithm
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        print("No frequent itemsets found.")
        return []

    # Step 5: Generate association rules
    # rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence, 
                          num_itemsets=len(frequent_itemsets))
    if rules.empty:
        print("No association rules found.")
        return []

    # Step 6: Filter recommendations based on user's watched movies
    recommended_movie_ids = set()
    for _, rule in rules.iterrows():
        antecedents = set(rule["antecedents"])
        consequents = set(rule["consequents"])

        # Recommend movies in the consequents that the user hasn't watched
        if antecedents & user_watched_movies:
            recommended_movie_ids.update(consequents - user_watched_movies)

    # Limit recommendations to now_playing movies
    recommended_movie_ids = list(recommended_movie_ids & now_playing_movie_ids)[:top_n]

    # Step 7: Fetch and return movie details for recommendations
    recommended_movies = list(movies_collection.find({"id": {"$in": recommended_movie_ids}}))
    for movie in recommended_movies:
        movie["_id"] = str(movie["_id"])
    return recommended_movies