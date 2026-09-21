from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  

from app.routes import projetos
from app.routes import tarefas

# Inicializa a aplicação FastAPI e define o título que aparece lá no topo do Swagger (/docs)
app = FastAPI(title="ProjectHub API")

# CONFIGURAÇÃO DE CORS
# Permite que o Frontend (HTML/JS rodando no navegador) se comunique com o Backend sem ser bloqueado por segurança.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Libera requisições de qualquer origem (ideal para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"], # Libera todos os métodos HTTP (GET, POST, PUT, DELETE)
    allow_headers=["*"], # Libera todos os cabeçalhos de requisição
)

# REGISTRO DE ROTAS (ROUTERS)
# Puxa todas as rotas de projetos e tarefas para dentro da aplicação principal
app.include_router(projetos.router)
app.include_router(tarefas.router)

# ROTA RAIZ (Página inicial da API)
@app.get("/")
def raiz():
    # Retorna uma mensagem simples para confirmar que o servidor está vivo e rodando
    return {"mensagem": "Bem-vindo à API do ProjectHub!"}