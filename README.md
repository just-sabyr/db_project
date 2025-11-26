# Spotify Music Dataset Project

#### The dataset in raw format is available in `dataset_csv/dataset.csv`


# Project Setup:
## 1. Install MySQL

## 2. Create the MySQL database

Open the MySQL Shell
```bash
    sudo mysql
```

Run these sql commands
```mysql
    CREATE USER 'superuser'@'localhost' IDENTIFIED BY '123';
    GRANT ALL PRIVILEGES ON db_project.* TO 'superuser'@'localhost';
    GRANT FILE ON *.* TO 'superuser'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
```

## 3. Initialize the MySQL database 
MySQL Database schema is in setup.sql, so just run
```bash
    mysql -u superuser -p < setup.sql
```

## 4. Copy to the safe folder
from proj to secure
```bash
sudo cp -r /home/sabyr/Documents/database_systems/project/ /var/lib/mysql-files/dataset_csv 
```

from secure to proj
```bash
    sudo cp -r /home/sabyr/Documents/database_systems/project/ /var/lib/mysql-files/dataset_csv 

```

## 5. Import CSVs directly

The `dataset_csv/genres.csv` file can be loaded directly into the database. Below are three common ways: MySQL

Replace paths and credentials as needed. Use absolute paths or run commands from the project root so the relative paths work.

### MySQL (LOAD DATA LOCAL INFILE)

Load the CSV (example using an absolute path):

```bash
    # run from project root or supply absolute path
    mysql --local-infile=1 -u superuser -p -e \
    "USE db_project; LOAD DATA LOCAL INFILE '$(pwd)/dataset_csv/genres.csv' \
    INTO TABLE genres \
    FIELDS TERMINATED BY ',' \
    OPTIONALLY ENCLOSED BY '\"' \
    LINES TERMINATED BY '\n' \
    IGNORE 1 LINES \
    (parent_genre, genre_name, genre_description, genre_id);"
```

Notes:
- If `LOCAL` is blocked by server/client, either enable `local_infile` or copy the CSV to the server and omit `LOCAL`.
- If you prefer auto-generated ids on the DB side, change `genre_id` to `INT AUTO_INCREMENT PRIMARY KEY` and omit `genre_id` from the load column-list.

### Quick verification queries (MySQL example)

```sql
USE db_project;
SELECT COUNT(*) FROM genres;
SELECT * FROM genres ORDER BY genre_id LIMIT 20;
```

---
