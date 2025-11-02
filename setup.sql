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
