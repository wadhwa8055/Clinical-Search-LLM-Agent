from pydantic import BaseModel, Field
from typing import Optional
import uuid

class UserQuery(BaseModel):
    query: str
    thread_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))