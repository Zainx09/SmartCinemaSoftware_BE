import cv2
import numpy as np
import face_recognition
import pymongo
import tkinter as tk
from tkinter import messagebox
import bcrypt
from datetime import datetime
import threading

# MongoDB setup
# Connect to local MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
users_collection = db["users"]
faces_collection = db["faces"]

# Global variable to store the user ID after sign-up
user_id = None

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# Function to handle user sign-up
def sign_up_user():
    global user_id  # Declare user_id as global

    username = entry_username.get()
    email = entry_email.get()
    password = entry_password.get()
    phone = entry_phone.get()

    if username and email and password and phone:
        # Hash the password before storing it
        hashed_password = hash_password(password)

        # Create the user document
        user = {
            "username": username,
            "email": email,
            "password": hashed_password,  # Store the hashed password
            "phone": phone,
            "created_at": datetime.now()
        }

        # Insert the user into the database and retrieve the inserted ID
        user_id = users_collection.insert_one(user).inserted_id
        messagebox.showinfo("Success", "User signed up successfully!")
        
        # Start face detection after successful sign-up
        start_detection()

    else:
        messagebox.showwarning("Input Error", "Please fill all fields!")

# Function to capture and process face samples in a background thread
def capture_face_samples():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    face_samples = []
    sample_count = 0

    frame_skip = 5  # Process every 5th frame
    frame_count = 0

    while sample_count < 15:
        ret, frame = video_capture.read()
        if not ret:
            break

        # # Resize frame to 1/4 size for faster processing
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # # Detect face locations and encode
        # face_locations = face_recognition.face_locations(rgb_frame)
        # if face_locations:
        #     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        #     # Only process the first detected face in each frame
        #     face_samples.append(face_encodings[0].tolist())
        #     sample_count += 1
        #     print(f"Sample {sample_count} collected.")  # Debugging

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

         # Skip frames to reduce processing load
        if frame_count % frame_skip == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if face_locations:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                for face_encoding in face_encodings:
                    face_samples.append(face_encoding.tolist())
                    sample_count += 1
                    print(f"Sample {sample_count} collected.")
        
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save face samples to MongoDB
    if face_samples and user_id:
        faces_collection.insert_one({'user_id': user_id, 'face_samples': face_samples})
        messagebox.showinfo("Detection", f"{sample_count} face samples collected and saved!")

    video_capture.release()
    cv2.destroyAllWindows()
    show_home_buttons()  

def check_camera_index():
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera index {i} is working.")
            cap.release()
    
    return


# def start_detection():
#     # Change the device index according to your connection method
#     # If using USB, it's usually 0 or 1
#     video_capture = cv2.VideoCapture(0)  # Use the camera index for your mobile device
#     face_samples = []
#     sample_count = 0

#     while sample_count < 15:
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         # Convert the frame from BGR to RGB
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Detect face locations
#         face_locations = face_recognition.face_locations(rgb_frame)

#         # If a face is detected, extract the face encoding
#         if face_locations:
#             face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#             # Collect face samples (up to 10 samples)
#             for face_encoding in face_encodings:
#                 face_samples.append(face_encoding.tolist())
#                 sample_count += 1
#                 print(f"Sample {sample_count} collected.")  # Debugging sample count

#         # Show the resulting image with the rectangle drawn
#         cv2.imshow("Face Detection", frame)

#         # Break the loop if the user presses 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Save collected face samples to MongoDB with user reference
#     if face_samples and user_id:
#         faces_collection.insert_one({'user_id': user_id, 'face_samples': face_samples})
#         messagebox.showinfo("Detection", f"{sample_count} face samples collected and saved!")

#     # Release the video capture object and close all windows
#     video_capture.release()
#     cv2.destroyAllWindows()
#     show_buttons()

# Function to start the face detection process in the background
def start_detection():
    
    # Display a "Processing" message on the screen
    messagebox.showinfo("Processing", "Collecting face samples...")

    # Start the face detection and collection in a background thread
    detection_thread = threading.Thread(target=capture_face_samples)
    detection_thread.start()



