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
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
user_collection = db["users"]
face_collection = db["faceSamples"]
movie_collection = db["moviesDB"]

# Global variable to store the user ID after sign-up
user_id = None

# Load OpenCV's face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

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
    user_id = user_collection.insert_one(user_data).inserted_id  # Get user object ID after inserting into MongoDB

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

    return jsonify({"status": True, "msg" : "Signup and face detection complete", "user_id": str(user_id), "samples_stored": len(face_samples)})

# @app.route('/signUp', methods=['GET'])
# def detect_faces():
#     cap = cv2.VideoCapture(0)
#     count = 0
#     face_samples = []

#     while count < 15:  # Capture 15 face samples
#         ret, frame = cap.read()
#         if not ret:
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 4)

#         for (x, y, w, h) in faces:
#             face_img = gray[y:y+h, x:x+w]
#             face_resized = cv2.resize(face_img, (100, 100))  # Resize for consistency
#             face_samples.append(face_resized)
#             count += 1
#             if count >= 15:
#                 break

#     cap.release()
#     cv2.destroyAllWindows()
    
#     # Serialize the face data and store in binary_samples
#     binary_samples = []
#     for face in face_samples:
#         face_data = pickle.dumps(face)  # Serialize the face data
#         binary_samples.append(Binary(face_data))

#     # Save face samples to MongoDB using the binary data
#     if binary_samples:
#         face_collection.insert_one({'face_samples': binary_samples})

#     return jsonify({"status": "Detection complete", "samples_stored": len(face_samples)})

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
                    userDetail = {'username':user['username'] , 'email':user['email'], "phone":user['phone']}
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

        return jsonify({"status": True, "movies": movie_list})

    except Exception as e:
        return jsonify({"status": None, "msg": str(e)})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
