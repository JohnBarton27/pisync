from pydantic import BaseModel


class LedPatternUpdateRequest(BaseModel):

    db_id: int
    name: str
