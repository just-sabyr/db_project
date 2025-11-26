-- setup.sql
CREATE DATABASE IF NOT EXISTS db_project;
USE db_project;

-- Drop existing tables if they exist
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS AudioFeatures;
DROP TABLE IF EXISTS Tracks;
DROP TABLE IF EXISTS Albums;
DROP TABLE IF EXISTS Artists;
DROP TABLE IF EXISTS Genres;
SET FOREIGN_KEY_CHECKS = 1;

-- Extra tables
CREATE TABLE IF NOT EXISTS Genres (                                 -- Sabyr
    genre_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    parent_genre VARCHAR(100),
    genre_name VARCHAR(100),
    genre_description VARCHAR(255)
);


-- Main tables
CREATE TABLE IF NOT EXISTS Artists (                                -- Flavio
    artist_id INT UNSIGNED PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    artist_popularity INTEGER,
    country VARCHAR(100),
    genre_id INT UNSIGNED NULL,

    UNIQUE (artist_name, country),                                  -- prevent duplicate artist names from same country
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE IF NOT EXISTS Albums (                                 -- Ildi
    album_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    album_name VARCHAR(255) NOT NULL,
    release_year INT NOT NULL,
    artist_id INT UNSIGNED NOT NULL,
    genre_id INT UNSIGNED NULL,
    cover_url VARCHAR(500),

    PRIMARY KEY (album_id),
    
    UNIQUE (artist_id, album_name, release_year),   
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),   
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id) 
);


CREATE TABLE IF NOT EXISTS Tracks (                                 -- Sabyr
    track_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    track_name VARCHAR(100) NOT NULL,
    album_id INT UNSIGNED NOT NULL,
    artist_id INT UNSIGNED NULL,
    genre_id INT UNSIGNED NULL,
    duration INT NULL,
    explicit BOOL NULL,
    popularity INT NULL,

    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE IF NOT EXISTS AudioFeatures (                          -- Frenklin
    feature_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    track_id INT UNSIGNED NOT NULL,
    danceability DECIMAL(3,2),
    energy       DECIMAL(3,2),
    valence      DECIMAL(3,2),
    tempo        DECIMAL(5,2),
    loudness     DECIMAL(4,1),
    acousticness DECIMAL(3,2),
    UNIQUE (track_id),
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id)              -- Added foreign key constraint from tracks
);


CREATE TABLE IF NOT EXISTS Users (                                  -- Sabyr
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),                                             
    phone_number CHAR(13),                                          -- + and 12 numbers
    dob DATE,
    genre_id INT UNSIGNED NULL,
    artist_id INT UNSIGNED NULL,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id),             -- Favourite genre
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id),          -- Fav artist

    CONSTRAINT chk_users_email CHECK (email IS NULL OR email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);


-- Load data from CSV files

LOAD DATA LOCAL INFILE 'dataset_csv/genres.csv'
INTO TABLE Genres
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(parent_genre, genre_name, genre_description, genre_id);

LOAD DATA INFILE '/var/lib/mysql-files/dataset_csv/artists.csv'
INTO TABLE Artists
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(artist_id, artist_name, artist_popularity, country, @genre_id)
SET genre_id = NULLIF(@genre_id, '');

LOAD DATA INFILE '/var/lib/mysql-files/dataset_csv/albums.csv'
INTO TABLE Albums
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(album_id, album_name, release_year, artist_id, @genre_id, cover_url)
SET genre_id = NULLIF(@genre_id, '');

LOAD DATA INFILE '/var/lib/mysql-files/dataset_csv/tracks.csv'
INTO TABLE Tracks
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(track_id, track_name, album_id, artist_id, @genre_id, duration, explicit, popularity)
SET genre_id = NULLIF(@genre_id, '');

LOAD DATA INFILE '/var/lib/mysql-files/dataset_csv/audio_features.csv'
INTO TABLE AudioFeatures
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;    
    
    
    
    
    
    
    
    
    
    







