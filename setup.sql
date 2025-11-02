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

-- Ildi, Flavio implement your tables here
DROP TABLE IF EXISTS albums;

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

