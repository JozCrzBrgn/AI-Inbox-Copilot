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