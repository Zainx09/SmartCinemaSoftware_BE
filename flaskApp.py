from flask import Flask, jsonify, request
import cv2
import numpy as np
import face_recognition
import pymongo
from bson.binary import Binary
import pickle
from datetime import datetime
from flask_cors import CORS
import bcrypt
from bson import ObjectId
from werkzeug.security import check_password_hash
from scripts.getRecommendatedMovies import main  # Import main from your script
from scripts.getReviewRecommendation import generate_recommendations
from scripts.getAprioriRecommendation import generate_apriori_recommendations

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
user_collection = db["users"]
face_collection = db["faceSamples"]
movie_collection = db["moviesDB"]
show_details_collection = db['showsDetails']
watched_movie_collection = db["watched_movies"]
fav_movies_collection = db['favMovies']

# Global variable to store the user ID after sign-up
user_id = None

# Load OpenCV's face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Helper function to convert ObjectId fields to strings
def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        return {key: str(value) if isinstance(value, ObjectId) else value for key, value in data.items()}
    return data

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


@app.route('/signIn', methods=['POST'])
def sign_in():
    try:
        data = request.json  # Get JSON data from request body
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"status": None, "msg": "Email and password are required"}), 400

        # Find user by email
        user = user_collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            # User found and password is correct
            user_data = {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username"),
                "phone": user.get("phone")
            }
            return jsonify({"status": True, "userDetail": user_data})

        # User not found or incorrect password
        return jsonify({"status": None, "msg": "Wrong email or password"}), 401
    
    except Exception as e:
        return jsonify({"status": None, "msg": str(e)})

# Function to capture face samples and save them to MongoDB along with user data
@app.route('/signUp', methods=['POST'])
def detect_faces():
    # Extract user signup data from the request
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    # Capture face samples
    cap = cv2.VideoCapture(1)
    count = 0
    face_samples = []

    while count < 15:  # Capture 15 face samples
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_img, (100, 100))  # Resize for consistency
            face_samples.append(face_resized)
            count += 1
            if count >= 15:
                break

    cap.release()
    cv2.destroyAllWindows()

    # Check if the required number of face samples were captured
    if len(face_samples) < 15:
        return jsonify({"status": None, "msg":"Something went wrong!"}), 400



    # Hash the user's password
    hashed_password = hash_password(password)

    # Store the user details in the 'user' collection
    user_data = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'phone': phone,
        "created_at": datetime.now()
    }
    userDetail = {'username': username , 'email': email, "phone": phone}
    user_id = user_collection.insert_one(user_data).inserted_id  # Get user object ID after inserting into MongoDB

    user_data['id'] = str(user_id)
    # Serialize the face data and store in binary_samples
    binary_samples = []
    for face in face_samples:
        face_data = pickle.dumps(face)  # Serialize the face data
        binary_samples.append(Binary(face_data))

    # Save face samples to MongoDB using the binary data
    if binary_samples:
        face_collection.insert_one({
            'user_id': user_id,          # Store the user's ObjectId
            'face_samples': binary_samples
        })

    return jsonify({"status": True, "msg" : "Signup and face detection complete", "user_id": str(user_id), "userDetail":userDetail})


