import os

import psycopg2

from dotenv import load_dotenv

load_dotenv()

# FUNÇÃO DE CONEXÃO DE BANCO DE DADOS
def get_db_connection():
    dados = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    return dados