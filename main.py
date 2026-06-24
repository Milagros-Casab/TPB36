import sqlite3
from interfaces.codigoEntradas import *

from models.database import *
from models.date import *


# instalar rich con "pip install -r requierements.txt"



if __name__ == '__main__':



    # pueden comentar esta parte para probar cosas y asi.
        inicializar_db()
        usuario_activo = pantalla_inicio()
        menu_principal()
#
