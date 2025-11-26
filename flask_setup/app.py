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
    app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
    app.config["DB_USER"] = os.getenv("DB_USER", "superuser")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "123")
    app.config["DB_NAME"] = os.getenv("DB_NAME", "db_project")

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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
