import os
from pymongo import MongoClient

# Leemos la variable de entorno o usamos localhost por defecto
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/meditech_db')

client = MongoClient(MONGO_URI)
db = client.get_database() # Se conecta a la base de datos definida en la URI