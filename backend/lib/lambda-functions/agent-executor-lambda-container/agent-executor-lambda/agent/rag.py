from langchain.chains import RetrievalQA
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import PGVector


def get_rag_chain(config, llm, bedrock_runtime):
    # Prepare the same embedding model used for creating the semantic search index
    # to be used for real-time semantic search.
    embedding_model = BedrockEmbeddings(
        model_id=config.embedding_model_id, client=bedrock_runtime
    )

    vector_store = PGVector.from_existing_index(
        embedding=embedding_model,
        collection_name=config.collection_name,
        connection_string=config.postgres_connection_string,
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(k=5, fetch_k=50),
        # TODO: Pass the source documents names as part of the final answer.
        return_source_documents=False,
        input_key="question",
    )
