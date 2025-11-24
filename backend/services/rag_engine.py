import os
from typing import List, Dict, Any

from dotenv import load_dotenv

from backend.services.embeddings import generate_embedding, get_openai_client
from backend.services.search import hybrid_search
from backend.services.azure_blob import generate_sas_url

load_dotenv()

AZURE_OPENAI_GPT4O_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT")
AZURE_BLOB_ACCOUNT = os.getenv("AZURE_BLOB_ACCOUNT")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER_NAME")


# Recuperar contexto do Azure Search
def retrieve_context(query: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Usa hybrid search (vetorial + semantic) para recuperar
    os chunks mais relevantes do índice.
    Retorna lista de dicts com conteúdo, metadados e URL do blob.
    """
    query_embedding = generate_embedding(query)
    results = hybrid_search(query_text=query, query_embedding=query_embedding, k=top_k)

    contexts: List[Dict[str, Any]] = []

    for r in results:

        blob_url = generate_sas_url(r.get("file_name"))
        print("Generated SAS URL for blob:", blob_url)

        doc = {
            "id": r.get("id"),
            "file_name": r.get("file_name"),
            "section": r.get("section"),
            "content": r.get("content"),
            "score": getattr(r, "score", None),
            "blob_url": blob_url,  
        }

        contexts.append(doc)

    return contexts



# Montar prompt para o GPT-4o
def build_prompt(query: str, contexts: List[Dict[str, Any]]) -> str:
    """
    Concatena os contextos em um bloco único, com instruções claras
    para o modelo responder com base **apenas** nesses trechos.
    """
    context_blocks = []
    for i, c in enumerate(contexts):
        header = f"[TRECHO {i+1} | arquivo={c.get('file_name')} | seção={c.get('section')}]"
        block = f"{header}\n{c.get('content')}"
        context_blocks.append(block)

    joined_context = "\n\n".join(context_blocks)

    prompt = f"""
Você é o assistente do sistema InsightForge. 
Responda SEMPRE em português, mesmo que o texto original esteja em outro idioma.

Você DEVE seguir estas regras:

1. Use apenas as informações dos trechos de contexto abaixo.
2. Se a resposta não estiver clara no contexto, diga:
   "Não encontrei essa informação nos documentos."
3. Quando possível, cite explicitamente de qual trecho veio a informação (ex: "No trecho 2, o documento diz que...").
4. Seja objetivo, mas completo. Use bullet points quando fizer sentido.

---------------- CONTEXTO INÍCIO ----------------
{joined_context}
---------------- CONTEXTO FIM ----------------

Pergunta do usuário:
{query}

Agora, gere uma resposta em português com base SOMENTE no contexto acima.
"""
    return prompt.strip()


# Gerar resposta com GPT-4o
def generate_answer(query: str, contexts: List[Dict[str, Any]]) -> str:
    client = get_openai_client()
    prompt = build_prompt(query, contexts)

    response = client.chat.completions.create(
        model=AZURE_OPENAI_GPT4O_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente de RAG chamado InsightForge. Responda sempre em português e jamais invente informações."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=800,
    )

    return response.choices[0].message.content


# Função única de RAG (entrada → saída)
def rag_answer(query: str) -> Dict[str, Any]:
    """
    Pipeline de consulta completo:
    1. Recupera contexto (Azure Search)
    2. Gera resposta (GPT-4o)
    3. Retorna resposta + fontes
    """
    contexts = retrieve_context(query)

    if not contexts:
        return {
            "answer": "Não encontrei informações relevantes nos documentos para responder essa pergunta.",
            "sources": [],
        }

    answer = generate_answer(query, contexts)

    sources = []
    for c in contexts:
        sources.append(
            {
                "id": c.get("id") or "",
                "file_name": c.get("file_name"),
                "section": c.get("section"),
                "score": c.get("score"),
                "content": c.get("content") or "",
                "blob_url": c.get("blob_url"),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }
