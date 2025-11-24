import re
import unicodedata

def clean_text(text: str) -> str:
    # Remove caracteres estranhos
    text = unicodedata.normalize("NFKC", text)

    # Remove múltiplos espaços
    text = re.sub(r"[ \t]+", " ", text)

    # Remove múltiplas quebras de linha
    text = re.sub(r"\n{2,}", "\n", text)

    # Remove bordas e colunas de tabelas
    text = re.sub(r"[││─┼]+", "", text)

    # Remove sequências numéricas soltas (ex: números de página)
    text = re.sub(r"\n\d+\n", "\n", text)

    # Limpa espaços no início/fim
    text = text.strip()

    return text
