
# Oracle to PostgreSQL Migration

This repository contains a Python-based tool to migrate data from an Oracle database (specifically Oracle 23ai Free) to a PostgreSQL database. The project includes scripts to set up schemas, generate and populate Oracle with test data, and perform the migration, complete with logging and verification steps.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Create Oracle Schema](#1-create-oracle-schema)
  - [2. Generate and Populate Oracle Data](#2-generate-and-populate-oracle-data)
  - [3. Create PostgreSQL Schema](#3-create-postgresql-schema)
  - [4. Perform Migration](#4-perform-migration)
  - [5. Verify Migration](#5-verify-migration)
  - [6. Test Functionality](#6-test-functionality)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview
This project was developed to facilitate the migration of a sample database schema and dataset from Oracle to PostgreSQL. It includes:
- A rerunnable Oracle schema creation script.
- A Python script to generate and populate Oracle with synthetic data (20 departments, 100,000 employees, 100 projects, 200,000 employee-project assignments).
- A migration tool to transfer data to PostgreSQL.
- PostgreSQL schema setup with views, materialized views, and functions mirroring Oracle equivalents.

The migration process is logged, and the tool handles large datasets efficiently with batch processing.

## Features
- Automated schema creation for both Oracle and PostgreSQL.
- Data generation and population with realistic test data using the `Faker` library.
- Batch migration of data from Oracle to PostgreSQL.
- Logging of migration progress and errors.
- Support for views, materialized views, and custom functions/procedures.
- Verification steps to ensure data integrity post-migration.

## Prerequisites
Before setting up the project, ensure you have the following installed:
- **Python 3.8+**
- **Oracle 23ai Free** (or compatible Oracle database)
- **Oracle Instant Client for Python** (`cx_Oracle`)
- **PostgreSQL** (e.g., via Docker)
- **Docker** (optional, for running PostgreSQL)
- **Git** (for cloning the repository)

### Required Python Packages
- `cx_Oracle`
- `psycopg2-binary`
- `Faker`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/oracle-to-postgres-migration.git
cd oracle-to-postgres-migration
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment:
```bash
python -m venv ora2postgres_env
.\ora2postgres_env\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install cx_Oracle psycopg2-binary Faker
```

### 4. Install Oracle Instant Client
* Download the Oracle Instant Client from Oracle's website.
* Extract it (e.g., to C:\oracle\instantclient_19_11).
* Add the directory to your system PATH environment variable.

### 5. Set Up Databases
* Oracle:
    * Install Oracle 23ai Free and configure a pluggable database (e.g., FREEPDB1).
    * Update connection details in src/connect.py (e.g., dsn="localhost:1521/FREEPDB1").

* PostgreSQL:
    * Run PostgreSQL via Docker:
		```bash
		docker run -d -p 5432:5432 --name postgres_db -e POSTGRES_PASSWORD=OBFUSCATED postgres
		```

* Create a database:
	```bash
	psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE migration_db;"
	```

## Usage
### 1. Create Oracle Schema 
* Run the schema script in Oracle (FREEPDB1):
	* Use SQL Developer to execute `scripts/setup_oracle.sql` (or manually run the script provided in the project).

### 2. Generate and Populate Oracle Data
* Use the `populate_oracle_data.py` script to generate synthetic data and populate the Oracle database:
	```bash
	python scripts/populate_oracle_data.py --user sys --password OraclePass123
	```
* **Data Generated**:
**Departments**: 20 records with department names (e.g., "Inc Dept") and locations using Faker.
**Projects**: 100 records with project names (e.g., "Catch Phrase"), start dates, and budgets (between $50,000 and $1,000,000).
**Employees**: 100,000 records with names, emails (emp<Id>@example.com), hire dates (within the last 5 years), salaries (between $30,000 and $120,000), and department IDs.
**Employee_Projects**: 200,000 records linking employees to projects with random hours worked (between 10 and 500 hours).

* Details:
    * The script uses the `Faker` library to generate realistic data.
    * Data is inserted in batches of 10,000 to improve performance for large tables (`employees` and `employee_projects`).

* Verify the data in Oracle:
	```sql
	SELECT COUNT(*) FROM departments;       -- Expected: 20
	SELECT COUNT(*) FROM employees;         -- Expected: 100000
	SELECT COUNT(*) FROM projects;          -- Expected: 100
	SELECT COUNT(*) FROM employee_projects; -- Expected: 200000
	```
### 3. Create PostgreSQL Schema
* Run the PostgreSQL schema setup:
	```bash
	psql -h localhost -p 5432 -U postgres -d migration_db -f scripts/setup_postgres_full.sql
	```
### 4. Perform Migration
Run the migration script:
```bash
python -m src.main
```
Monitor the console for progress logs (e.g., "Migrated 10000 rows for employees").

### 5. Verify Migration
Check row counts in PostgreSQL:
```sql
SELECT COUNT(*) FROM departments;       -- Expected: 20
SELECT COUNT(*) FROM employees;         -- Expected: 100000
SELECT COUNT(*) FROM projects;          -- Expected: 100
SELECT COUNT(*) FROM employee_projects; -- Expected: 200000
SELECT COUNT(*) FROM project_employee_summary;  -- Expected: 100
```
Review migration logs:
```sql
SELECT * FROM migration_logs ORDER BY timestamp DESC;
```
pgAdmin Query Tool
![dashboard](https://github.com/richardgliane/oracle-to-postgres-migration/blob/main/images/ps5.png)
### 6. Test Functionality
- Test the view:
	```sql
	SELECT * FROM employee_department_details LIMIT 5;
	```
pgAdmin Query Tool
![dashboard](https://github.com/richardgliane/oracle-to-postgres-migration/blob/main/images/ps1.png)
- Test the function:
	```sql
	SELECT get_employee_annual_salary(1);
	```
pgAdmin Query Tool
![dashboard](https://github.com/richardgliane/oracle-to-postgres-migration/blob/main/images/ps2.png)
- Test the procedure equivalent:
	```sql
	SELECT add_employee('Jane', 'Smith', 'jane.smith@example.com', '2024-01-01', 60000, 1);
	```
pgAdmin Query Tool
![dashboard](https://github.com/richardgliane/oracle-to-postgres-migration/blob/main/images/ps3.png)	
![dashboard](https://github.com/richardgliane/oracle-to-postgres-migration/blob/main/images/ps4.png)
## Project Structure
```
oracle-to-postgres-migration/
├── scripts/
│   ├── populate_oracle_data.py    # Populates Oracle with test data
│   ├── setup_postgres.sql         # Initial PostgreSQL logs table setup
│   └── setup_postgres_full.sql    # Full PostgreSQL schema setup
├── src/
│   ├── connect.py                # Database connection configurations
│   └── main.py                   # Migration script
└── README.md                     # This file
```
## Contributing
Contributions are welcome! Please fork the repository and submit pull requests for:
- Bug fixes
- Performance improvements
- Additional features (e.g., incremental migration)

Please follow the existing code style and include tests where applicable.
## License
This project is licensed under the MIT License. See the LICENSE file for details.
## Acknowledgments
- Special thanks to the open-source communities behind `cx_Oracle`, `psycopg2`, and `Faker`.

