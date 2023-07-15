from pydantic import BaseModel


class InfoResponse(BaseModel):

    is_client: bool = False
    is_server: bool = False
