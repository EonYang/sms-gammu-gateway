from pydantic import BaseModel


class SMS(BaseModel):
    date: str = ''
    number: str = ''
    state: str = ''
    text: str = ''
    spam: bool = False