# Function to start face recognition
def start_recognition():
    samples = list(faces_collection.find())

    # Check if there are any face samples in the database
    if not samples:
        messagebox.showinfo("Recognition", "No face samples found. Please enroll your face first.")
        return

    video_capture = cv2.VideoCapture(0)
    found_match = False
    matching_percentage = 0
    matched_user_id = None
    matched_threshold = 1

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Convert the frame from BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop over each face detected in the video frame
        for face_encoding in face_encodings:
            all_checked = True  # Flag to track if all samples were checked

            # Iterate over each document (each object in MongoDB)
            for sample in samples:
                known_face_encodings = np.array(sample['face_samples'])

                # Check each stored face sample in the current MongoDB document
                for known_face_encoding in known_face_encodings:
                    # Compare the current detected face with known samples
                    face_distances = face_recognition.face_distance([known_face_encoding], face_encoding)
                    confidence = 1 - face_distances[0]  # Confidence level

                    if confidence >= matched_threshold:  # If confidence is above threshold
                        found_match = True
                        matching_percentage = confidence * 100
                        matched_user_id = sample['user_id']
                        break
                if found_match:
                    break  # Break the loop once a match is found
            if found_match:
                break  # Break the loop once a match is found

        # Break the loop if a match is found or if the user presses 'q'
        if found_match or (cv2.waitKey(1) & 0xFF == ord('q')):
            break

         # If all faces were checked and no match was found, stop the process
        if all_checked:
            break
    # If a match was found, fetch user details
    if found_match and matched_user_id:
        user = users_collection.find_one({"_id": matched_user_id})
        if user:
            user_details = f"User: {user['username']}, Email: {user['email']}"
            # messagebox.showinfo("User Matched", user_details)

            # Release the video capture object before re-opening
            video_capture.release()

            # Start recognition again to display matched face
            video_capture = cv2.VideoCapture(0)

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break

                # Display user details on the top left corner
                cv2.putText(frame, user_details, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Calculate the width of the user details text to position the percentage text accordingly
                (user_details_width, _), _ = cv2.getTextSize(user_details, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)

                # Display matching percentage next to user details
                percentage_text = f"{matching_percentage:.2f}%"
                cv2.putText(frame, percentage_text, (10 + user_details_width + 10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.imshow("Face Recognition", frame)

                # Break the loop if the user presses 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    # If no match was found after checking all frames
    else:
        messagebox.showinfo("Recognition", "Face not found in the database.")

    # Release the video capture object and close all windows
    video_capture.release()
    cv2.destroyAllWindows()

# Function to start face recognition
# def start_recognition():
#     samples = list(faces_collection.find())

#     # Check if there are any face samples in the database
#     if not samples:
#         messagebox.showinfo("Recognition", "No face samples found. Please enroll your face first.")
#         return

#     video_capture = cv2.VideoCapture(0)
#     found_match = False
#     matching_percentage = 0
#     matched_user_id = None

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         # Convert the frame from BGR to RGB
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Detect face locations and encodings in the current frame
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop over each face detected in the video frame
#         for face_encoding in face_encodings:
#             # Iterate over each document (each object in MongoDB)
#             for sample in samples:
#                 known_face_encodings = np.array(sample['face_samples'])

#                 # Check each stored face sample in the current MongoDB document
#                 for known_face_encoding in known_face_encodings:
#                     # Compare the current detected face with known samples
#                     face_distances = face_recognition.face_distance([known_face_encoding], face_encoding)
#                     confidence = 1 - face_distances[0]  # Confidence level

#                     if confidence >= 0.6:  # If confidence is above threshold
#                         found_match = True
#                         matching_percentage = confidence * 100
#                         matched_user_id = sample['user_id']
#                         break
#                 if found_match:
#                     break  # Break the loop once a match is found
#             if found_match:
#                 break  # Break the loop once a match is found

#         if found_match:
#             break  # Break the loop once a match is found

#         # Break the loop if the user presses 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     messagebox.showinfo(f"Percentage : {matching_percentage} ----- User ID : {matched_user_id}")
#     # If a match was found, fetch user details
#     if found_match and matched_user_id:
#         user = users_collection.find_one({"_id": matched_user_id})
#         if user:
#             messagebox.showinfo("User Matched", f"User: {user['username']}, Email: {user['email']}")
#         else:
#             messagebox.showinfo("User Not Found")
#     # If no match was found after checking all frames
#     else:
#         messagebox.showinfo("Recognition", "Face not found in the database.")

#     # Release the video capture object and close all windows
#     video_capture.release()
#     cv2.destroyAllWindows()



# Exit full-screen mode
def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

def show_home_buttons():
    hide_sign_up_fields()
    detection_button.pack(side=tk.BOTTOM, pady=20)
    recognition_button.pack(side=tk.BOTTOM, pady=20)

# Show sign-up fields when detection is clicked
def showSignUpFields():
    detection_button.pack_forget()
    recognition_button.pack_forget()

    label_username.pack()
    entry_username.pack()
    label_email.pack()
    entry_email.pack()
    label_password.pack()
    entry_password.pack()
    label_phone.pack()
    entry_phone.pack()

    # Button to sign up the user and back
    btn_sign_up.pack()
    btn_back.pack() 

def hide_sign_up_fields():
    label_username.pack_forget()
    entry_username.pack_forget()
    label_email.pack_forget()
    entry_email.pack_forget()
    label_password.pack_forget()
    entry_password.pack_forget()
    label_phone.pack_forget()
    entry_phone.pack_forget()
    btn_sign_up.pack_forget()
    btn_back.pack_forget()

# Set up the Tkinter window
root = tk.Tk()
root.attributes('-fullscreen', True)
root.bind("<Escape>", exit_fullscreen)

# Create buttons
detection_button = tk.Button(root, text="Sign Up and Detect", command=showSignUpFields)
# detection_button = tk.Button(root, text="Sign Up and Detect", command=start_detection)
recognition_button = tk.Button(root, text="Recognition", command=start_recognition)

#SignUp Fields
label_username = tk.Label(root, text="Username")
entry_username = tk.Entry(root)
label_email = tk.Label(root, text="Email")
entry_email = tk.Entry(root)
label_password = tk.Label(root, text="Password")
entry_password = tk.Entry(root, show='*')
label_phone = tk.Label(root, text="Phone")
entry_phone = tk.Entry(root)
btn_sign_up = tk.Button(root, text="Submit", command=sign_up_user)
btn_back = tk.Button(root, text="Back", command=show_home_buttons)

# Show buttons initially
show_home_buttons()
# detection_button.pack(side=tk.BOTTOM, pady=20)
# recognition_button.pack(side=tk.BOTTOM, pady=20)

# Start the Tkinter main loop
root.mainloop()