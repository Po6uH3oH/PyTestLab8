from pydantic import BaseModel
from typing import Dict, Any

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]
