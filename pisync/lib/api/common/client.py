from pydantic import BaseModel


class Client(BaseModel):

    hostname: str
    ip_address: str
