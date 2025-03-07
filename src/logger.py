def log_migration(pg_cursor, table_name, status, message):
    pg_cursor.execute(
        "INSERT INTO migration_logs (table_name, status, message) VALUES (%s, %s, %s)",
        (table_name, status, message)
    )