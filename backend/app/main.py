import os

from dotenv import load_dotenv
import psycopg2

from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

def get_db_connection():

    dados = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    return dados


class ProjetoCriacao(BaseModel):
    nome: str

class Projeto(BaseModel):
    id: int
    nome: str

@app.get("/")
def inicio():
    return {"mensagem": "ProjectHub API funcionando!"}

# PEGA AS INFORMAÇÕES DO BANCO DE DADOS
@app.get("/projetos")
def listar_projetos():
    dados = get_db_connection()
    # RealDictCursor faz o banco retornar dicionários {"id": 1, "nome": "..."} em vez de tuplas
    cursor = dados.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM projetos ORDER BY id;")
    projetos = cursor.fetchall()
    
    cursor.close()
    dados.close()
    return projetos

# CRIA NOVOS ITENS NO BANCO DE DADOS
@app.post("/projetos")
def criar_projeto(projeto: ProjetoCriacao):
    dados = get_db_connection()
    cursor = dados.cursor(cursor_factory=RealDictCursor)
    
    # O PostgreSQL gera o ID automaticamente graças ao IDENTITY que configuramos!
    cursor.execute(
        "INSERT INTO projetos (nome) VALUES (%s) RETURNING id, nome;",
        (projeto.nome,)
    )
    novo_projeto = cursor.fetchone()
    
    dados.commit() # Salva a alteração no banco
    cursor.close()
    dados.close()
    
    return novo_projeto

# DELETA INFORMAÇÕES DO BANCO DE DADOS
@app.delete("/projetos/{projeto_id}")
def excluir_projeto(projeto_id: int):
    dados = get_db_connection()
    cursor = dados.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "DELETE FROM projetos WHERE id = %s RETURNING id;",
        (projeto_id,)
    )
    projeto_deletado = cursor.fetchone()
    
    dados.commit()
    cursor.close()
    dados.close()

    if not projeto_deletado:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    return {"mensagem": "Projeto excluído com sucesso!"}

# ATUALIZA INFORMAÇÕES DENTRO DO BANCO DE DADOS
@app.put("/projetos/{projeto_id}")
def atualizar_projeto(projeto_id: int, projeto_atualizado: ProjetoCriacao):
    dados = get_db_connection()
    cursor = dados.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "UPDATE projetos SET nome = %s WHERE id = %s RETURNING id, nome;",
        (projeto_atualizado.nome, projeto_id)
    )
    projeto_editado = cursor.fetchone()
    
    dados.commit()
    cursor.close()
    dados.close()

    if not projeto_editado:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    return projeto_editado