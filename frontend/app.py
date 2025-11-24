import streamlit as st
import requests

API_URL = "http://localhost:8000"

def list_files():
    resp = requests.get(f"{API_URL}/upload/list_uploads")
    if resp.status_code != 200:
        return []
    return resp.json().get("files", [])


def upload_document(file):
    url = f"{API_URL}/upload/upload"
    files = {"file": (file.name, file.read(), file.type)}
    resp = requests.post(url, files=files)
    return resp.json()


def ask_question(query, mode="hybrid"):
    url = f"{API_URL}/chat/rag"
    resp = requests.post(url, json={"query": query, "mode": mode})
    return resp.json()


def delete_file(file_name):
    url = f"{API_URL}/upload/delete/{file_name}"
    resp = requests.delete(url)
    return resp.json()


# ===========================================
# CONFIGURAÇÃO DO LAYOUT 
# ===========================================
st.set_page_config(
    page_title="InsightForge",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
/* Background geral */
body {
    background-color: #0f0f0f;
    color: white;
}

/* Header */
h1, h2, h3 {
    color: #d6d6d6 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1c1c1c !important;
    border-right: 1px solid #333 !important;
}

/* Botões */
.stButton>button {
    background-color: #3b3d42 !important;
    color: white !important;
    border-radius: 6px !important;
    border: 1px solid #444 !important;
}

/* Input do chat */
input[type="text"] {
    background-color: #2b2b2b !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid #444 !important;
}
</style>
""", unsafe_allow_html=True)


# ===========================================
# SIDEBAR – MENU
# ===========================================
st.sidebar.title("InsightForge")

menu = st.sidebar.radio(
    "Navegação",
    [
        "Início",
        "Arquivos no Blob",
        "Upload de Documento",
        "Chat com RAG"
    ]
)

if menu == "Início":
    st.title("🔍 InsightForge – Sobre o Projeto")
    st.markdown("""
    O **InsightForge** é uma plataforma de análise inteligente de documentos construída para transformar PDFs, DOCX, TXT e outros arquivos
    em conhecimento pesquisável e acessível por meio de um chat interativo baseado em RAG (*Retrieval Augmented Generation*).

    A solução integra armazenamento em nuvem, extração de conteúdo, geração de embeddings, indexação vetorial e busca semântica através
    de serviços avançados da Microsoft Azure. Com isso, o InsightForge funciona como uma espécie de **ChatGPT treinado exclusivamente nos seus documentos**.

    ---

    ## 🧩 Como o InsightForge funciona

    ### 🖥️ **Frontend (Streamlit)**
    A interface do InsightForge é construída com Streamlit, oferecendo:
    - Navegação clara pelo menu lateral.
    - Visualização dos documentos armazenados no Azure Blob.
    - Upload simples de novos arquivos.
    - Chat no estilo ChatGPT, com histórico e respostas em tempo real.
    - Comunicação direta com o backend via API REST.

    ---

    ### ⚙️ **Backend (FastAPI)**
    O backend utiliza FastAPI e é organizado em módulos profissionais:
    - **Upload**: recebe os arquivos e envia para o Blob Storage.
    - **Document Processor**: extrai texto, limpa e realiza chunking.
    - **OpenAI Embeddings**: cria vetores de similaridade.
    - **Azure Search Engine**: realiza buscas semânticas, vetoriais e híbridas.
    - **RAG Engine**: compõe os trechos relevantes e gera respostas com GPT.
    - **Orchestrator e Agents**: coordenam todo fluxo de busca e resposta.

    Arquivos importantes no backend:
    - `azure_blob.py` – comunicação com Azure Blob
    - `document_intelligence.py` – extração com Azure Document Intelligence
    - `chunker.py` – divisão em chunks
    - `embeddings.py` – geração de embeddings
    - `search.py` – consultas ao Azure AI Search
    - `rag_pipeline.py` – pipeline completo de RAG
    - `rag_engine.py` – execução lógica do RAG
    - `chat.py` – rota principal do chat

    ---

    ## ☁️ Como os serviços Azure são utilizados

    ### 🔹 **Azure Blob Storage**
    Armazena todos os documentos enviados pelo usuário.
    O acesso é privado e seguro; o backend realiza o download via streaming.

    ### 🔹 **Azure Document Intelligence**
    Extrai automaticamente o texto do documento, detectando:
    - estrutura
    - seções
    - conteúdo organizável

    ### 🔹 **Azure OpenAI**
    Usado para:
    - geração de embeddings vetoriais
    - respostas inteligentes baseadas no contexto recuperado
    - entendimento avançado da pergunta do usuário

    ### 🔹 **Azure AI Search**
    É o núcleo do RAG:
    - Armazena os chunks
    - Indexa vetores (HNSW)
    - Faz busca semântica e vetorial combinada
    - Seleciona os trechos mais relevantes para resposta

    ---

    ## 🧠 Pipeline completo (como uma pergunta vira resposta)

    1. Você envia uma pergunta pelo chat.
    2. O **Orchestrator** aciona o SearchAgent.
    3. O SearchAgent realiza *Hybrid Search* no Azure Search.
    4. Os trechos mais relevantes são recuperados.
    5. O AnswerAgent usa o GPT-4o para gerar uma resposta fundamentada.
    6. O frontend exibe a resposta no formato de chat.

    ---

    ## 📂 Pipeline completo de documentos (upload → conhecimento)

    1. Upload do arquivo pelo frontend.
    2. Backend envia o arquivo para o Blob.
    3. Document Intelligence extrai o texto.
    4. O texto é limpo e dividido em chunks.
    5. Embeddings são gerados.
    6. Tudo é indexado no Azure AI Search.
    7. Documento pronto para ser consultado via chat.

    ---

    ## 🚀 Use o menu lateral para navegar:
    - **Início**: visão geral do sistema  
    - **Arquivos no Blob**: visualize e gerencie documentos  
    - **Upload de Documento**: envie novos arquivos para indexação  
    - **Chat com RAG**: consulte seus documentos com IA

    Explore seus dados e descubra insights reais usando IA + Azure.
    """)



# ===========================================
# LISTAR ARQUIVOS
# ===========================================
if menu == "Arquivos no Blob":
    st.header("Arquivos armazenados no Azure Blob Storage")

    files = list_files()

    if not files:
        st.warning("Nenhum arquivo foi enviado ainda.")
    else:
        for f in files:

            col1, col2 = st.columns([6, 1])

            with col1:
                st.markdown(
                    f"<span style='font-size:16px;'>{f['name']}</span>",
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("Excluir", key=f"delete_{f['name']}"):
                    resp = delete_file(f["name"])
                    if resp.get("status") == "success":
                        st.success(f"Arquivo '{f['name']}' deletado.")
                        st.rerun()
                    else:
                        st.error(f"Erro ao excluir o arquivo '{f['name']}'.")

            st.markdown("<hr style='margin-top:6px; margin-bottom:6px;'>",
                        unsafe_allow_html=True)


# ===========================================
# UPLOAD
# ===========================================
elif menu == "Upload de Documento":
    st.header("Enviar novo documento")

    file = st.file_uploader("Selecione um PDF, TXT ou DOCX",
                            type=["pdf", "txt", "docx"])

    if file:
        st.info("Processando upload e indexação...")

        resp = upload_document(file)

        if resp.get("status") == "success":
            st.success(f"Arquivo '{resp['file']}' enviado e indexado!")
            st.json(resp)
        else:
            st.error("Falha ao indexar o arquivo:")
            st.json(resp)


# ===========================================
# CHAT RAG 
# ===========================================
elif menu == "Chat com RAG":
    st.header("Chat com RAG baseado nos documentos")

    if "history" not in st.session_state:
        st.session_state.history = []

    chat_container = st.container()

    with chat_container:
        for entry in st.session_state.history:

            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-end; margin:6px 0;">
                    <div style="
                        background-color:#3b3d42;
                        padding:10px 14px;
                        border-radius:14px;
                        max-width:60%;
                        font-size:16px;
                        color:white;
                    ">
                        {entry['query']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-start; margin:6px 0;">
                    <div style="
                        background-color:#1e1e1e;
                        padding:10px 14px;
                        border-radius:14px;
                        max-width:75%;
                        font-size:17px;
                        color:white;
                        line-height:1.6;
                    ">
                        {entry['answer']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if "sources" in entry and entry["sources"]:
                st.markdown(
                    "<div style='font-size:14px; color:#bfbfbf; margin:4px 0 0 6px;'>Fontes utilizadas:</div>",
                    unsafe_allow_html=True
                )

                good_sources = [src for src in entry["sources"] if src["score"] and src["score"] >= 0.031]

                for src in good_sources:
                    st.markdown(
                        f"""
                        <div style="margin:4px 0 4px 12px;">
                            <a href="{src['blob_url']}" target="_blank" style="color:#6aa9ff; text-decoration:none;">
                                {src['file_name']}
                            </a>
                            <span style="color:#888;"> (score: {src['score']:.4f})</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    st.markdown("---")

    with st.container():
        col1, col2 = st.columns([0.86, 0.14])

        with col1:
            user_query = st.text_input(
                "",
                placeholder="Digite uma pergunta...",
                key="chatbox",
                label_visibility="collapsed"
            )

        with col2:
            enviar = st.button("Enviar")

        if enviar and user_query.strip():
            with st.spinner("Pensando..."):
                resp = ask_question(user_query)

            st.session_state.history.append({
                "query": user_query,
                "answer": resp.get("answer", "Erro ao gerar resposta."),
                "sources": resp.get("sources", [])   # ⬅ ESSENCIAL
            })

            st.rerun()
