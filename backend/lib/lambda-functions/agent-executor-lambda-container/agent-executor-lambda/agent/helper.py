import psycopg2


def test_db_connection(host, dbname, username, password):
    # Connect to the database
    conn = psycopg2.connect(
        host=host, database=dbname, user=username, password=password
    )
    # Get cursor
    cur = conn.cursor()

    # Query to get all tables
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
    )

    # Fetch all the tables
    tables = cur.fetchall()

    # Print the table names
    print(f"SQL tables: {tables}")

    # Close connection
    conn.close()
