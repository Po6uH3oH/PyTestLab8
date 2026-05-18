from pydantic import BaseModel
from typing import Optional

class ProfileSchema(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    middlename: Optional[str] = None
    birthdate: Optional[str] = None
    about: Optional[str] = None
    links: Optional[str] = None
