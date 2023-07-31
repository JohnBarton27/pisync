from pydantic import BaseModel
from typing import Optional


class MediaUpdateRequest(BaseModel):

    db_id: int
    name: str
    start_time: Optional[float]
    end_time: Optional[float]
