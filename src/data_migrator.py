def migrate_data(oracle_conn, pg_conn, table_name):
    oracle_cursor = oracle_conn.cursor()
    pg_cursor = pg_conn.cursor()

    # Fetch Oracle data
    oracle_cursor.execute(f"SELECT * FROM {table_name}")
    rows = oracle_cursor.fetchall()
    columns = [desc[0] for desc in oracle_cursor.description]

    # Insert into PostgreSQL
    placeholders = ",".join(["%s"] * len(columns))
    pg_query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
    pg_cursor.executemany(pg_query, rows)

    pg_conn.commit()