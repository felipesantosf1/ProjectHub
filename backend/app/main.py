from fastapi import FastAPI

from app.routes.projetos import router as projetos_router


app = FastAPI()


@app.get("/")
def inicio():
    return {"mensagem": "ProjectHub API funcionando!"}


app.include_router(projetos_router)