from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from app.schemas.projeto import Projeto, ProjetoCriacao
from app.database import get_db

# Roteador para os projetos
# 'prefix' define que a URL base deste arquivo será sempre /projetos
router = APIRouter(prefix="/projetos", tags=["Projetos"])


# PEGAR TODAS AS INFORMAÇÕES DO BANCO DE DADOS
# response_model garante que a saída seja formatada como uma lista de Projetos
@router.get("/", response_model=list[Projeto])
def listar_projetos(dados=Depends(get_db)):

    # RealDictCursor faz o banco devolver os dados como dicionário (ideal para JSON)
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM projetos ORDER BY id;")

    # fetchall() captura todas as linhas que o banco encontrou
    projetos = cursor.fetchall()

    cursor.close()

    return projetos


# CRIA NOVOS ITENS NO BANCO DE DADOS
@router.post("/", response_model=Projeto)
def criar_projeto(projeto: ProjetoCriacao, dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O %s substitui a variável com segurança, evitando ataques de SQL Injection
    # O comando RETURNING devolve a linha recém-criada (evita fazer um SELECT logo depois)
    cursor.execute(
        "INSERT INTO projetos (nome) VALUES (%s) RETURNING id, nome;",
        (projeto.nome,)
    )

    # fetchone() captura a única linha que o RETURNING devolveu
    novo_projeto = cursor.fetchone()

    # Confirma e salva a inserção de fato no banco de dados
    dados.commit()

    cursor.close()

    return novo_projeto


# DELETA ITENS NO BANCO DE DADOS
@router.delete("/{projeto_id}")
def excluir_projeto(projeto_id: int, dados=Depends(get_db)):

    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # Deleta o projeto onde o ID seja igual ao projeto_id que veio na URL
    cursor.execute(
        "DELETE FROM projetos WHERE id = %s RETURNING id;",
        (projeto_id,)
    )

    projeto_deletado = cursor.fetchone()

    dados.commit()

    cursor.close()

    # Se a variável estiver vazia, levanta um erro 404 (Não Encontrado) para o frontend
    if not projeto_deletado:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return {"mensagem": "Projeto excluído com sucesso!"}


# ATUALIZA ITENS NO BANCO DE DADOS
@router.put("/{projeto_id}", response_model=Projeto)
def atualizar_projeto(projeto_id: int, projeto_atualizado: ProjetoCriacao, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O comando UPDATE altera apenas a linha onde o id bate com a URL
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

    # Como é uma alteração no banco, precisamos do commit
    dados.commit()

    cursor.close()

    # Se o banco não devolveu nada, é porque o id não existe
    if not projeto_editado:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return projeto_editado


# PEGAR UM ÚNICO PROJETO PELO ID
@router.get("/{projeto_id}", response_model=Projeto)
def obter_projeto(projeto_id: int, dados=Depends(get_db)):
    
    cursor = dados.cursor(cursor_factory=RealDictCursor)

    # O %s garante que a busca seja feita de forma segura passando o id da URL
    cursor.execute("SELECT * FROM projetos WHERE id = %s;", (projeto_id,))

    # Pega apenas o projeto específico que foi encontrado
    projeto = cursor.fetchone()

    cursor.close()

    # Se não encontrou o projeto, avisa o frontend com erro 404
    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        )

    return projeto