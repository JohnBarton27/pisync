from pydantic import BaseModel


class ClientUpdateRequest(BaseModel):

    db_id: int
    name: str
    ip_address: str
