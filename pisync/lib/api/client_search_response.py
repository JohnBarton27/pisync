from pydantic import BaseModel
from typing import List

from pisync.lib.api.common.client import Client


class ClientSearchResponse(BaseModel):

    clients: List[Client]
