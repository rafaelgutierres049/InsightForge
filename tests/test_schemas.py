import pytest
from pydantic import ValidationError
from backend.models.schemas import ChatRequest, ChatResponse, SourceChunk, UploadResponse


class TestChatRequest:
    def test_valid_query(self):
        req = ChatRequest(query="What is the total revenue?")
        assert req.query == "What is the total revenue?"

    def test_empty_query_is_allowed(self):
        req = ChatRequest(query="")
        assert req.query == ""

    def test_missing_query_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ChatRequest()


class TestSourceChunk:
    def test_minimal_required_fields(self):
        chunk = SourceChunk(id="abc123", content="some extracted text")
        assert chunk.id == "abc123"
        assert chunk.content == "some extracted text"

    def test_optional_fields_default_to_none(self):
        chunk = SourceChunk(id="abc123", content="text")
        assert chunk.file_name is None
        assert chunk.section is None
        assert chunk.score is None

    def test_all_fields_set(self):
        chunk = SourceChunk(
            id="abc123",
            file_name="report.pdf",
            section="Financial Results",
            score=0.95,
            content="revenue grew 20%",
        )
        assert chunk.file_name == "report.pdf"
        assert chunk.section == "Financial Results"
        assert chunk.score == 0.95

    def test_missing_required_content_raises_error(self):
        with pytest.raises(ValidationError):
            SourceChunk(id="abc123")

    def test_missing_required_id_raises_error(self):
        with pytest.raises(ValidationError):
            SourceChunk(content="some text")


class TestChatResponse:
    def test_answer_with_sources(self):
        sources = [
            SourceChunk(id="1", content="text one"),
            SourceChunk(id="2", content="text two"),
        ]
        resp = ChatResponse(answer="The answer is 42.", sources=sources)
        assert resp.answer == "The answer is 42."
        assert len(resp.sources) == 2

    def test_sources_default_to_empty_list(self):
        resp = ChatResponse(answer="No data found.")
        assert resp.sources == []

    def test_missing_answer_raises_error(self):
        with pytest.raises(ValidationError):
            ChatResponse()


class TestUploadResponse:
    def test_valid_upload_response(self):
        resp = UploadResponse(filename="report.pdf", status="indexed")
        assert resp.filename == "report.pdf"
        assert resp.status == "indexed"

    def test_missing_filename_raises_error(self):
        with pytest.raises(ValidationError):
            UploadResponse(status="indexed")

    def test_missing_status_raises_error(self):
        with pytest.raises(ValidationError):
            UploadResponse(filename="report.pdf")
