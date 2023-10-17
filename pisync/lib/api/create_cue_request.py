from typing import Optional

from pydantic import BaseModel


class CreateCueRequest(BaseModel):

    name: str
    sourceMediaId: int
    sourceMediaTimecode: float
    targetMediaId: Optional[int] = None
    targetPatternId: Optional[int] = None
