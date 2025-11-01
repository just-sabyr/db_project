# Spotify Music Dataset Project

#### The dataset in raw format is available in `dataset_csv/dataset.csv`


# Project Setup:
## 1. Install MySQL
## 2. Create the MySQL database

Open the MySQL Shell
```bash
    sudo mysql
```

Run this sql commands
```mysql
    CREATE DATABASE db_project;
    CREATE USER 'superuser'@'localhost' IDENTIFIED BY 'pwd_easy123';
    GRANT ALL PRIVILEGES ON db_project.* TO 'superuser'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
```

## 3. Initialize the MySQL database 
MySQL Database schema is in setup.sql, so just run
```bash
    mysql -u superuser -p < setup.sql
```