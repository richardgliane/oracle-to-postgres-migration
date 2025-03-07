import cx_Oracle
import psycopg2

def oracle_connect():
    conn = cx_Oracle.connect(user="sys", password="OBFUSCATED", dsn="localhost:1521/FREEPDB1", mode=cx_Oracle.SYSDBA)
    conn.cursor().execute("ALTER SESSION SET CONTAINER = FREEPDB1")
    return conn

def postgres_connect():
    return psycopg2.connect(
        dbname="migration_db",  # Updated to the new database
        user="postgres",
        password="OBFUSCATED",
        host="localhost",
        port="5432"
    )