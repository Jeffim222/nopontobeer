import psycopg2
import os
def get_connection():
    return psycopg2.connect(
        host=os.getenv("dpg-d4ffejk9c44c73boc8hg-a.oregon-postgres.render.com"),
        dbname=os.getenv("beer_jp8s"),
        user=os.getenv("admin"),
        password=os.getenv("FvNx1g2vewP6487FkJ1z0eItBLJe5joR"),
        port=os.getenv("5432")
    )