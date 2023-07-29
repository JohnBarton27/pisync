from pydantic import BaseModel


class CreateCueRequest(BaseModel):

    name: str
    sourceMediaId: int
    sourceMediaTimecode: int
    targetMediaId: int
