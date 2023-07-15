from pydantic import BaseModel


class MediaUpdateRequest(BaseModel):

    db_id: int
    name: str
