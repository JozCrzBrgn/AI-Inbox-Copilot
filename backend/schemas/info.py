from pydantic import BaseModel


class InfoResponse(BaseModel):
    created_by: str
    description: str
    version: str