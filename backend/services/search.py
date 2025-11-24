import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_SEARCH_SEMANTIC_CONFIG = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIG")
AZURE_SEARCH_VECTOR_DIM = int(os.getenv("AZURE_SEARCH_VECTOR_DIMENSION"))


def get_search_client():
    return SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
    )


# INDEXAÇÃO 
def index_chunks(documents: list[dict]):
    client = get_search_client()
    return client.upload_documents(documents=documents)


# VECTOR SEARCH 
def vector_search(query_embedding: list[float], k: int = 5):
    client = get_search_client()

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k=k,
        fields="embedding"
    )

    results = client.search(
        vector_queries=[vector_query],
        top=k
    )

    return results


# SEMANTIC SEARCH
def semantic_search(query_text: str, k: int = 5):
    client = get_search_client()

    return client.search(
        search_text=query_text,
        query_type="semantic",
        semantic_configuration_name=AZURE_SEARCH_SEMANTIC_CONFIG,
        top=k
    )


# HYBRID SEARCH (vetor + semântico)
def hybrid_search(query_text: str, query_embedding: list[float], k: int = 5):
    client = get_search_client()

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k=k,
        fields="embedding"
    )

    return client.search(
        search_text=query_text,
        vector_queries=[vector_query],
        query_type="semantic",
        semantic_configuration_name=AZURE_SEARCH_SEMANTIC_CONFIG,
        top=k
    )
