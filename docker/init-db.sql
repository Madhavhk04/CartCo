SELECT 'Initializing Databases';
CREATE DATABASE airflow;
CREATE DATABASE marquez;

CREATE USER marquez WITH PASSWORD 'marquez';
GRANT ALL PRIVILEGES ON DATABASE marquez TO marquez;
ALTER DATABASE marquez OWNER TO marquez;
