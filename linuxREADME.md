# Spotify Music Dataset Project

## Dataset

The raw dataset is available in `dataset_csv/dataset.csv` and related CSV files in the `dataset_csv/` folder.

## Project Setup

### 1. Install MySQL

Install MySQL on your system if not already installed.

### 2. Create the MySQL Database and User

Open the MySQL Shell:

```bash
sudo mysql
```

Run these SQL commands:

```sql
CREATE USER 'superuser'@'localhost' IDENTIFIED BY '123';
GRANT ALL PRIVILEGES ON db_project.* TO 'superuser'@'localhost';
GRANT FILE ON *.* TO 'superuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Initialize the MySQL Database and Insert Data

The schema and all data are inserted automatically by running the setup script. No manual data insertion is needed.

```bash
mysql -u superuser -p < setup_linux.sql
```

> **Note:** Use `setup_linux.sql` for Linux. For other platforms, use `setup.sql` if needed.

### 4. (Optional) Copy CSVs to MySQL Secure Folder

If you need to import CSVs manually or for troubleshooting:

```bash
sudo cp -r /home/sabyr/Documents/database_systems/project/dataset_csv /var/lib/mysql-files/
```

### 5. Verifying the Database

You can verify the data was loaded correctly with queries like:

```sql
USE db_project;
SELECT COUNT(*) FROM genres;
SELECT * FROM genres ORDER BY genre_id LIMIT 20;
```

---

# Running the Flask Backend

## Create virtual enviroment

```bash
   python -m venv venv
```

## Activate in Windows

```bash
   venv\Scripts\activate
```

## Activate in Linux or Mac

```bash
   source venv/bin/activate
```

## Install Python dependencies

```bash
   pip install flask mysql-connector-python python-dotenv
```

## Create .env file (Each team member can put their own MySQL username and password.)

```bash
   DB_HOST=localhost
   DB_USER=YOUR USERNAME
   DB_PASSWORD=YOUR PASSWORD
   DB_NAME=db_project

   FLASK_APP=app.py
   FLASK_ENV=development
```

## Run the flask server

```bash
         cd flask_setup
```

```bash
   flask run
```

## If Flask doesn't detect the app, set manually:

```bash
   $env:FLASK_APP="app.py"     # PowerShell
   export FLASK_APP=app.py     # Mac/Linux
```

## The server will start at

```bash
   http://127.0.0.1:5000/
```
