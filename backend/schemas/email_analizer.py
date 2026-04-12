from typing import Literal, Optional

from pydantic import BaseModel


class EmailAnalizerResquest(BaseModel):
    email_content: str


class EmailAnalizerResponse(BaseModel):
    customer_name: str = "Unknown"
    intent: str
    summary: str
    priority: Literal["low", "medium", "high"]
    sentiment: Literal["positive", "neutral", "negative"]
    suggested_subject: str = ""
    suggested_reply: str = ""


class EmailResponse(BaseModel):
    id: int
    date: Optional[str]
    customer_name: Optional[str] = None
    intent: str
    priority: str
    sentiment: str
    summary: str
    reply: str
