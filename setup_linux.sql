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
    artist_id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    artist_name VARCHAR(255) NOT NULL,
    artist_popularity INTEGER,
    country VARCHAR(100),
    genre_id INT UNSIGNED NULL,

    UNIQUE (artist_name, country),                                  -- prevent duplicate artist names from same country
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Albums (                                 -- Ildi
    album_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    album_name VARCHAR(255) NOT NULL,
    release_year INT NULL,
    artist_id INT UNSIGNED NOT NULL,
    genre_id INT UNSIGNED NULL,
    cover_url VARCHAR(500),

    PRIMARY KEY (album_id),
    
    UNIQUE (artist_id, album_name),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE,   
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id) ON DELETE CASCADE
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

    FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE
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
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id) ON DELETE CASCADE         
);


CREATE TABLE IF NOT EXISTS Users (                                  -- Sabyr
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),                                             
    phone_number CHAR(13),                                          -- + and 12 numbers
    dob DATE,
    genre_id INT UNSIGNED NULL,
    artist_id INT UNSIGNED NULL,

    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE,             -- Favourite genre
    FOREIGN KEY (artist_id) REFERENCES Artists(artist_id) ON DELETE CASCADE,          -- Fav artist

    CONSTRAINT chk_users_email CHECK (email IS NULL OR email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
);


-- Load data from CSV files

LOAD DATA LOCAL INFILE 'dataset_csv/genres.csv'
INTO TABLE Genres
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(parent_genre, genre_name, genre_description, @genre_id)
SET genre_id = NULLIF(TRIM(@genre_id), '');

LOAD DATA LOCAL INFILE 'dataset_csv/artists.csv'
IGNORE INTO TABLE Artists
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(artist_id, artist_name, artist_popularity, country, @genre_id)
SET genre_id = NULLIF(TRIM(@genre_id), '');

LOAD DATA LOCAL INFILE 'dataset_csv/albums.csv'
INTO TABLE Albums
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(album_id, album_name, artist_id, @genre_id, release_year, cover_url)
SET genre_id = NULLIF(TRIM(@genre_id), '');

LOAD DATA LOCAL INFILE 'dataset_csv/tracks.csv'
INTO TABLE Tracks
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(track_id, track_name, album_id, @artist_id, @genre_id, duration, explicit, popularity)
SET genre_id = NULLIF(TRIM(@genre_id), ''),
    artist_id = NULLIF(TRIM(@artist_id), '');

LOAD DATA LOCAL INFILE 'dataset_csv/audio_features.csv'
INTO TABLE AudioFeatures
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(track_id, danceability, energy, valence, tempo, loudness, acousticness);


-- generate_users.py
INSERT INTO Users (username, password, email, phone_number, dob, genre_id, artist_id) VALUES
('frenklin23', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'frenklin23@gmail.com', '+90682345678', '2000-05-12', 1, 62),
('sabyrPM', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'projectmanager@yahoo.com', '+90694567890', '1999-11-03', 3, 5),
('Favi', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'favi@gmail.com', '+90671234567', '2001-07-21', 2, 1),
('ildo', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'ildoh@hotmail.com', '+905312345678', '1998-02-18', 4, 7),
('amira_sound', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'amira.sound@outlook.com', '+90672220011', '2002-09-30', 6, NULL),
('noah.dev', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'noah.dev@gmail.com', '+491712345678', '1997-03-05', 1, 3),
('melisa2000', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'melisa2000@gmail.com', '+35688899900', '2000-12-14', 5, 4),
('altin_rh', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'altin.rh@yahoo.com', '+35691234888', '1995-01-09', NULL, NULL),
('julia_tunes', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'julia.tunes@gmail.com', '+55696666222', '2003-04-27', 2, 9),
('genti_official', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'genti.official@gmail.com', '+55682998877', '1996-10-10', 8, 12),
('mario_s', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'mario.s@gmail.com', '+393512345678', '1994-06-01', 4, NULL),
('eva_star', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'eva.star@hotmail.com', '+35692340000', '2001-08-23', 7, 13),
('lina_k', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'lina.k@yahoo.com', '+35675556677', '2002-03-14', 1, 5),
('andrea_vibe', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'andrea.vibe@gmail.com', '+35682112233', '1998-12-31', 9, 6),
('kevin_m', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'kevin.m@gmail.com', '+1 2025550199', '1997-04-17', 2, 10),
('elira_x', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'elira.x@gmail.com', '+35683330055', '2000-11-20', 3, NULL),
('ronaldo_plays', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'ronaldo.plays@gmail.com', '+35690099887', '1999-01-01', NULL, 4),
('diana_live', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'diana.live@gmail.com', '+35694443210', '2003-09-15', 6, 8),
('markosound', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'markosound@outlook.com', '+306944442211', '2002-02-02', 10, NULL),
('sara_b', 'scrypt:32768:8:1$leIQvoWvOsrUb3fR$d59d2fe16990fe100b67bfebed41cd2c273b419a2751f52bb23a97ff4905f1a6a9ca27b6a73210ee3e0a3458687e0fecb825a1d708078437f035ff42f68da761', 'sara.b@gmail.com', '+90688812121', '1998-05-05', 5, 15);
    
    
    
    
    
    
    
    







