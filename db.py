import psycopg2
def get_connection():
    try:
        conn = psycopg2.connect(
            host="dpg-d4ffejk9c44c73boc8hg-a.oregon-postgres.render.com",
            database="beer_jp8s",
            user="admin",
            password="FvNx1g2vewP6487FkJ1z0eItBLJe5joR",
            port="5432",
            sslmode="require" 
        )
        print("✅ Conexão com banco estabelecida")
        return conn
    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        return None