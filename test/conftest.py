import os

# La app construye el engine al importarse. Las pruebas no deben abrir MySQL.
os.environ["DATABASE_URL"] = "sqlite://"
