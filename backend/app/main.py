from fastapi import FastAPI
from app.routes import projetos
from app.routes import tarefas  # 1. Importamos o novo arquivo de rotas

app = FastAPI(title="ProjectHub API")

# Incluímos as rotas de projetos (que você já tinha)
app.include_router(projetos.router)

# 2. Incluímos as rotas de tarefas (NOVO)
app.include_router(tarefas.router)

@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo à API do ProjectHub!"}










