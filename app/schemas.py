from pydantic import BaseModel
from typing import Optional, List, Dict, Union, Any

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    company: str

class User(BaseModel):
    id: int
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class DocumentSchema(BaseModel):
    document_id: str
    mongo_collection: str

class Document(BaseModel):
    id: str
    title: str

class EditorData(BaseModel):
    time: int
    blocks: list
    version: str

class RenameTitleSchema(BaseModel):
    id: str
    title: str

class PromptSchema(BaseModel):
    prompt: str
