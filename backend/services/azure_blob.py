import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone
import os

load_dotenv()

AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
AZURE_BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")
AZURE_BLOB_ACCOUNT = os.getenv("AZURE_BLOB_ACCOUNT")
AZURE_BLOB_KEY = os.getenv("AZURE_BLOB_KEY")

blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_BLOB_CONNECTION_STRING
)
container_client = blob_service_client.get_container_client(
    AZURE_BLOB_CONTAINER_NAME
)


def upload_file_to_blob(file_name: str, file_data: bytes, content_type: str = None) -> str:
    blob_client = container_client.get_blob_client(file_name)

    blob_client.upload_blob(
        file_data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )

    return blob_client.url


def get_blob_url(file_name: str) -> str:
    """
    Retorna a URL pública (ou SAS, se configurado) do blob para um dado nome de arquivo.
    Não faz chamada de rede, só monta a URL com base no client.
    """
    blob_client = container_client.get_blob_client(file_name)
    return blob_client.url


def list_files_in_blob():
    files = []
    for blob in container_client.list_blobs():
        files.append({
            "name": blob.name
        })
    return files

def download_file_from_blob(file_name: str) -> bytes:
    blob_client = container_client.get_blob_client(file_name)
    data = blob_client.download_blob().readall()
    return data    


def generate_sas_url(file_name: str, expiry_minutes: int = 30) -> str:
    sas_token = generate_blob_sas(
        account_name=AZURE_BLOB_ACCOUNT,
        container_name=AZURE_BLOB_CONTAINER_NAME,
        blob_name=file_name,
        account_key=AZURE_BLOB_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)    
        )

    url = f"https://{AZURE_BLOB_ACCOUNT}.blob.core.windows.net/{AZURE_BLOB_CONTAINER_NAME}/{file_name}?{sas_token}"

    return url