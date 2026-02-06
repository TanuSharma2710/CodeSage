from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DebugRequest(BaseModel):
    code: str
    error_message: str
    language: str = "python"
    expected_output: Optional[str] = None


class CodeFix(BaseModel):
    line_number: int
    original:str        
    fixed:str 
    explanation:str


class DebugResponse(BaseModel):
    diagnosis: str
    mistakes: List[str]
    fixes: List[CodeFix]
    fixed_code: str
    changed_lines: List[int] = []  # Line numbers that AI changed
    study_topics: List[str]
    session_id: Optional[int] = None


class DebugSessionResponse(BaseModel):
    id: int
    code: str
    error_message: str
    language: str
    diagnosis: Optional[str]
    fixed_code: Optional[str]
    study_topics: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DebugHistoryResponse(BaseModel):
    sessions: List[DebugSessionResponse]
    total: int
