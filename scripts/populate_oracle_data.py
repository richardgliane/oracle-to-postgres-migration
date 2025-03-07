# scripts/populate_oracle_data.py
# Populates Oracle database with sample data for migration testing (~5 minutes runtime)

import cx_Oracle
from faker import Faker
import random
from datetime import datetime
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Populate Oracle database with test data.")
    parser.add_argument("--user", default="sys", help="Oracle database username (default: sys)")
    parser.add_argument("--password", default="OBFUSCATED", help="Oracle database password (default: OraclePass123)")
    return parser.parse_args()

def main():
    args = parse_args()
    fake = Faker()
    
    # Connect with SYSDBA role
    conn = cx_Oracle.connect(user=args.user, password=args.password, dsn="localhost:1521/FREEPDB1", mode=cx_Oracle.SYSDBA)
    cursor = conn.cursor()

    # Switch to FREEPDB1 PDB
    cursor.execute("ALTER SESSION SET CONTAINER = FREEPDB1")

    # Insert Departments (20 rows)
    dept_data = [(i, fake.company_suffix() + " Dept", fake.city()) for i in range(1, 21)]
    cursor.executemany(
        "INSERT INTO departments (dept_id, dept_name, location) VALUES (:1, :2, :3)",
        dept_data
    )
    conn.commit()
    print("Departments inserted")

    # Insert Projects (100 rows)
    proj_data = [(i, fake.catch_phrase(), fake.date_this_decade(), random.uniform(50000, 1000000)) 
                 for i in range(1, 101)]
    cursor.executemany(
        "INSERT INTO projects (project_id, project_name, start_date, budget) VALUES (:1, :2, :3, :4)",
        proj_data
    )
    conn.commit()
    print("Projects inserted")

    # Insert Employees (100K rows in batches)
    batch_size = 10000
    for batch in range(0, 100000, batch_size):
        emp_data = [
            (i, fake.first_name(), fake.last_name(), f"emp{i}@example.com", 
             fake.date_between(start_date="-5y", end_date="today"), 
             random.uniform(30000, 120000), random.randint(1, 20))
            for i in range(batch + 1, min(batch + batch_size + 1, 100001))
        ]
        cursor.executemany(
            "INSERT INTO employees (emp_id, first_name, last_name, email, hire_date, salary, dept_id) "
            "VALUES (:1, :2, :3, :4, :5, :6, :7)",
            emp_data
        )
        conn.commit()
        print(f"Inserted employees {batch + 1} to {min(batch + batch_size, 100000)}")

    # Insert Employee_Projects (200K rows in batches)
    for batch in range(0, 200000, batch_size):
        emp_proj_data = [
            (i, random.randint(1, 100000), random.randint(1, 100), random.uniform(10, 500))
            for i in range(batch + 1, min(batch + batch_size + 1, 200001))
        ]
        cursor.executemany(
            "INSERT INTO employee_projects (emp_proj_id, emp_id, project_id, hours_worked) "
            "VALUES (:1, :2, :3, :4)",
            emp_proj_data
        )
        conn.commit()
        print(f"Inserted employee_projects {batch + 1} to {min(batch + batch_size, 200000)}")

    conn.close()
    print("Data population complete!")

if __name__ == "__main__":
    main()