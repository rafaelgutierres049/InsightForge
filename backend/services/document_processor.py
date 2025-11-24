from .document_intelligence import extract_text_from_blob
from .text_cleaner import clean_text
from .chunker import detect_sections, fixed_chunking, semantic_chunking


def process_document_for_rag(file_name: str) -> list[str]:
    """
    Extrai texto do blob, limpa, faz chunking híbrido
    e retorna lista final de chunks.
    """

    # Extrai texto via Document Intelligence
    raw_text = extract_text_from_blob(file_name)

    # Limpa texto
    clean = clean_text(raw_text)

    # Detecta seções
    sections = detect_sections(clean)

    structural_chunks = [
        f"[SEÇÃO: {title}]\n{content}"
        for title, content in sections
        if len(content.strip()) > 30
    ]

    # Chunking fixo (fallback)
    fallback_chunks = fixed_chunking(clean)

    # Chunking semântico leve
    semantic_chunks = semantic_chunking(sections)

    # Combina tudo e remove duplicatas
    final = []
    for c in structural_chunks + fallback_chunks + semantic_chunks:
        if c not in final and len(c.strip()) > 30:
            final.append(c)

    return final

