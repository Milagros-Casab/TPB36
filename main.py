import sqlite3
from ticketMESSI_recitales import *

from models.database import *
from models.sales_database import *
from models.date import *


# instalar rich con "pip install -r requierements.txt"


"""
Punto de entrada de ticketMESSI — Sistema de Recitales.
"""

from ticketMESSI_recitales import inicializar_db, main

if __name__ == "__main__":
    inicializar_db()
    main()
