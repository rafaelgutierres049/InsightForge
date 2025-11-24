from datetime import datetime, timezone
import uuid

from backend.services.document_processor import process_document_for_rag
from backend.services.embeddings import generate_embedding
from backend.services.search import index_chunks


def process_and_index_document(file_name: str):
    """
    Pipeline completo do InsightForge.
    1. Extrai e limpa texto
    2. Chunking híbrido
    3. Gera embeddings
    4. Indexa no Azure Search
    """

    chunks = process_document_for_rag(file_name)
    documents_for_index = []

    for chunk in chunks:
        emb = generate_embedding(chunk)

        doc = {
            "id": str(uuid.uuid4()),
            "file_name": file_name,
            "title": file_name, 
            "section": "",
            "content": chunk,
            "tags": [],
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "embedding": emb,
        }

        documents_for_index.append(doc)

    result = index_chunks(documents_for_index)
    return {"status": "indexed", "results": str(result)}