# Function to recognize a face from camera and compare with MongoDB samples
@app.route('/recognize', methods=['GET'])
def recognize_face():

     # Capture video from the first camera
    cap = cv2.VideoCapture(1)
    ret, frame = cap.read()
    if not ret:
        return jsonify({"status": None, "msg":"Failed to capture frame"})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    cap.release()
    cv2.destroyAllWindows()

    if len(faces) == 0:
        return jsonify({"status": None, "msg":"No face detected"})

    (x, y, w, h) = faces[0]  # Use the first detected face
    captured_face = gray[y:y+h, x:x+w]
    captured_face_resized = cv2.resize(captured_face, (100, 100))

    # Initialize variable to track the highest match percentage
    highest_match_percentage = 0
    userDetail = {}

    # Compare with samples stored in MongoDB
    for user in face_collection.find():
        user_face_samples = user["face_samples"]  # Get the list of face samples for the user
        userObjId = user["user_id"]

        userObjId = ObjectId(userObjId)

        for stored_face_binary in user_face_samples:
            stored_face = pickle.loads(stored_face_binary)  # Deserialize each stored face sample
            # Resize the stored face if necessary to match dimensions
            stored_face_resized = cv2.resize(stored_face, (100, 100))

            # Perform template matching
            match = cv2.matchTemplate(captured_face_resized, stored_face_resized, cv2.TM_CCOEFF_NORMED)
            match_percentage = np.max(match) * 100  # Convert to percentage

            # Check if match percentage is greater than 60
            if match_percentage > 60:
                # Query the user from the MongoDB collection
                user = user_collection.find_one({"_id": userObjId})
                # user = None

                if user:
                    # print(f"User found: {user['username']}, Email: {user['email']}")
                    userDetail = {'username':user['username'] , 'email':user['email'], "phone":user['phone'], "id": str(user["_id"])}
                    highest_match_percentage = match_percentage
                
                break  # Exit inner loop if a match is found

        # If a match was found, exit the outer loop as well
        if highest_match_percentage > 0:
            break

    if highest_match_percentage > 60:
        return jsonify({"status": True, "match_percentage": highest_match_percentage, "userDetail":userDetail})
    else:
        return jsonify({"status": None, "match_percentage": None})



@app.route('/get_nowPlaying_movies', methods=['GET'])
def get_nowPlaying_movies():
    try:
        # Query MongoDB to find all movies where 'in_cinemas' is True
        movies_in_cinemas = movie_collection.find({"now_playing": True})
        
        # Create a list of movies to return with all fields included
        movie_list = []
        for movie in movies_in_cinemas:
            # Convert ObjectId to string for JSON serialization
            # movie['_id'] = str(movie['_id'])
            # movie_list.append(movie)  # Include all fields of the movie
            movie_list.append({
                "genres" : movie.get('genres', 'N/A'),
                "imdb_id" : movie.get('imdb_id', 'N/A'),
                "title" : movie.get('title', 'N/A'),
                "poster_path" : movie.get('poster_path', 'N/A'),
                "overview" : movie.get('overview', 'N/A'),
                "release_date" : movie.get('release_date', 'N/A'),
                "runtime" : movie.get('runtime', 'N/A'),
                "vote_average" : movie.get('vote_average', 'N/A'),
                "id" : movie.get('id', 'N/A'),
            })

        return jsonify({"status": True, "data": movie_list})

    except Exception as e:
        return jsonify({"status": None, "msg": str(e)})
    




@app.route('/popularNowPlayingMovies', methods=['GET'])
def get_popular_now_playing_movies():
    try:
        # Query to find movies that are now playing, have a vote_average greater than 6,
        # and sort them in descending order based on vote_average
        popular_movies = list(movie_collection.find({
            "now_playing": True,
            "vote_average": {"$gt": 6}
        }).sort("vote_average", -1))  # Sort by vote_average in descending order

        movie_list = []
        for movie in popular_movies:
            # Append relevant fields to the movie list
            movie_list.append({
                "genres": movie.get('genres', 'N/A'),
                "imdb_id": movie.get('imdb_id', 'N/A'),
                "title": movie.get('title', 'N/A'),
                "poster_path": movie.get('poster_path', 'N/A'),
                "overview": movie.get('overview', 'N/A'),
                "release_date": movie.get('release_date', 'N/A'),
                "runtime": movie.get('runtime', 'N/A'),
                "vote_average": movie.get('vote_average', 'N/A'),
                "id": movie.get('id', 'N/A'),
            })

        # Return success response with the sorted popular movies data
        return jsonify({"status": True, "data": movie_list})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to fetch popular now_playing movies"}), 500





