# src/main.py
from src.connect import oracle_connect, postgres_connect
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_migration(table_name, status, message, pg_cursor):
    pg_cursor.execute(
        "INSERT INTO migration_logs (table_name, status, message) VALUES (%s, %s, %s)",
        (table_name, status, message)
    )

def migrate_table(ora_cursor, pg_cursor, table_name, columns, ora_query, pg_insert):
    logging.info(f"Migrating {table_name}...")
    ora_cursor.execute(ora_query)
    batch_size = 10000
    rows = ora_cursor.fetchmany(batch_size)
    total_migrated = 0

    while rows:
        try:
            pg_cursor.executemany(pg_insert, rows)
            total_migrated += len(rows)
            logging.info(f"Migrated {total_migrated} rows for {table_name}")
            rows = ora_cursor.fetchmany(batch_size)
        except Exception as e:
            log_migration(table_name, "FAILURE", str(e), pg_cursor)
            raise
        else:
            log_migration(table_name, "SUCCESS", f"Migrated {total_migrated} rows", pg_cursor)

def main():
    ora_conn = oracle_connect()
    pg_conn = postgres_connect()
    ora_cursor = ora_conn.cursor()
    pg_cursor = pg_conn.cursor()

    try:
        # Migrate departments
        migrate_table(
            ora_cursor, pg_cursor,
            "departments",
            ["dept_id", "dept_name", "location"],
            "SELECT dept_id, dept_name, location FROM departments",
            "INSERT INTO departments (dept_id, dept_name, location) VALUES (%s, %s, %s)"
        )

        # Migrate employees
        migrate_table(
            ora_cursor, pg_cursor,
            "employees",
            ["emp_id", "first_name", "last_name", "email", "hire_date", "salary", "dept_id"],
            "SELECT emp_id, first_name, last_name, email, hire_date, salary, dept_id FROM employees",
            "INSERT INTO employees (emp_id, first_name, last_name, email, hire_date, salary, dept_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )

        # Migrate projects
        migrate_table(
            ora_cursor, pg_cursor,
            "projects",
            ["project_id", "project_name", "start_date", "budget"],
            "SELECT project_id, project_name, start_date, budget FROM projects",
            "INSERT INTO projects (project_id, project_name, start_date, budget) VALUES (%s, %s, %s, %s)"
        )

        # Migrate employee_projects
        migrate_table(
            ora_cursor, pg_cursor,
            "employee_projects",
            ["emp_proj_id", "emp_id", "project_id", "hours_worked"],
            "SELECT emp_proj_id, emp_id, project_id, hours_worked FROM employee_projects",
            "INSERT INTO employee_projects (emp_proj_id, emp_id, project_id, hours_worked) VALUES (%s, %s, %s, %s)"
        )

        # Refresh materialized view
        pg_cursor.execute("REFRESH MATERIALIZED VIEW project_employee_summary")
        log_migration("project_employee_summary", "SUCCESS", "Materialized view refreshed", pg_cursor)

        pg_conn.commit()
        logging.info("Migration completed successfully!")

    except Exception as e:
        pg_conn.rollback()
        logging.error(f"Migration failed: {e}")
        raise
    finally:
        ora_cursor.close()
        pg_cursor.close()
        ora_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main()