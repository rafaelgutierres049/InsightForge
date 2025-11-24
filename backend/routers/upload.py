from fastapi import APIRouter, UploadFile, File, HTTPException
from ..agents.index_agent import IndexAgent
from ..services.azure_blob import upload_file_to_blob, list_files_in_blob
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
import traceback
load_dotenv()

router = APIRouter()
index_agent = IndexAgent()

router = APIRouter()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX_NAME")
SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")

search_client = SearchClient(
    SEARCH_ENDPOINT,
    SEARCH_INDEX,
    AzureKeyCredential(SEARCH_KEY)
)

@router.get("/list_uploads")
async def list_uploads():
      return {"files": list_files_in_blob()}   

@router.delete("/delete/{file_name}")
async def delete_file(file_name: str):
    """
    Deleta um arquivo do Blob Storage.
    """
    try:
        from ..services.azure_blob import container_client
        blob_client = container_client.get_blob_client(file_name)
        blob_client.delete_blob()
        delete_file_chunks(file_name)
        return {"status": "success", "message": f"Arquivo '{file_name}' deletado."}
    except Exception as e:
        print("[Delete] ERRO durante deleção do arquivo:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload de um documento, envio ao Blob Storage,
    processamento completo pelo IndexAgent.
    """
    try:
        print("\n[Upload] Recebendo arquivo:", file.filename)

        file_bytes = await file.read()

        # Upload para Blob Storage
        blob_url = upload_file_to_blob(file.filename, file_bytes, content_type=file.content_type)
        print(f"[Upload] Arquivo salvo no Blob: {blob_url}")

        # Processar via IndexAgent
        result = index_agent.process_and_index(file.filename)

        print("[Upload] Processamento concluído.")
        return {
            "status": "success",
            "file": file.filename,
            "blob_url": "http://xxxxxxxxxxxxxxxxxxx.blob.core.windows.net/container/" + file.filename,
            "chunks_indexed": result["chunks_indexed"]
        }

    except Exception as e:
        print("[Upload] ERRO durante upload/indexação:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
def delete_file_chunks(file_name: str):
    """
    Remove todos os registros do índice relacionados ao arquivo excluído.
    """
    results = search_client.search(
        search_text="",
        filter=f"file_name eq '{file_name}'",
        top=2000
    )

    batch = []
    for r in results:
        batch.append({
            "@search.action": "delete",
            "id": r["id"]
        })

    if batch:
        search_client.upload_documents(documents=batch)
        print(f"[SearchCleanup] Chunks removidos para {file_name}: {len(batch)}")
    else:
        print(f"[SearchCleanup] Nenhum chunk encontrado para {file_name}.")
