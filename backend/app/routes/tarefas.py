from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

# Importa os moldes de validação (Schemas) e a conexão com o banco de dados
from app.schemas.tarefa import Tarefa, TarefaCriacao, TarefaAtualizacao
from app.database import get_db


# Roteador para as tarefas
# 'prefix' define que a URL base deste arquivo será sempre /tarefas
router = APIRouter(
    prefix="/tarefas",
    tags=["Tarefas"]
)

# PEGAR TODAS AS TAREFAS DE UM PROJETO ESPECÍFICO
# response_model garante que a saída seja formatada como uma lista de Tarefas
@router.get("/projeto/{projeto_id}", response_model=list[Tarefa])
def listar_tarefas_do_projeto(projeto_id: int, dados=Depends(get_db)):
    
    # RealDictCursor faz o banco devolver os dados como dicionário (ideal para JSON)
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O %s substitui a variável com segurança, evitando ataques de SQL Injection
    cursor.execute(
        "SELECT * FROM tarefas WHERE projeto_id = %s ORDER BY id;", 
        (projeto_id,)
    )

    # fetchall() captura todas as linhas que o banco encontrou
    tarefas = cursor.fetchall()

    cursor.close()

    # Retornamos a lista. Se não tiver nenhuma tarefa, ele retorna uma lista vazia: []
    return tarefas


# ROTA PARA CRIAR UMA NOVA TAREFA (POST)
@router.post("/", response_model=Tarefa)
def criar_tarefa(tarefa: TarefaCriacao, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O banco gera o 'id' e coloca 'Pendente' no status automaticamente!
    # O comando RETURNING devolve a linha recém-criada (evita fazer um SELECT logo depois)
    cursor.execute(
        """
        INSERT INTO tarefas (titulo, projeto_id) 
        VALUES (%s, %s) 
        RETURNING id, titulo, status, projeto_id;
        """,
        (tarefa.titulo, tarefa.projeto_id)
    )

    # fetchone() captura a única linha que o RETURNING devolveu
    nova_tarefa = cursor.fetchone()

    # Confirma e salva a inserção de fato no banco de dados
    dados.commit()

    cursor.close()

    return nova_tarefa


# DELETA UMA TAREFA ESPECÍFICA DO BANCO DE DADOS
@router.delete("/{tarefa_id}")
def excluir_tarefa(tarefa_id: int, dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # deleta a tarefa onde o ID da tarefa seja igual ao tarefa_id que veio na URL
    cursor.execute(
        "DELETE FROM tarefas WHERE id = %s RETURNING id;",
        (tarefa_id,)
    )

    tarefa_deletada = cursor.fetchone()

    dados.commit()

    cursor.close()

    # Se a variável estiver vazia, levanta um erro 404 (Não Encontrado) para o frontend
    if not tarefa_deletada:
        raise HTTPException(
            status_code=404,
            detail="Tarefa não encontrada."
        )

    return {"mensagem": "Tarefa excluída com sucesso!"}


# ATUALIZA UMA TAREFA NO BANCO DE DADOS (Título ou Status)
@router.put("/{tarefa_id}", response_model=Tarefa)
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: TarefaAtualizacao, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O comando UPDATE altera apenas a linha onde o id bate com a URL
    cursor.execute(
        """
        UPDATE tarefas
        SET titulo = %s, status = %s
        WHERE id = %s
        RETURNING id, titulo, status, projeto_id;
        """,
        (tarefa_atualizada.titulo, tarefa_atualizada.status, tarefa_id)
    )

    tarefa_editada = cursor.fetchone()

    # Como é uma alteração no banco, precisamos do commit
    dados.commit()

    cursor.close()

    # Se o banco não devolveu nada, é porque o id não existe
    if not tarefa_editada:
        raise HTTPException(
            status_code=404,
            detail="Tarefa não encontrada."
        )

    return tarefa_editada