# InsightForge
## Intelligent RAG Platform powered by Azure AI

InsightForge is a production-ready **Retrieval-Augmented Generation (RAG)** platform for intelligent document analysis. It transforms PDFs, DOCX, and TXT files into queryable knowledge accessible through a natural language chat interface.

Built as an applied AI engineering solution using the full Azure AI stack:
- Azure OpenAI (GPT-4o + embeddings)
- Azure AI Document Intelligence (layout-aware extraction)
- Azure AI Search (vector + semantic + hybrid)
- Azure Blob Storage with SAS token security
- FastAPI backend + Streamlit frontend
- Multi-agent orchestration architecture

---

## Demo

**Upload**
<img src="prints/BlobUploadFile.gif" width="600">

**Document Management**
<img src="prints/BlobFiles.png" width="600">

**RAG Chat**
<img src="prints/ChatRAG.gif" width="600">

---

## Business Problem

Organizations dealing with large volumes of documents — contracts, technical manuals, compliance policies, financial reports — face significant friction when extracting specific information. Traditional keyword search misses semantic meaning, and manual review is slow and expensive.

**InsightForge solves this by:**

- Ingesting any document (PDF, DOCX, TXT) into a searchable, semantically-aware knowledge base
- Enabling users to query documents in plain natural language and receive accurate, cited answers
- Grounding every response strictly in indexed document content, eliminating hallucination risk
- Providing full source attribution so every answer can be traced back to the original document and section

**Target use cases:** legal teams reviewing contracts, compliance officers searching policies, engineers querying technical documentation, analysts extracting insights from reports.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             INSIGHTFORGE                                     │
├──────────────────────────────┬──────────────────────────────────────────────┤
│      INGESTION PIPELINE      │              RAG QUERY PIPELINE               │
│                              │                                               │
│  User                        │  User Question                                │
│   │                          │        │                                      │
│   ▼                          │        ▼                                      │
│  Streamlit UI                │  Streamlit Chat                               │
│   │                          │        │                                      │
│   ▼                          │        ▼                                      │
│  FastAPI  /upload            │  FastAPI  /chat/rag                           │
│   │                          │        │                                      │
│   ▼                          │        ▼                                      │
│  Azure Blob Storage          │  AgentOrchestrator                            │
│   │                          │    ├──► SearchAgent                           │
│   ▼                          │    │      ├─ Azure OpenAI Embeddings          │
│  IndexAgent                  │    │      └─ Azure AI Search                  │
│   ├─ Document Intelligence   │    │           (hybrid: vector + semantic)    │
│   ├─ Text Cleaner            │    │                                          │
│   ├─ Chunker                 │    └──► AnswerAgent                           │
│   │   ├─ Section Detection   │             └─ GPT-4o (Azure OpenAI)         │
│   │   └─ Fixed Overlap       │                  (temperature = 0.1)         │
│   ├─ Azure OpenAI Embeddings │                                               │
│   └─ Azure AI Search Index   │  Answer + Sources → Streamlit                │
└──────────────────────────────┴──────────────────────────────────────────────┘
```

---

## Features

- Upload documents (PDF, DOCX, TXT) via a Streamlit UI
- Secure storage in **Azure Blob Storage** with automatic SAS token generation
- Layout-aware text extraction using **Azure AI Document Intelligence** (handles scanned PDFs and tables)
- Text cleaning and normalization pipeline (unicode, whitespace, table borders)
- Hybrid chunking strategy: semantic section detection + fixed-size overlapping chunks
- Vector embedding generation via **Azure OpenAI** (`text-embedding-ada-002`)
- Indexing in **Azure AI Search** with:
  - Vector search (HNSW)
  - Semantic search (BM25 + reranking)
  - Hybrid search (combines all three, best overall recall and precision)
- Natural language Q&A over documents using a full **RAG pipeline**
- Multi-agent architecture:
  - **IndexAgent** — document processing and indexing
  - **SearchAgent** — hybrid retrieval with SAS-URL generation
  - **AnswerAgent** — grounded answer generation with GPT-4o
  - **AgentOrchestrator** — coordinates agents and consolidates the response
- ChatGPT-style chat interface with source attribution and document links
- Document deletion with automatic chunk removal from the search index

---

## How It Works

### 1. Document Ingestion Pipeline

```
User uploads file (Streamlit)
        │
        ▼
Azure Blob Storage              ← file stored securely
        │
        ▼
Azure Document Intelligence     ← extracts text, layout, tables
        │
        ▼
Text Cleaner                    ← unicode normalization, noise removal
        │
        ▼
