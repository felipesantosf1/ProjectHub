from pydantic import BaseModel


class ProjetoCriacao(BaseModel):
    nome: str


class Projeto(BaseModel):
    id: int
    nome: str