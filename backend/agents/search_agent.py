from ..services.embeddings import generate_embedding
from ..services.search import hybrid_search, vector_search
from ..services.azure_blob import get_blob_url, generate_sas_url

class SearchAgent:

    def retrieve(self, query: str, k: int = 5):
        print(f"\n[SearchAgent] Iniciando busca para: {query}")

        # embedding da pergunta
        embedding = generate_embedding(query)

        # tenta Hybrid Search
        try:
            print("[SearchAgent] Executando Hybrid Search...")
            results = hybrid_search(query, embedding, k=k)
            mode = "hybrid"
        except Exception as e:
            print(f"[SearchAgent] Hybrid Search falhou ({e}). Tentando Vector Search...")
            results = vector_search(embedding, k=k)
            mode = "vector"

        contexts = []

        for r in results:
            file_name = r.get("file_name", "")
            section = r.get("section", "")
            score = r.get("@search.score", 0)

            blob_url = generate_sas_url(file_name) if file_name else None
            
            ctx = {
                "id": r["id"],
                "file_name": file_name,
                "section": section,
                "score": score,
                "content": r.get("content", ""),
                "blob_url": blob_url,
            }
            contexts.append(ctx)

        print(f"[SearchAgent] Total de contextos retornados: {len(contexts)} (modo: {mode})")

        return {
            "mode": mode,
            "query": query,
            "contexts": contexts,
        }