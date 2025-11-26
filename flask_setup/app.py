from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# load the variables from the .env file 
load_dotenv()

def create_app():
    app = Flask(__name__)

    # basic database settings (taken from .env or the default values)
    app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost") # set this in .env
    app.config["DB_USER"] = os.getenv("DB_USER", "YOUR USERNAME") # set this in .env
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "YOUR PASSWORD") # set this in env
    app.config["DB_NAME"] = os.getenv("DB_NAME", "db_project") # set this in env 

    # helper function to open a connection to MySQL
    def get_db_connection():
        try:
            conn = mysql.connector.connect(
                host=app.config["DB_HOST"],
                user=app.config["DB_USER"],
                password=app.config["DB_PASSWORD"],
                database=app.config["DB_NAME"]
            )
            return conn
        except Error as e:
            # just print the error so I can see what went wrong
            print("MySQL error:", e)
            return None

    # default route; something to show that the API works
    @app.route("/")
    def index():
        return """
        <h1>Spotify Database Flask API</h1>
        <p>Server is running. Try these endpoints:</p>
        <ul>
            <li><a href='/ping'>/ping</a></li>
            <li><a href='/genres'>/genres</a></li>
            <li><a href='/artists'>/artists</a></li>
            <li><a href='/albums'>/albums</a></li>
            <li><a href='/tracks'>/tracks</a></li>
            <li><a href='/audiofeatures'>/audiofeatures</a></li>
            <li><a href='/users'>/users</a></li>
        </ul>
        """

    # simple test route
    @app.route("/ping")
    def ping():
        return {"message": "Flask is running!"}

    # route to show some of the genres from the database
    @app.route("/genres")
    def get_genres():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        # using dictionary=True so we get JSON-friendly column names
        cursor = conn.cursor(dictionary=True)

        # just selecting a few rows to test the query
        cursor.execute("SELECT genre_id, parent_genre, genre_name FROM Genres LIMIT 10;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(rows)
    
    # Artists API Route 
    @app.route("/artists")
    def get_artists():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        # selecting a few columns just to keep output readable, its just for testing
        cursor.execute("SELECT artist_id, artist_name, country, genre_id FROM Artists LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows)


    # Albums API Route 
    @app.route("/albums")
    def get_albums():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT album_id, album_name, release_year, artist_id FROM Albums LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows)


    # Tracks API Route 
    @app.route("/tracks")
    def get_tracks():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT track_id, track_name, album_id, artist_id, genre_id FROM Tracks LIMIT 20;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows)


    # Audio Features API Route 
    @app.route("/audiofeatures")
    def get_audio_features():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT feature_id, track_id, danceability, energy, valence, tempo, loudness
            FROM AudioFeatures LIMIT 20;
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows)


    # Users API Route
    @app.route("/users")
    def get_users():
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Cannot connect to database"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, username, email, phone_number, dob, genre_id, artist_id
            FROM Users LIMIT 20;
        """)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows)

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
