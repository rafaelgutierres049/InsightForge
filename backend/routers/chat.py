from fastapi import APIRouter
from pydantic import BaseModel
from ..agents.agent_orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()

class ChatQuery(BaseModel):
    query: str

@router.post("/rag")
def chat_rag(payload: ChatQuery):
    result = orchestrator.answer_query(payload.query)
    return result