from ..services.document_intelligence import extract_text_from_blob
from ..services.chunker import detect_sections, semantic_chunking, fixed_chunking
from ..services.embeddings import generate_embedding
from ..services.search import index_chunks
from uuid import uuid4

class IndexAgent:

    def process_and_index(self, file_name: str):
        print(f"\n[IndexAgent] Iniciando processamento do arquivo: {file_name}")

        # Extrair texto do Document Intelligence
        text = extract_text_from_blob(file_name)

        if not text or len(text.strip()) < 5:
            raise ValueError("[IndexAgent] Nenhum texto foi extraído do documento.")

        print(f"[IndexAgent] Texto extraído ({len(text)} caracteres).")

        # Detectar seções
        sections = detect_sections(text)
        print(f"[IndexAgent] Seções detectadas: {len(sections)}")

        # CHUNKING HÍBRIDO
        semantic_chunks = semantic_chunking(sections)
        print(f"[IndexAgent] Chunks semânticos gerados: {len(semantic_chunks)}")

        fixed_chunks = fixed_chunking(text, max_tokens=800, overlap=100)
        print(f"[IndexAgent] Chunks fixos gerados: {len(fixed_chunks)}")

        # Combinação final
        chunks = []

        for c in semantic_chunks:
            chunks.append(("SEMANTIC", c))

        for c in fixed_chunks:
            chunks.append(("FIXED", c))

        print(f"[IndexAgent] Total de chunks combinados: {len(chunks)}")

        # Para cada chunk - gerar embedding e indexar
        docs_to_index = []

        for idx, (chunk_type, chunk_text) in enumerate(chunks):

            chunk_id = str(uuid4())

            embedding = generate_embedding(chunk_text)

            document = {
                "id": chunk_id,
                "file_name": file_name,
                "section": chunk_type,
                "content": chunk_text,
                "embedding": embedding,
                "tags": []
            }

            docs_to_index.append(document)

            print(f"[IndexAgent] Chunk {idx+1}/{len(chunks)} preparado.")

        # Enviar para o Azure Search
        response = index_chunks(docs_to_index)

        print(f"[IndexAgent] Indexação concluída.")
        print(f"[IndexAgent] Azure Search retornou: {response}")

        return {
            "status": "success",
            "chunks_indexed": len(docs_to_index),
            "file": file_name
        }
