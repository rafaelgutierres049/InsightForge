from ..agents.search_agent import SearchAgent
from ..agents.answer_agent import AnswerAgent


class AgentOrchestrator:

    def __init__(self):
        self.search_agent = SearchAgent()
        self.answer_agent = AnswerAgent()

    def answer_query(self, query: str, k: int = 5):
        print("\n[Orchestrator] ===== Novo fluxo RAG iniciado =====")
        print(f"[Orchestrator] Pergunta: {query}")

        # recuperar contextos
        search_result = self.search_agent.retrieve(query, k=k)
        contexts = search_result["contexts"]
        mode = search_result["mode"]

        print(f"[Orchestrator] Contextos recuperados: {len(contexts)} (modo: {mode})")

        # gerar resposta com GPT-4o
        answer_result = self.answer_agent.answer(query, contexts)

        print("[Orchestrator] Resposta gerada com sucesso.")

        # montar saída final no formato padrão
        return {
            "query": query,
            "mode": mode,
            "answer": answer_result["answer"],
            "sources": [
                {
                    "id": c["id"],
                    "file_name": c["file_name"],
                    "section": c.get("section", ""),
                    "score": c.get("score", 0),
                    "blob_url": c.get("blob_url"),
                }
                for c in contexts
            ],
        }