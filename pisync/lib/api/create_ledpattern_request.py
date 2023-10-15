from charset_normalizer.md import Optional
from pydantic import BaseModel


class CreateLedPatternRequest(BaseModel):

    name: str
    client_id: Optional[int]