Chunker
  ├── Section Detection         ← regex-based header matching
  │       └── Semantic Chunks   ← keyword-grouped sections
  └── Fixed Chunking (fallback) ← 800-word windows, 100-word overlap
        │
        ▼
Azure OpenAI Embeddings         ← text-embedding-ada-002
        │
        ▼
Azure AI Search                 ← vector + semantic index ready for queries
```

### 2. RAG Query Pipeline

```
User question (Streamlit Chat)
        │
        ▼
AgentOrchestrator
  ├── SearchAgent
  │       ├── Azure OpenAI Embeddings  ← embed the question
  │       ├── Azure AI Search          ← hybrid search (vector + semantic + BM25)
  │       └── SAS URL generation       ← per-chunk document links
  │
  └── AnswerAgent
          ├── Build grounded prompt    ← context + strict anti-hallucination rules
          └── GPT-4o (temp=0.1)        ← deterministic, source-bound answer
                  │
                  ▼
        Answer + Sources → Streamlit
```

### 3. Agent Responsibilities

| Agent | Responsibility |
|---|---|
| `IndexAgent` | Full document processing: extraction → cleaning → chunking → embeddings → indexing |
| `SearchAgent` | Hybrid search with vector fallback, SAS URL generation per result chunk |
| `AnswerAgent` | Grounded answer generation with GPT-4o; returns fixed fallback if context is insufficient |
| `AgentOrchestrator` | Coordinates SearchAgent and AnswerAgent, consolidates the final JSON response |

---

## Technical Decisions

### Hybrid Search over pure vector search
Azure AI Search's hybrid mode combines BM25 (keyword-based) with HNSW vector similarity and applies semantic reranking on top. This outperforms pure vector search on short, keyword-heavy queries (dates, names, codes, identifiers) while maintaining strong performance on semantic/conceptual queries. Vector-only search struggles with exact matches; BM25-only misses paraphrases — hybrid handles both.

### Dual chunking strategy
Documents are first split by detected section headers (regex patterns for `SECTION`, `CHAPTER`, `TÍTULO`, numbered headings, etc.), preserving the document's logical structure. Sections that don't match any header pattern fall back to fixed-size chunks of 800 words with 100-word overlap, ensuring no context is lost at chunk boundaries.

### Azure Document Intelligence over simple PDF parsers
Document Intelligence preserves layout, handles scanned PDFs via OCR, and correctly extracts multi-column text and tables — scenarios where simple parsers like PyMuPDF or pdfplumber produce broken or unordered text. This is critical for legal documents and technical reports.

### Temperature 0.1 for AnswerAgent
The near-zero temperature ensures deterministic, grounded responses. The AnswerAgent prompt explicitly instructs GPT-4o to return a fixed fallback string when context is insufficient, making it easy to detect and measure unanswered queries without any creative deviation.

### Score threshold filtering (≥ 0.031)
Search results below the relevance threshold are discarded before being sent to the AnswerAgent. This prevents low-quality or unrelated chunks from diluting the context window and causing the model to generate loosely-grounded answers.

### Agent architecture over a monolithic pipeline
Separating concerns into specialized agents (Index, Search, Answer, Orchestrator) makes the system modular: each agent can be tested, replaced, or upgraded independently. The `SearchAgent` can swap backends; the `AnswerAgent` can switch models — without touching the orchestration layer.

---

## Security Considerations

### Credentials management
- All Azure credentials (API keys, connection strings) are stored in `.env` and never committed to version control
- `.env` is excluded via `.gitignore`
- **Production recommendation**: store secrets in **Azure Key Vault** and retrieve them at runtime via Managed Identity — eliminates key rotation risk and removes secrets from the environment entirely

### SAS Tokens for document access
- Document blobs are never exposed with a public URL. The system generates **time-limited SAS tokens** (Shared Access Signatures) for each access request
- Tokens expire automatically, preventing stale or unauthorized long-lived access

### Credentials not exposed to the frontend
- The Streamlit frontend communicates only with the FastAPI backend, which acts as a secure proxy
- Azure API keys and connection strings are never forwarded to the browser

### Input handling
- User queries are passed as plain strings to the search index and to GPT-4o; no shell execution, SQL, or dynamic code evaluation occurs
- Document uploads are validated by file extension before processing

### Production hardening recommendations
- Enable **Azure Private Endpoints** for Blob Storage, AI Search, and Azure OpenAI to restrict access to your VNet
- Add API authentication to FastAPI endpoints (Azure AD OAuth2 or a shared API key header)
- Enable **Azure Monitor** and **Diagnostic Logs** on all services for audit trails
- Rotate API keys regularly and use Azure Key Vault references where possible

---

## Evaluation

Quality measurement is critical for RAG systems. InsightForge applies the following evaluation strategy:

### Retrieval quality
| Signal | How it's measured |
|---|---|
| Relevance threshold | Results below score 0.031 are filtered out before answer generation |
| Search mode logging | `SearchAgent` logs whether hybrid, vector fallback, or semantic was used per query |
| Context coverage | Manual spot-checks confirm retrieved chunks contain the information needed to answer |

### Answer quality
| Signal | How it's measured |
|---|---|
| Grounding | AnswerAgent returns a fixed fallback message when context is insufficient — unanswered rate is directly measurable |
| Source attribution | Every response includes source chunks + document names for human verification |
| Determinism | Temperature 0.1 minimizes stochastic deviation from the retrieved context |

### Recommended next steps for systematic evaluation
Integrate **RAGAS** or **Azure AI Evaluation** to compute automated metrics on a golden dataset:

- `answer_relevancy` — does the answer address the question?
- `context_precision` — are the top-K retrieved chunks relevant?
- `faithfulness` — is every claim in the answer grounded in the retrieved context?

Build a golden Q&A dataset from representative documents and run automated evaluation in CI on every prompt or pipeline change.

---

## Q&A Examples

The following examples illustrate the system behavior when documents are indexed:

**Q: What was the company's total revenue in Q3?**
> Based on the financial report, total revenue in Q3 reached R$ 4.2 billion, representing a 12% year-over-year increase. *(Source: relatorio_q3.pdf — Resultados Financeiros)*

**Q: What are the minimum system requirements for installation?**
> The installation requires Windows 10 or later, 8 GB RAM minimum, and 20 GB of free disk space. A stable internet connection is required for license activation. *(Source: manual_instalacao.pdf — Requisitos do Sistema)*

**Q: Who is the technical lead for the infrastructure project?**
> The infrastructure project is led by Eng. Ana Lima, designated as Technical Responsible on page 3 of the project scope document. *(Source: escopo_projeto.pdf — Equipe Técnica)*

**Q: What are the penalties for contract breach?**
> According to the contract terms, breach of delivery deadlines incurs a daily fine of 0.5% of the contract value, limited to a maximum of 10% of the total amount. *(Source: contrato_servicos.pdf — Cláusulas de Penalidade)*

**Q: (information not in any indexed document)**
> "I could not find this information in the documents."

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Pydantic, Uvicorn |
| Frontend | Streamlit |
| LLM | Azure OpenAI — GPT-4o |
| Embeddings | Azure OpenAI — text-embedding-ada-002 |
| Document Parsing | Azure AI Document Intelligence |
| Search Index | Azure AI Search (vector + semantic + hybrid) |
| Object Storage | Azure Blob Storage |
| Security | Azure SAS Tokens, `.env`-based secrets |

---

## Installation

### Prerequisites

- Python 3.11+
- Azure subscription with the following services provisioned:
  - Azure Blob Storage (container created)
  - Azure AI Document Intelligence
  - Azure OpenAI (GPT-4o and embedding model deployments)
  - Azure AI Search (index with vector field configured)

### Local setup

```bash
git clone https://github.com/rafaelgutierres049/InsightForge
cd InsightForge
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file at the project root:

