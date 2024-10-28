import tkinter as tk
from tkinter import messagebox
import bcrypt
import pymongo
from datetime import datetime

# Connect to local MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']

# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

# Function to handle user sign-up
def sign_up_user():
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

        # Insert the user into the database
        db.users.insert_one(user)
        messagebox.showinfo("Success", "User signed up successfully!")
    else:
        messagebox.showwarning("Input Error", "Please fill all fields!")

# Create Tkinter window
window = tk.Tk()
window.title("Sign-Up Screen")

# User input fields for sign-up
label_username = tk.Label(window, text="Username")
label_username.pack()
entry_username = tk.Entry(window)
entry_username.pack()

label_email = tk.Label(window, text="Email")
label_email.pack()
entry_email = tk.Entry(window)
entry_email.pack()

label_password = tk.Label(window, text="Password")
label_password.pack()
entry_password = tk.Entry(window, show='*')  # Mask password input
entry_password.pack()

label_phone = tk.Label(window, text="Phone")
label_phone.pack()
entry_phone = tk.Entry(window)
entry_phone.pack()

# Button to sign up the user
btn_sign_up = tk.Button(window, text="Sign Up", command=sign_up_user)
btn_sign_up.pack()

# Run the Tkinter event loop
window.mainloop()
