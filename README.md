Cinema Kiosk Backend

Overview
This repository contains the backend implementation for the Cinema Kiosk System, built using Flask. The backend provides APIs to handle user authentication, movie recommendations, ticket booking, and data management. It integrates advanced algorithms like Collaborative Filtering, Apriori, and Review-Based Recommendations to enhance user experience.

Features

1. User Management
Sign Up and Sign In with secure password hashing.
User profile management.

2. Movie Recommendations
Collaborative Filtering: Recommends movies based on user similarity.
Apriori Algorithm: Suggests movies frequently watched together.
Review-Based Recommendations: Unique approach leveraging movie reviews for personalized suggestions.

3. Ticket Booking
Fetch show details and seat availability.
Book multiple seats for selected shows.
Manage ticket bookings in real time.

4. Favorites
Add or remove movies from the user's favorite list.
Fetch all favorite movies for a user.

5. Movie Data Management
Manage "Now Playing" movies.
Store and retrieve movie reviews using external APIs.

Tech Stack
Language: Python
Framework: Flask
Database: MongoDB

Algorithms:
Collaborative Filtering
Apriori
Review-Based Recommendation

External API: TMDB for fetching movie data and reviews


Setup Instructions

1. Prerequisites
Ensure you have the following installed on your system:
Python (>=3.8)
MongoDB
Git

2. Installation Steps
Clone the repository:
bash
Copy code
git clone <repository-url>
cd cinema-kiosk-backend


Create and activate a virtual environment:
bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
bash
Copy code
pip install -r requirements.txt

Set up MongoDB:
Create a MongoDB database named cinema_kiosk.
Add the required collections: users, moviesDB, watched_movies, favMovies, movie_reviews, and shows_details.

Create a .env file in the root directory and configure the following:
makefile
Copy code
FLASK_APP=app.py
FLASK_ENV=development
MONGO_URI=mongodb://localhost:27017/cinema_kiosk

Run the Flask app:
bash
Copy code
flask run
The server will start at http://127.0.0.1:5000/.

How It Works
1. Recommendations
The backend generates personalized recommendations using:
    1. Collaborative Filtering: Finds users with similar preferences.
    2. Apriori Algorithm: Identifies frequent patterns among watched movies.
    3. Review-Based: Analyzes textual reviews for similarity.

2. Ticket Booking
Users can select shows and book seats.
The backend updates seat availability in real-time.

3. MongoDB Integration
MongoDB stores user data, movies, reviews, and ticketing details.