from pydantic import BaseModel


class EmailAnalizerResquest(BaseModel):
    message: str

class EmailAnalizerResponse(BaseModel):
    success: bool
    message: str