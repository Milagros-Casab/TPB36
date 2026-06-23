import sqlite3
from interfaces.login import *

from models.database import *
from models.date import *


# instalar rich con "pip install -r requierements.txt"



if __name__ == '__main__':



    # pueden comentar esta parte para probar cosas y asi.
    try:
        flujo_login()
    except KeyboardInterrupt:
        console.print(f"\n\n  [dim {GRIS_SUB}]Sesión cancelada. ¡Hasta pronto! ⚽[/]\n")
        sys.exit(0)
    print("test")
#
