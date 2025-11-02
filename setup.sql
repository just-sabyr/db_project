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

