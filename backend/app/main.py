from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  

from app.routes import projetos
from app.routes import tarefas

app = FastAPI(title="ProjectHub API")

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"], 
    
    allow_credentials=True,
    
    allow_methods=["*"], 
    
    allow_headers=["*"], 
)
# ==========================================

app.include_router(projetos.router)
app.include_router(tarefas.router)

@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo à API do ProjectHub!"}