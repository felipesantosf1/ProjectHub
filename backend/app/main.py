from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ProjetoCriacao(BaseModel):
    nome: str


class Projeto(BaseModel):
    id: int
    nome: str

# {"id": 1, "nome": "Projeto Baja"}
projetos = []


@app.get("/")
def inicio():
    return {"mensagem": "ProjectHub API funcionando!"}


@app.get("/projetos")
def listar_projetos():
    return projetos


@app.post("/projetos")
def criar_projeto(projeto: ProjetoCriacao):

    novo_id = len(projetos) + 1

    novo_projeto = Projeto(
        id=novo_id,
        nome=projeto.nome
    )

    projetos.append(novo_projeto.model_dump())

    return novo_projeto

@app.delete("/projetos/{projeto_id}")
def excluir_projeto(projeto_id: int):

    for projeto in projetos:
        if projeto["id"] == projeto_id:
            projetos.remove(projeto)
            return {"mensagem": "Projeto excluído com sucesso!"}

    return {"mensagem": "Projeto não encontrado."}