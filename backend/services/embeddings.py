import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

def get_openai_client():
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise ValueError("Azure OpenAI endpoint ou API key não configurados")
    
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-05-01-preview",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

def generate_embedding(text: str) -> str:
    client = get_openai_client()
    response = client.embeddings.create(
        input= text,
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding