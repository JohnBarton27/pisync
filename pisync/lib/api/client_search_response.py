from pydantic import BaseModel
from typing import List


class Client(BaseModel):

    hostname: str
    ip_address: str


class ClientSearchResponse(BaseModel):

    clients: List[Client]
