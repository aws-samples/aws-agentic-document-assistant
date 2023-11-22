import json
import os

import boto3
import dask.dataframe as dd
import psycopg2
import sqlalchemy

secretsmanager = boto3.client("secretsmanager")

secret_response = secretsmanager.get_secret_value(
    SecretId=os.environ["SQL_DB_SECRET_ID"]
)

database_secrets = json.loads(secret_response["SecretString"])

# Extract credentials
host = database_secrets['host']
dbname = database_secrets['dbname']
username = database_secrets['username']
password = database_secrets['password']
port = database_secrets["port"]

db_connection = psycopg2.connect(
    host=host,
    port=port,
    database=dbname,
    user=username,
    password=password,
)


def activate_vector_extension(db_connection):
    """Activate PGVector extension."""

    db_connection.autocommit = True
    cursor = db_connection.cursor()
    # install pgvector
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    db_connection.close()


def test_db_connection():
    # Connect to the database
    conn = psycopg2.connect(
        host=host,
        database=dbname,
        user=username,
        password=password
    )
    # Get cursor
    cur = conn.cursor()

    # Query to get all tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")

    # Fetch all the tables
    tables = cur.fetchall()

    # Print the table names
    print(f"SQL tables: {tables}")

    # Close connection
    conn.close()


def load_sql_tables(raw_tables_base_path, raw_tables_data_paths, columns_to_load, engine):
    """Load csv files as SQL tables into an Amazon Aurora PostgreSQL DB.

    Note:
        raw_tables_data_paths (List, str): a list of strings, each string
        can be a csv file, or a folder that contains a partitioned csv file.
    """

    for raw_table_path in raw_tables_data_paths:
        data_loading_path = os.path.join(
            raw_tables_base_path,
            raw_table_path
        )

        if os.path.isdir(data_loading_path):
            data_loading_path = os.path.join(data_loading_path, "*")
            table_name = raw_table_path
        else:
            table_name = raw_table_path.split(".")[0]

        print(f"Loading {table_name} data into a pandas dataframe")
        current_data_df = dd.read_csv(data_loading_path).compute()
        if columns_to_load == "all":
            columns_to_load = current_data_df.columns

        current_data_df = current_data_df[columns_to_load]

        current_data_df.to_sql(
            table_name, engine, if_exists='replace', index=False
        )

    return True


if __name__ == "__main__":
    test_db_connection()

    url_object = sqlalchemy.URL.create(
        "postgresql+psycopg2",
        username=username,
        password=password,
        host=host,
        database=dbname,
    )

    db_engine = sqlalchemy.create_engine(url_object)

    input_data_base_path = "/opt/ml/processing/input/"
    raw_sql_tables_base_path = os.path.join(input_data_base_path, "sqltables")
    tables_raw_data_paths = os.listdir(raw_sql_tables_base_path)
    columns_to_load = "all"

    print(raw_sql_tables_base_path, tables_raw_data_paths)
    load_sql_tables(
        raw_sql_tables_base_path,
        tables_raw_data_paths,
        columns_to_load,
        db_engine
    )

    test_db_connection()
