from typing import Optional

from pydantic import BaseModel


class EmailAnalizerResquest(BaseModel):
    email_content: str


class EmailAnalizerResponse(BaseModel):
    customer_name: str
    intent: str
    summary: str
    priority: str
    sentiment: str
    suggested_subject: str
    suggested_reply: str


class EmailResponse(BaseModel):
    id: int
    date: Optional[str]
    customer_name: str
    intent: str
    priority: str
    sentiment: str
    summary: str
    reply: str