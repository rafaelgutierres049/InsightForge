import re

# DETECÇÃO DE SEÇÕES
def detect_sections(text: str):
    lines = text.split("\n")

    sections = []
    current_title = "INTRODUCAO"
    current_content = []

    title_pattern = re.compile(
        r"^(CAP[IÍ]TULO|SE[CÇ][AÃ]O|SECTION|CHAPTER|T[IÍ]TULO|INTRODUÇÃO|CONCLUSÃO|RESUMO|[0-9]+\.)",
        re.IGNORECASE
    )

    for line in lines:
        if title_pattern.match(line.strip()):
            if current_content:
                sections.append((current_title, "\n".join(current_content)))
            current_title = line.strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append((current_title, "\n".join(current_content)))

    return sections


# CHUNKING FIXO (fallback)
def fixed_chunking(text: str, max_tokens=800, overlap=100):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + max_tokens
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks


# CHUNKING SEMÂNTICO LEVE
def semantic_chunking(sections):
    output = []

    keyword_groups = {
        "financeiro": ["faturamento", "lucro", "receita", "crescimento"],
        "custos": ["custos", "despesas", "gastos"],
        "investimentos": ["investimento", "infraestrutura", "automação", "IA"],
    }

    for title, content in sections:
        for group, kws in keyword_groups.items():
            if any(kw in content.lower() for kw in kws):
                output.append(f"[{group.upper()}] {title}\n{content}")
                break

    return output