```env
# Azure Blob Storage
AZURE_BLOB_CONNECTION_STRING=
AZURE_BLOB_CONTAINER_NAME=
AZURE_BLOB_ACCOUNT=
AZURE_BLOB_KEY=

# Azure Document Intelligence
AZURE_DI_ENDPOINT=
AZURE_DI_API_KEY=
AZURE_DI_MODEL_ID=

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
AZURE_OPENAI_GPT4O_DEPLOYMENT=
AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT=

# Azure AI Search
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=
AZURE_SEARCH_SEMANTIC_CONFIG=
AZURE_SEARCH_VECTOR_DIMENSION=1536

# App config
FRONTEND_URL=http://localhost:8501
APP_ENV=development
```

### Run locally

```bash
# Terminal 1 — Backend
uvicorn backend.app:app --reload

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

Backend available at `http://localhost:8000`  
Frontend available at `http://localhost:8501`

### Run with Docker Compose

```bash
cp .env.example .env   # fill in your Azure credentials
docker compose up --build
```

Backend: `http://localhost:8000` | Frontend: `http://localhost:8501`

---

### Running tests

```bash
pip install pytest
pytest tests/ -v
```

---

## License

MIT License.

## Author

Rafael Gutierres — AI Engineer  
[LinkedIn](https://linkedin.com/in/rafaelgutierres)
