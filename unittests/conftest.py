import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FLASK_SETUP_DIR = os.path.join(ROOT_DIR, "flask_setup")

if FLASK_SETUP_DIR not in sys.path:
    sys.path.insert(0, FLASK_SETUP_DIR)

import pytest
import mysql.connector
from flask_setup.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
    yield conn
    conn.close()


@pytest.fixture
def clean_db(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE AudioFeatures;")
    cursor.execute("TRUNCATE TABLE Tracks;")
    cursor.execute("TRUNCATE TABLE Albums;")
    cursor.execute("TRUNCATE TABLE Users;")
    cursor.execute("TRUNCATE TABLE Artists;")
    cursor.execute("TRUNCATE TABLE Genres;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    db_connection.commit()
    cursor.close()
