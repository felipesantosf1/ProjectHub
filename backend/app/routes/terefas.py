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