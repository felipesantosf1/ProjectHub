from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

# Importamos o molde que você acabou de criar
from app.schemas.tarefa import TarefaCriacao
from app.database import get_db


# Criamos um roteador específico para as tarefas
router = APIRouter(
    prefix="/tarefas",
    tags=["Tarefas"]
)


# ROTA PARA CRIAR UMA NOVA TAREFA (POST)
@router.post("/")
def criar_tarefa(tarefa: TarefaCriacao, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # Note que passamos apenas titulo e projeto_id.
    # O banco gera o 'id' e coloca 'Pendente' no status automaticamente!
    cursor.execute(
        """
        INSERT INTO tarefas (titulo, projeto_id) 
        VALUES (%s, %s) 
        RETURNING id, titulo, status, projeto_id;
        """,
        (tarefa.titulo, tarefa.projeto_id)
    )

    nova_tarefa = cursor.fetchone()

    # Como é um INSERT (escrita), precisamos do commit!
    dados.commit()

    cursor.close()

    return nova_tarefa


# PEGAR TODAS AS TAREFAS DE UM PROJETO ESPECÍFICO
@router.get("/projeto/{projeto_id}")
def listar_tarefas_do_projeto(projeto_id: int, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O segredo está aqui: pedimos tarefas ONDE o projeto_id seja igual ao que veio na URL
    cursor.execute(
        "SELECT * FROM tarefas WHERE projeto_id = %s ORDER BY id;", 
        (projeto_id,)
    )

    # Usamos fetchall() porque um projeto pode ter VÁRIAS tarefas (uma lista)
    tarefas = cursor.fetchall()

    cursor.close()

    # Retornamos a lista. Se não tiver nenhuma tarefa, ele retorna uma lista vazia: []
    # Isso é perfeitamente normal, significa apenas que o projeto ainda não tem tarefas.
    return tarefas


# DELETA UMA TAREFA ESPECÍFICA DO BANCO DE DADOS
@router.delete("/{tarefa_id}")
def excluir_tarefa(tarefa_id: int, dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # Agora sim: delete a tarefa onde o ID da tarefa seja igual ao tarefa_id que veio na URL
    cursor.execute(
        "DELETE FROM tarefas WHERE id = %s RETURNING id;",
        (tarefa_id,)
    )

    tarefa_deletada = cursor.fetchone()

    dados.commit()

    cursor.close()

    if not tarefa_deletada:
        raise HTTPException(
            status_code=404,
            detail="Tarefa não encontrada."
        )

    return {"mensagem": "Tarefa excluída com sucesso!"}