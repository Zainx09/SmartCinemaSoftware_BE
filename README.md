<h1 align="center">🎥 Cinema Kiosk Backend 🎥</h1>

<p align="center">
  This repository contains the backend implementation for the Cinema Kiosk System, built using Flask. The backend provides APIs to handle user authentication, movie recommendations, ticket booking, and data management. It integrates advanced algorithms like Collaborative Filtering, Apriori, and Review-Based Recommendations to enhance the user experience.
</p>

---

<h2>✨ Features</h2>

<h3>User Management</h3>
<ul>
  <li>Sign Up and Sign In with secure password hashing.</li>
  <li>User profile management.</li>
</ul>

<h3>Movie Recommendations</h3>
<ul>
  <li><strong>Collaborative Filtering:</strong> Recommends movies based on user similarity.</li>
  <li><strong>Apriori Algorithm:</strong> Suggests movies frequently watched together.</li>
  <li><strong>Review-Based Recommendations:</strong> Unique approach leveraging movie reviews for personalized suggestions.</li>
</ul>

<h3>Ticket Booking</h3>
<ul>
  <li>Fetch show details and seat availability.</li>
  <li>Book multiple seats for selected shows.</li>
  <li>Manage ticket bookings in real-time.</li>
</ul>

<h3>Favorites</h3>
<ul>
  <li>Add or remove movies from the user's favorite list.</li>
  <li>Fetch all favorite movies for a user.</li>
</ul>

<h3>Movie Data Management</h3>
<ul>
  <li>Manage "Now Playing" movies.</li>
  <li>Store and retrieve movie reviews using external APIs.</li>
</ul>

---

<h2>💻 Tech Stack</h2>
<ul>
  <li><strong>Language:</strong> Python</li>
  <li><strong>Framework:</strong> Flask</li>
  <li><strong>Database:</strong> MongoDB</li>
</ul>

<h3>Algorithms</h3>
<ul>
  <li>Collaborative Filtering</li>
  <li>Apriori</li>
  <li>Review-Based Recommendation</li>
</ul>

<h3>External API</h3>
<ul>
  <li><strong>TMDB:</strong> For fetching movie data and reviews.</li>
</ul>

---

<h2>⚙️ Setup Instructions</h2>

<h3>Prerequisites</h3>
<p>Ensure you have the following installed on your system:</p>
<ul>
  <li>Python (>=3.8)</li>
  <li>MongoDB</li>
  <li>Git</li>
</ul>

<h3>Installation Steps</h3>
<ol>
  <li>Clone the repository:
    <pre><code>git clone <repository-url>
cd cinema-kiosk-backend
    </code></pre>
  </li>
  <li>Create and activate a virtual environment:
    <pre><code>
# On Linux/Mac
python -m venv venv
source venv/bin/activate

# On Windows
venv\Scripts\activate
    </code></pre>
  </li>
  <li>Install dependencies:
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>Set up MongoDB:
    <ul>
      <li>Create a MongoDB database named <code>cinema_kiosk</code>.</li>
      <li>Add the required collections: <code>users</code>, <code>moviesDB</code>, <code>watched_movies</code>, <code>favMovies</code>, <code>movie_reviews</code>, and <code>shows_details</code>.</li>
    </ul>
  </li>
  <li>Create a <code>.env</code> file in the root directory and configure the following:
    <pre><code>
FLASK_APP=app.py
FLASK_ENV=development
MONGO_URI=mongodb://localhost:27017/cinema_kiosk
    </code></pre>
  </li>
  <li>Run the Flask app:
    <pre><code>flask run</code></pre>
    <p>The server will start at <code>http://127.0.0.1:5000/</code>.</p>
  </li>
</ol>

---

<h2>⚙️ How It Works</h2>

<h3>Recommendations</h3>
<ul>
  <li><strong>Collaborative Filtering:</strong> Finds users with similar preferences.</li>
  <li><strong>Apriori Algorithm:</strong> Identifies frequent patterns among watched movies.</li>
  <li><strong>Review-Based Recommendations:</strong> Analyzes textual reviews for similarity.</li>
</ul>

<h3>Ticket Booking</h3>
<ul>
  <li>Users can select shows and book seats.</li>
  <li>The backend updates seat availability in real-time.</li>
</ul>

<h3>MongoDB Integration</h3>
<p>MongoDB stores user data, movies, reviews, and ticketing details, ensuring a robust database structure for the system.</p>
