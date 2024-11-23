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
