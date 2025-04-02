CREATE DATABASE fitness_db;
CREATE USER fitness_user WITH ENCRYPTED PASSWORD 'fitness_pass';
GRANT ALL PRIVILEGES ON DATABASE fitness_db TO fitness_user;
ALTER DATABASE fitness_db SET timezone TO 'UTC';