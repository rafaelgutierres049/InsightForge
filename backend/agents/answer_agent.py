from openai import AzureOpenAI
from dotenv import load_dotenv
import os
load_dotenv()


class AnswerAgent:

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-06-01"
        )
        self.model = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT")

    def _build_prompt(self, query: str, contexts: list):
        
        context_text = "\n\n".join(
            f"[Fonte {i+1}]\n{ctx['content']}" for i, ctx in enumerate(contexts)
        )

        prompt = f"""
        Você é um assistente de IA especializado em RAG (Retrieval Augmented Generation).

        REGRAS IMPORTANTES:
        - Responda apenas com base no contexto fornecido.
        - Se a informação não estiver no contexto, responda exatamente: 
        "Não encontrei essa informação nos documentos."
        - Não invente nem faça suposições.
        - Seja objetivo, claro e direto.
        - Use português brasileiro.
        - Inclua apenas informações 100% presentes nas fontes.

        ### Pergunta do usuário:
        {query}

        ### Contexto recuperado:
        {context_text}

        ### Sua resposta:
        """
        return prompt

    def answer(self, query: str, contexts: list):

        if not contexts:
            return {
                "answer": "Não encontrei essa informação nos documentos.",
                "sources": []
            }

        prompt = self._build_prompt(query, contexts)

        print("[AnswerAgent] Chamando GPT-4o...")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um assistente RAG altamente confiável."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        answer_text = response.choices[0].message.content

        return {
            "answer": answer_text,
            "sources": contexts
        }
