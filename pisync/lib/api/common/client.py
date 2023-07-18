from pydantic import BaseModel


class Client(BaseModel):

    hostname: str
    ip_address: str

    def __eq__(self, other):
        if not isinstance(other, Client):
            return False

        return self.hostname == other.hostname

    def __hash__(self):
        return hash(self.hostname)
