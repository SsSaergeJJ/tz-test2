from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MessageModel(BaseModel):
    username: str
    text: str
    timestamp: Optional[datetime] = None
    
