import pytest
from backend.services.chunker import detect_sections, fixed_chunking, semantic_chunking


class TestFixedChunking:
    def test_produces_multiple_chunks_for_long_text(self):
        text = " ".join(["word"] * 1000)
        chunks = fixed_chunking(text, max_tokens=100, overlap=10)
        assert len(chunks) > 1

    def test_each_chunk_respects_max_tokens(self):
        text = " ".join(["word"] * 500)
        chunks = fixed_chunking(text, max_tokens=100, overlap=10)
        assert all(len(chunk.split()) <= 100 for chunk in chunks)

    def test_short_text_returns_single_chunk(self):
        text = "short text here"
        chunks = fixed_chunking(text, max_tokens=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == "short text here"

    def test_overlap_causes_shared_words_between_chunks(self):
        words = [str(i) for i in range(200)]
        text = " ".join(words)
        chunks = fixed_chunking(text, max_tokens=50, overlap=10)
        # Last words of chunk N should appear at start of chunk N+1
        last_words = set(chunks[0].split()[-10:])
        first_words = set(chunks[1].split()[:10])
        assert len(last_words & first_words) > 0

    def test_empty_text_returns_empty_list(self):
        chunks = fixed_chunking("", max_tokens=100, overlap=10)
        assert chunks == []


class TestDetectSections:
    def test_detects_numbered_sections(self):
        text = "1. Introduction\nsome text\n2. Methods\nmore text"
        sections = detect_sections(text)
        titles = [s[0] for s in sections]
        assert any("1." in t for t in titles)

    def test_detects_section_keyword(self):
        text = "SECTION Overview\nsome overview text\nSECTION Details\ndetail text"
        sections = detect_sections(text)
        assert len(sections) >= 2

    def test_no_headers_returns_introducao_section(self):
        text = "a plain paragraph without any section headers at all"
        sections = detect_sections(text)
        assert len(sections) == 1
        assert sections[0][0] == "INTRODUCAO"

    def test_content_is_preserved_in_sections(self):
        text = "1. Overview\nThis is the overview content."
        sections = detect_sections(text)
        combined = " ".join(content for _, content in sections)
        assert "overview content" in combined


class TestSemanticChunking:
    def test_financial_keyword_match(self):
        sections = [("Revenue", "faturamento cresceu 20% no trimestre")]
        result = semantic_chunking(sections)
        assert len(result) == 1
        assert "FINANCEIRO" in result[0]

    def test_cost_keyword_match(self):
        sections = [("Expenses", "custos operacionais aumentaram este ano")]
        result = semantic_chunking(sections)
        assert len(result) == 1
        assert "CUSTOS" in result[0]

    def test_investment_keyword_match(self):
        sections = [("Invest", "investimento em infraestrutura foi aprovado")]
        result = semantic_chunking(sections)
        assert len(result) == 1
        assert "INVESTIMENTOS" in result[0]

    def test_no_keyword_match_returns_empty(self):
        sections = [("Random", "nothing relevant here in this text at all")]
        result = semantic_chunking(sections)
        assert len(result) == 0

    def test_multiple_sections_partial_match(self):
        sections = [
            ("Finance", "receita aumentou bastante"),
            ("Other", "unrelated content here"),
        ]
        result = semantic_chunking(sections)
        assert len(result) == 1
