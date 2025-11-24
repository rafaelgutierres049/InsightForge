from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str


class SourceChunk(BaseModel):
    id: str
    file_name: Optional[str] = None
    section: Optional[str] = None
    score: Optional[float] = None
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []


class UploadResponse(BaseModel):
    filename: str
    status: str