@app.route('/recommendedMovies', methods=['GET'])
def get_recommended_movies():
    try:
        userId = request.args.get('userId')

        if userId is None or userId == "":
            return jsonify({"status": None , "msg":'No User Found!'})
        
        # Call the main function from recommendation_script and wait for its response
        recommended_movies = main(userId)
        
        # Return success response with the recommended movies
        return jsonify({"status": True, "data": recommended_movies})
    
    except Exception as e:
        # Handle errors by returning a response with status None and error message
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to fetch recommended movies"}), 500





@app.route('/reviewRecommendedMovies', methods=['GET'])
def get_review_recommendations():
    try:
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({"status": None, "msg": "User ID is required"}), 400

        # Convert userId to ObjectId for MongoDB
        user_object_id = ObjectId(user_id)
        
        # Call the recommendation generation function
        recommended_movies = main(user_object_id)
        recommended_movies_id = []
        if(recommended_movies):
            # Using list comprehension
            recommended_movies_id = [item["id"] for item in recommended_movies]
        review_recommended_movies = generate_recommendations(user_object_id, recommended_movies_id)

        return jsonify({"status": True, "data": review_recommended_movies})
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to generate recommendations"}), 500
    



@app.route('/aprioriRecommendedMovies', methods=['GET'])
def recommend_by_apriori():
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({"status": None, "msg": "User ID is required"}), 400

        # Call Apriori recommendation function
        recommendations = generate_apriori_recommendations(user_id)

        if recommendations:
            return jsonify({"status": True, "data": recommendations})
        else:
            return jsonify({"status": None, "msg": "No recommendations found"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": None, "msg": "An error occurred"}), 500
    



@app.route('/getWatchedMovies', methods=['GET'])
def get_watched_movies():
    try:
        userId = request.args.get('userId')
        
        if userId is None or userId == "":
            return jsonify({"status": None, "msg": 'No User Found!'})

        # Convert user_id to ObjectId for MongoDB
        user_id = ObjectId(userId)

        # Retrieve the user's watched movies list
        user_watched_obj = watched_movie_collection.find_one({"user_id": user_id})

        # Initialize an empty list for movie details
        watched_movie_details = []

        if user_watched_obj:
            # Retrieve each movie ID from the watchList and fetch the full movie object
            for watch_item in user_watched_obj.get('watchList', []):
                movie_id = watch_item.get('id')
                
                # Fetch the movie object from moviesDB based on movie_id
                movie_obj = movie_collection.find_one({"id": movie_id})
                
                # If the movie object is found, add it to the list
                if movie_obj:
                    # Add watched date to the movie object
                    movie_obj["watched_on"] = watch_item.get("watched_on")
                    # Convert ObjectId fields in movie_obj to strings
                    movie_obj = convert_objectid_to_str(movie_obj)
                    watched_movie_details.append(movie_obj)

        # Return success response with the watched movie details
        return jsonify({"status": True, "data": watched_movie_details})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to fetch watched movies"}), 500
    

@app.route('/getFavoriteMovies', methods=['GET'])
def get_favorite_movies():
    try:
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({"status": None, "msg": "User ID is required"}), 400

        # Convert the userId to ObjectId
        user_object_id = ObjectId(user_id)
        
        # Find user's favorite movies in favMovies collection
        user_favorites = fav_movies_collection.find_one({"user_id": user_object_id})
        
        if not user_favorites:
            return jsonify({"status": True, "data": []})  # Return empty list if no favorites
        
        # Extract movie IDs from favList
        movie_ids = [fav['id'] for fav in user_favorites.get('favList', [])]
        
        # Fetch full movie details from moviesDB
        movies = list(movie_collection.find({"id": {"$in": movie_ids}}))
        
        # Convert ObjectId fields to strings for JSON serialization
        # for movie in movies:
        #     movie["_id"] = str(movie["_id"])

        movie_list = []
        for movie in movies:
            # Append relevant fields to the movie list
            movie_list.append({
                "genres": movie.get('genres', 'N/A'),
                "imdb_id": movie.get('imdb_id', 'N/A'),
                "title": movie.get('title', 'N/A'),
                "poster_path": movie.get('poster_path', 'N/A'),
                "overview": movie.get('overview', 'N/A'),
                "release_date": movie.get('release_date', 'N/A'),
                "runtime": movie.get('runtime', 'N/A'),
                "vote_average": movie.get('vote_average', 'N/A'),
                "id": movie.get('id', 'N/A'),
            })

        return jsonify({"status": True, "data": movie_list})
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to fetch favorite movies"}), 500


@app.route('/updateFavoriteMovie', methods=['POST'])
def update_favorite_movie():
    try:
        data = request.json
        user_id = data.get('userId')
        movie_id = int(data.get('movieId')) if data.get('movieId') else None
        remove = data.get('remove', False)

        if not user_id or not movie_id:
            return jsonify({"status": None, "msg": "User ID and Movie ID are required"}), 400

        # Convert userId to ObjectId for MongoDB
        user_object_id = ObjectId(user_id)

        # Determine action based on `remove` flag
        if remove:
            # Remove movie from user's favList
            result = fav_movies_collection.update_one(
                {"user_id": user_object_id},
                {"$pull": {"favList": {"id": movie_id}}}
            )
            if result.modified_count > 0:
                return jsonify({"status": True, "msg": "Movie removed from favorites"})
            else:
                return jsonify({"status": None, "msg": "Movie not found in favorites"}), 404
        else:
            # Check if the movie already exists in the user's favList
            existing_entry = fav_movies_collection.find_one(
                {"user_id": user_object_id, "favList.id": movie_id}
            )
            if existing_entry:
                return jsonify({"status": None, "msg": "Movie already in favorites"}), 409

            # Add movie to user's favList with the current date
            result = fav_movies_collection.update_one(
                {"user_id": user_object_id},
                {"$push": {"favList": {"id": movie_id, "fav_on": datetime.now()}}},
                upsert=True
            )
            return jsonify({"status": True, "msg": "Movie added to favorites"})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to update favorite movies"}), 500

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": None, "msg": "Failed to update favorite movies"}), 500
    
# GET API to fetch show details by movie id
@app.route('/getShowDetails', methods=['GET'])
def get_show_details():
    try:
        id = request.args.get('id')
        if not id:
            return jsonify({"status": None, "msg": "Movie ID is required"}), 400
        
        # Fetch show details from the collection
        show_data = show_details_collection.find_one({"id": int(id)})

        if show_data:
            # Return the show data excluding MongoDB's default _id field
            show_data['_id'] = str(show_data['_id'])
            return jsonify({"status": True, "data": show_data})
        
        return jsonify({"status": None, "msg": "No show details found for this movie"}), 404
    except Exception as e:
        return jsonify({"status": None, "msg": str(e)})

# POST API to book seats
@app.route('/bookSeats', methods=['POST'])
def book_seats():
    try:
        data = request.json
        id = data.get('id')
        show_datetime = data.get('show_datetime')
        booked_seats = data.get('booked_seats', [])

        if not id or not show_datetime or not booked_seats:
            return jsonify({"status": None, "msg": "id, show_datetime, and booked_seats are required"}), 400
        
        # Find the show details document by id
        show_data = show_details_collection.find_one({"id": int(id)})

        if not show_data:
            return jsonify({"status": None, "msg": "Show not found"}), 404

        # Find the show within the document that matches the specified datetime
        for show in show_data["shows"]:
            if show["datetime"] == show_datetime:
                # Add new booked seats to the existing list of booked seats
                show["booked_seats"] = list(set(show.get("booked_seats", []) + booked_seats))
                show["remaining_seats"] -= len(booked_seats)
                break
        else:
            return jsonify({"status": None, "msg": "Show with the specified datetime not found"}), 404

        # Update the document in the database
        show_details_collection.update_one(
            {"_id": ObjectId(show_data["_id"])},
            {"$set": {"shows": show_data["shows"]}}
        )

        return jsonify({"status": True, "msg": "Seats successfully booked!"})

    except Exception as e:
        return jsonify({"status": None, "msg": str(e)})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
