from pydantic import BaseModel


class CueUpdateRequest(BaseModel):

    db_id: int
    name: str
    source_media_id: int
    source_media_timecode: float
    target_media_id: int
    is_enabled: bool
