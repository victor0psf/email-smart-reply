from pydantic import BaseModel

class EmailResult(BaseModel):
    categoria: str
    resposta: str