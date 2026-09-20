from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from app.schemas.projeto import Projeto, ProjetoCriacao
from app.database import get_db


router = APIRouter(prefix="/projetos", tags=["Projetos"])


# PEGAR TODAS AS INFORMAÇÕES DO BANCO DE DADOS PODENDO EXIBIR
@router.get("/")
def listar_projetos(dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM projetos ORDER BY id;")

    projetos = cursor.fetchall()

    cursor.close()

    return projetos


# CRIA NOVOS ITENS NO BANCO DE DADOS
@router.post("/")
def criar_projeto(projeto: ProjetoCriacao, dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "INSERT INTO projetos (nome) VALUES (%s) RETURNING id, nome;",
        (projeto.nome,)
    )

    novo_projeto = cursor.fetchone()

    dados.commit()

    cursor.close()

    return novo_projeto


# DELETA ITENS NO BANCO DE DADOS
@router.delete("/{projeto_id}")
def excluir_projeto(projeto_id: int,dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "DELETE FROM projetos WHERE id = %s RETURNING id;",
        (projeto_id,)
    )

    projeto_deletado = cursor.fetchone()

    dados.commit()

    cursor.close()

    if not projeto_deletado:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return {"mensagem": "Projeto excluído com sucesso!"}


# ATUALIZA ITENS NO BANCO DE DADOS
@router.put("/{projeto_id}")
def atualizar_projeto(projeto_id: int,projeto_atualizado: ProjetoCriacao,dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        """
        UPDATE projetos
        SET nome = %s
        WHERE id = %s
        RETURNING id, nome;
        """,
        (projeto_atualizado.nome, projeto_id)
    )

    projeto_editado = cursor.fetchone()

    dados.commit()

    cursor.close()

    if not projeto_editado:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return projeto_editado


# PEGAR UM ÚNICO PROJETO PELO ID
@router.get("/{projeto_id}")
def obter_projeto(projeto_id: int, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM projetos WHERE id = %s;", (projeto_id,))

    projeto = cursor.fetchone()

    cursor.close()

    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return projeto