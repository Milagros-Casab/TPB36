#=================================================#
#                                                 #
#              models.stats_event                 #
#         estadísticas de ventas de tickets.      #
#                                                 #
#=================================================#



import sqlite3

from models.database import *

database_file = "data.db"

conn = sqlite3.connect(database_file)
conn.row_factory = sqlite3.Row

db = conn.cursor()



def estadisticas_evento(event):

	data = db.execute(f'SELECT * FROM TICKETS WHERE EVENT="{event}";').fetchall()

	class ret:
		total_vendidas = 0
		recaudacion = 0
		campo_vendidas = 0
		platea_vendidas = 0
		campo_recaudacion = 0
		platea_recaudacion = 0

	for row in data:
		ret.total_vendidas += 1
		ret.recaudacion += row["PRICE"]

		if row["TYPE"] == 1:
			ret.platea_vendidas += 1
			ret.platea_recaudacion += row["PRICE"]
		else:
			ret.campo_vendidas += 1
			ret.campo_recaudacion += row["PRICE"]

	return ret
#
