from pydantic import BaseModel
from enum import Enum  # 1. Importamos a ferramenta de Enum do Python

# 2. Criamos a nossa lista de múltipla escolha
# Dizemos que ela é baseada em 'str' (textos) e é um 'Enum'
class StatusTarefa(str, Enum):
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"

class TarefaCriacao(BaseModel):
    titulo: str
    projeto_id: int

class TarefaAtualizacao(BaseModel):
    titulo: str
    # 3. Aqui está a mágica! Trocamos 'str' pela nossa classe 'StatusTarefa'
    status: StatusTarefa

class Tarefa(BaseModel):
    id: int
    titulo: str
    status: str
    projeto_id: int