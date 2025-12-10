import psycopg2
import os
from urllib.parse import urlparse

def get_connection():
    # Tenta pegar DATABASE_URL (formato do Render)
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Parse da URL para psycopg2
        url = urlparse(database_url)
        
        # Para Render PostgreSQL
        conn_params = {
            "host": url.hostname,
            "database": url.path[1:],  # Remove a barra inicial
            "user": url.username,
            "password": url.password,
            "port": url.port or 5432,
        }
        
        # Conexão com SSL para Render
        return psycopg2.connect(**conn_params, sslmode='require')
    else:
        # Fallback para variáveis separadas
        return psycopg2.connect(
            host=os.getenv("dpg-d4ffejk9c44c73boc8hg-a.oregon-postgres.render.com"),
            dbname=os.getenv("beer_jp8s"),
            user=os.getenv("admin"),
            password=os.getenv("FvNx1g2vewP6487FkJ1z0eItBLJe5joR"),
            port=os.getenv("5432")
        )