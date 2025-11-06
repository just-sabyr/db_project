-- setup.sql
CREATE DATABASE IF NOT EXISTS db_project;
USE db_project;


-- Extra tables
CREATE TABLE IF NOT EXISTS genres (
    genre_id INT NOT NULL PRIMARY KEY,
    parent_genre VARCHAR(100),
    genre_name VARCHAR(100),
    genre_description TEXT
);


-- Main tables
CREATE TABLE Artists (
  artist_id INTEGER PRIMARY KEY,
  artist_name VARCHAR(255) NOT NULL,
  artist_popularity INTEGER,
  country VARCHAR(100),
  genre_id INTEGER NOT NULL,
  FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE albums (
  album_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  album_name VARCHAR(255) NOT NULL,
  release_year INT NOT NULL,
  artist_id INT UNSIGNED NOT NULL,
  genre_id INT UNSIGNED NULL,
  cover_url VARCHAR(500),
  PRIMARY KEY (album_id)
) ENGINE=InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE Tracks (
    track_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    track_name VARCHAR(100) NOT NULL,
    album_id INTEGER NOT NULL,
    artist_id INTEGER NULL,
    genre_id INTEGER NULL,
    duration INTEGER NULL, -- in milliseconds
    explicit BOOL NULL,
    popularity INT NULL,
    
    PRIMARY KEY track_id,
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE IF NOT EXISTS AudioFeatures (          -- Added the AudioFeatures  table
    feature_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    track_id INT NOT NULL,
    danceability DECIMAL(3,2),
    energy       DECIMAL(3,2),
    valence      DECIMAL(3,2),
    tempo        DECIMAL(5,2),
    loudness     DECIMAL(4,1),
    acousticness DECIMAL(3,2),
    UNIQUE (track_id)
);

CREATE TABLE IF NOT EXISTS Users (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    email VARCHAR(100) NULL, -- Email validation must be done at the Entry-point or even at the flask level
    phone_number VARCHAR(13), -- + and 12 numbers
    dob DATE NULL,
    genre_id NULL, -- CREATE A separate table to allow multiple genres
    artist_id NULL, -- CREATE a separate table to allow multiple fav artsits

    FOREIGN KEY (genre_id) REFERENCES Genres, -- Favourite genre
    FOREIGN KEY (artist_id) REFERENCES Artists, -- Fav artist
);
