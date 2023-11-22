import json
import os
from botocore.config import Config
import boto3
from langchain.embeddings import BedrockEmbeddings
from langchain.schema.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores.pgvector import PGVector

import psycopg2
import sqlalchemy

ssm = boto3.client("ssm")

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

CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver="psycopg2",
    host=host,
    port=port,
    database=dbname,
    user=username,
    password=password,
)

db_connection = psycopg2.connect(
    host=host,
    port=port,
    database=dbname,
    user=username,
    password=password,
)

BEDROCK_CROSS_ACCOUNT_ROLE_ARN = os.environ.get("BEDROCK_CROSS_ACCOUNT_ROLE_ARN")
bedrock_region_parameter = "/AgenticLLMAssistant/bedrock_region"

BEDROCK_REGION = ssm.get_parameter(Name=bedrock_region_parameter)
BEDROCK_REGION = BEDROCK_REGION["Parameter"]["Value"]

retry_config = Config(
    region_name=BEDROCK_REGION,
    retries={"max_attempts": 10, "mode": "standard"}
)
bedrock_runtime = boto3.client("bedrock-runtime", config=retry_config)
bedrock = boto3.client("bedrock", config=retry_config)


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


def prepare_documents_with_metadata(documents_processed):

    langchain_documents_text = []
    langchain_documents_tables = []

    for document in documents_processed:
        document_name = document['name']
        document_source_location = document['source_location']
        document_s3_metadata = document['metadata']

        mapping_to_original_page_numbers = {
            idx: pg_num for idx, pg_num
            in enumerate(json.loads(document_s3_metadata["pages_kept"]))
        }
        # remove pages_kept since we already put the original page number.
        del document_s3_metadata["pages_kept"]

        for page in document['pages']:
            # Turn each page into a Langchain Document.
            # Note: you could choose to also prepend part of the previous document
            # and append part of the next document to include more context for documents
            # that have many pages which continue their text on the next page.
            current_metadata = {
                'document_name': document_name,
                'document_source_location': document_source_location,
                'page_number': page['page'],
                'original_page_number': mapping_to_original_page_numbers[page['page']]
            }
            # merge the document_s3_metadata into the langchain Document metadata
            # to be able to use them for filtering.
            current_metadata.update(document_s3_metadata)

            langchain_documents_text.append(
                Document(
                    page_content=page['page_text'],
                    metadata=current_metadata
                )
            )
            # Turn all the tables of the pages into seperate Langchain Documents as well
            for table in page['page_tables']:
                langchain_documents_tables.append(
                    Document(
                        page_content=table,
                        metadata=current_metadata
                    )
                )

    return langchain_documents_text, langchain_documents_tables


def load_processed_documents(json_file_path):
    with open(json_file_path, 'rb') as file:
        processed_documents = json.load(file)
    return processed_documents


if __name__ == "__main__":
    test_db_connection()

    url_object = sqlalchemy.URL.create(
        "postgresql+psycopg2",
        username=username,
        password=password,
        host=host,
        database=dbname,
    )

    input_data_base_path = "/opt/ml/processing/input/"
    processed_docs_filename = "documents_processed.json"
    token_split_chunk_size = 512
    token_chunk_overlap = 64
    # Define an embedding model to generate embeddings
    embedding_model_id = "amazon.titan-embed-text-v1"
    COLLECTION_NAME = 'agentic_assistant_vector_store'
    # make this an argument.
    pre_delete_collection = True

    db_engine = sqlalchemy.create_engine(url_object)

    processed_documents_file_path = os.path.join(
        input_data_base_path,
        "processed_documents",
        processed_docs_filename
    )

    print(processed_documents_file_path)

    if os.path.isfile(processed_documents_file_path):
        processed_documents = load_processed_documents(processed_documents_file_path)
        langchain_documents_text, langchain_documents_tables = prepare_documents_with_metadata(
            processed_documents
        )
        # The chunk overlap duplicates some text across chunks
        # to prevent context from being lost between chunks.
        # TODO: the following spliting uses tiktoken,
        # create a custom one that use the tokenizer from anthropic.
        text_splitter = TokenTextSplitter(
            chunk_size=token_split_chunk_size,
            chunk_overlap=token_chunk_overlap
        )

        langchain_documents_text_chunked = text_splitter.split_documents(
            langchain_documents_text + langchain_documents_tables
        )

        embedding_model = BedrockEmbeddings(
            model_id=embedding_model_id,
            client=bedrock_runtime
        )

        activate_vector_extension(db_connection)

        pgvector_store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
            embedding_function=embedding_model,
            pre_delete_collection=pre_delete_collection
        )

        pgvector_store.add_documents(langchain_documents_text_chunked)

        print("test indexing results")
        test_question = "Who were in the board of directors of Amazon in 2021 and what were their positions?"
        print(pgvector_store.similarity_search_with_score(test_question))

    else:
        raise ValueError(f"{processed_documents_file_path} must be a file.")

    test_db_connection()
