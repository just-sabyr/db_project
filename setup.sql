-- setup.sql
CREATE DATABASE IF NOT EXISTS db_project;
USE db_project;


-- Extra table
CREATE TABLE GENRES (
    genre_id INT AUTOINCREMENT PRIMARY KEY, 
    parent_genre VARCHAR(50) DEFAULT NULL,
    genre_name VARCHAR(20) DEFAULT NULL,
    genre_description VARCHAR(200) DEFAULT NULL,
    -- let's ignore genres.parent_genre_id for now
);

-- Current task
read from the dataset_csv/genres.csv column names: parent_genre,genre,short_description,genre_id