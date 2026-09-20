from pydantic import BaseModel

# Molde para quando o Frontend quiser CRIAR uma nova tarefa
class TarefaCriacao(BaseModel):
    titulo: str
    projeto_id: int

# Molde para quando o nosso Backend for DEVOLVER a tarefa para o Frontend
class Tarefa(BaseModel):
    id: int
    titulo: str
    status: str
    projeto_id: int

# Molde para quando o Frontend quiser ATUALIZAR uma tarefa
class TarefaAtualizacao(BaseModel):
    titulo: str
    status: str