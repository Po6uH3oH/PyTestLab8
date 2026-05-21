from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class ProfileSchema(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    middlename: Optional[str] = None
    birthdate: Optional[str] = None
    about: Optional[str] = None
    links: Optional[str] = None

class ProfilesListSchema(BaseModel):
    model_config = ConfigDict(extra='ignore')
    profiles: List[ProfileSchema]
    count: int
