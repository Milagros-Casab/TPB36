
import sqlite3
from interfaces.ticketMESSI_recitales import *

from models.database import *
from models.sales_database import *
from models.date import *


# instalar rich con "pip install -r requierements.txt"


"""
Punto de entrada de ticketMESSI — Sistema de recitales
"""

if __name__ == "__main__":
    create_database()
    main()




