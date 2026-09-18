from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor

from app.schemas.projeto import Projeto, ProjetoCriacao
from app.database import get_db_connection


router = APIRouter(
    prefix="/projetos",
    tags=["Projetos"]
)

# PEGAR TODAS AS INFORMAÇÕES DO BANCO DE DADOS PODENDO EXIBIR
@router.get("/")
def listar_projetos():
    dados = get_db_connection()

    cursor = dados.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM projetos ORDER BY id;")

    projetos = cursor.fetchall()

    cursor.close()
    dados.close()

    return projetos

# CRIA NOVOS ITENS NO BANCO DE DADOS
@router.post("/")
def criar_projeto(projeto: ProjetoCriacao):
    dados = get_db_connection()

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "INSERT INTO projetos (nome) VALUES (%s) RETURNING id, nome;",
        (projeto.nome,)
    )

    novo_projeto = cursor.fetchone()

    dados.commit()

    cursor.close()
    dados.close()

    return novo_projeto

# DELETA ITENS NO BANCO DE DADOS
@router.delete("/{projeto_id}")
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
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return {"mensagem": "Projeto excluído com sucesso!"}

# ATUALIZA ITENS NO BANCO DE DADOS
@router.put("/{projeto_id}")
def atualizar_projeto(
    projeto_id: int,
    projeto_atualizado: ProjetoCriacao
):
    dados = get_db_connection()

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
    dados.close()

    if not projeto_editado:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return projeto_editado