import os
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from .azure_blob import download_file_from_blob
load_dotenv()

DI_ENDPOINT = os.getenv("AZURE_DI_ENDPOINT")
DI_KEY = os.getenv("AZURE_DI_API_KEY")
DI_MODEL = os.getenv("AZURE_DI_MODEL_ID")

client = DocumentIntelligenceClient(
    endpoint=DI_ENDPOINT,
    credential=AzureKeyCredential(DI_KEY)
)

def extract_text_from_blob(file_name: str) -> str:
    """
    Faz o download do arquivo do Blob e extrai o texto contido via Azure Document Intelligence
    Retorna o texto completo do documento
    """

    # Download do arquivo
    file_bytes = download_file_from_blob(file_name)

    # Criar requisição
    analyse_request = AnalyzeDocumentRequest(bytes_source=file_bytes)

    # Chamar a API
    poller = client.begin_analyze_document(
        model_id=DI_MODEL,
        analyze_request=analyse_request
    )

    result = poller.result() 

    # Extrair o texto
    full_text = ""

    for page in result.pages:
        if hasattr(page, "lines"):
            for line in page.lines:
                full_text += line.content + "\n"

    return full_text

