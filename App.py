import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk

import cv2
import numpy as np
import face_recognition
import pymongo
import bcrypt
from datetime import datetime
import threading 

# Global variable to store the user ID after sign-up
user_id = None

# Connect to local MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['cinema_kiosk']
users_collection = db["users"]
faces_collection = db["faces"]


# Modified sign-up function
def sign_up_user(username, email, password, phone, entry_password):
    global user_id  # Declare user_id as global

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
        
        # Go to the third screen and show user data
        app.show_third_screen()

        # Start face detection after successful sign-up
        # start_detection()

    else:
        messagebox.showwarning("Input Error", "Please fill all fields!")



# Function to hash the password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cinema Kiosk")
        self.root.geometry("800x600")  # Set window size
        # self.root.resizable(False, False)

        # Background image
        self.bg_image = Image.open("background.png")
        self.bg_image = self.bg_image.resize((800, 600), Image.Resampling.LANCZOS)  # Corrected the image resizing
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Initialize screen
        self.show_first_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


    # def show_first_screen(self):
    #     self.clear_screen()
    #     # Add background again after clearing
    #     self.bg_label = tk.Label(self.root, image=self.bg_photo)
    #     self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    #     # Create a card (Frame) with rounded corners
    #     card = tk.Frame(self.root, bg="white", width=600, height=200)
    #     card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    #     # Use canvas for rounded corners
    #     # self.create_rounded_rectangle(card)
    #      # Call update_idletasks to refresh the layout
    #     self.root.update_idletasks()

    #      # Add a label for the welcome message
    #     welcome_font = font.Font(family="Helvetica", size=16, weight="bold")
    #     label = tk.Label(card, text="Welcome Back!", bg="white", font=welcome_font)
    #     label.pack(padx=50,pady=10)

    #     # Add buttons
    #     explore_button = tk.Button(card, text="Start Explore", command=self.show_third_screen, bg="#007BFF", fg="white", width=20, padx=5, pady=5)
    #     explore_button.pack(pady=10)

    #     signup_button = tk.Button(card, text="Sign Up", command=self.show_second_screen, bg="white", fg="black", width=20, padx=5, pady=5, borderwidth=1, relief="solid")
    #     signup_button.pack(pady=10)


    def show_first_screen(self):
        self.clear_screen()
        # Make the window full-screen
        self.root.attributes("-fullscreen", True)

        # Add background image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Define background color to match the image (optional, depending on background image)
        bg_color = "#f0f0f0"  # Replace this with a color similar to your image's background if needed

        # Create a frame for the grid of cards on the left (80% of screen width)
        left_frame = tk.Frame(self.root, bg=bg_color, bd=0)  # Matching background color
        left_frame.grid(row=0, column=0, sticky="nsew")  # Full height, left side
        left_frame.grid_propagate(0)  # Prevent the frame from resizing to its content

        # Create a canvas for scrolling in the left frame
        canvas = tk.Canvas(left_frame, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)

        # Configure scrollable area
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate the grid with cards (20 cards)
        for i in range(20):
            card = tk.Frame(scrollable_frame, bg="white", width=150, height=200, bd=2, relief="groove")
            card.grid(row=i//4, column=i%4, padx=5, pady=5)  # 4 in a row
            card_label = tk.Label(card, text=f"Card {i+1}", bg="white")
            card_label.pack(pady=10)

        # Create a card (Frame) for the sign-up on the right (20% of screen width)
        right_frame = tk.Frame(self.root, bg=bg_color, bd=0)
        right_frame.grid(row=0, column=1, sticky="nsew")  # Right side, expand to full height

        # Add welcome label in the center of the right frame
        label = tk.Label(right_frame, text="Welcome Back!", font=('Helvetica', 16), bg="white")
        label.pack(pady=5)

        # Add buttons to the right frame
        explore_button = tk.Button(right_frame, text="Start Explore", command=self.show_third_screen, width=20, bg='blue', fg='white')
        explore_button.pack(pady=10)

        signup_button = tk.Button(right_frame, text="Sign Up", command=self.show_second_screen, width=20, bg='white', fg='black')
        signup_button.pack(pady=10)

        # Configure the layout to make sure it stretches to fill the entire screen
        self.root.grid_rowconfigure(0, weight=1)
        
        # Set column widths (80% left, 20% right)
        self.root.grid_columnconfigure(0, weight=8)  # 80% for the grid view
        self.root.grid_columnconfigure(1, weight=2)  # 20% for the right card section




    def show_second_screen(self):
        self.clear_screen()
        
        # Add background again after clearing
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a card for Sign Up
        card = tk.Frame(self.root, bg="white", width=700, height=300)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        #SignUp Fields
        self.label_username = tk.Label(card, text="Username")
        self.username_entry = tk.Entry(card)

        self.label_email = tk.Label(card, text="Email")
        self.email_entry = tk.Entry(card)

        self.label_password = tk.Label(card, text="Password")
        self.password_entry = tk.Entry(card, show='*')

        self.label_phone = tk.Label(card, text="Phone")
        self.contact_entry = tk.Entry(card)

        # self.btn_sign_up = tk.Button(card, text="Submit", command=self.collect_user_data)
        # Update Sign Up button to use the new `sign_up_user` function
        self.btn_sign_up = tk.Button(card, text="Submit", command=lambda: sign_up_user(
            self.username_entry.get(),
            self.email_entry.get(),
            self.password_entry.get(),
            self.contact_entry.get(),
            self.password_entry
        ))

        self.btn_back = tk.Button(card, text="Back", command=self.show_first_screen)

        self.label_username.pack(pady=5)
        self.username_entry.pack(pady=5)
        self.label_email.pack(pady=5)
        self.email_entry.pack(pady=5)
        self.label_password.pack(pady=5)
        self.password_entry.pack(pady=5)
        self.label_phone.pack(pady=5)
        self.contact_entry.pack(pady=5)

        # Buttons for sign up and back
        self.btn_sign_up.pack(pady=10)
        self.btn_back.pack(pady=10)

    def collect_user_data(self):
        # Store input values in variables
        self.username = self.username_entry.get()
        self.email = self.email_entry.get()
        self.password = self.password_entry.get()
        self.phone = self.contact_entry.get()

        # Go to third screen with user data
        self.show_third_screen()

    def show_third_screen(self):
        self.clear_screen()

        # Add background again after clearing
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a card for displaying user data
        card = tk.Frame(self.root, bg="white", width=700, height=300)
        card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        if(user_id):

            user = users_collection.find_one({"_id": user_id})

            if not user:
                label = tk.Label(card, text="No User Found!")
                label.pack(pady=10)
                return
            # Display the user data collected from the sign-up screen
            user_info = f"User: {user['username']}, Email: {user['email']}, User: {user['phone']}"
            label = tk.Label(card, text=user_info)
            label.pack(pady=10)
        

        self.btn_back = tk.Button(card, text="Back", command=self.show_first_screen)
        self.btn_back.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
