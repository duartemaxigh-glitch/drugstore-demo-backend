import os
from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(override=True)


db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', '5432'))
db_user=os.getenv('DB_USUARIO', 'postgres')
db_password=os.getenv('DB_PASSWORD', '')
db_name=os.getenv('DB_NOMBRE', 'drugstore')

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
)