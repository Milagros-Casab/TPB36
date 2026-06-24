#=================================================#
#                                                 #
#      Todas las funciones necesarias que         #
#       usan la base de datos están aquí.         #
#                                                 #
#=================================================#

import sqlite3
import hashlib
from models.date import to_unix

# Configuración de la base de datos
database_file = "data.db"
conn = sqlite3.connect(database_file)
conn.row_factory = sqlite3.Row

def process_password(password):
	hash_object = hashlib.blake2b(password.encode('utf-8'))
	return hash_object.hexdigest()

# =========================================
#    Manejo de cuentas de usuario
# =========================================

def read_user(email):
	data = conn.execute('SELECT * FROM ACCOUNTS WHERE EMAIL = ?;', (email,)).fetchone()
	class ret:
		email = False
		password = False
	
	res = ret()
	if data:
		res.email = data["EMAIL"]
		res.password = data["PASSWORD"]
	return res

def create_user(email, password):
	hash_password = process_password(password)
	if read_user(email).email is False:
		try:
			conn.execute('INSERT INTO ACCOUNTS VALUES(?, ?);', (email, hash_password))
			conn.commit()
			return True
		except sqlite3.Error:
			return False
	return False

def purge_user(email):
	if read_user(email).email is not False:
		try:
			conn.execute('DELETE FROM ACCOUNTS WHERE EMAIL = ?;', (email,))
			conn.commit()
			return True
		except sqlite3.Error:
			return False
	return False

def login_user(email, password):
	user = read_user(email)
	if user.email is not False:
		return user.password == process_password(password)
	return False

# =========================================
#    Manejo de eventos
# =========================================

def read_event(ev_name):
	data = conn.execute('SELECT * FROM EVENTS WHERE NAME = ?;', (ev_name,)).fetchone()
	class ret:
		name = False
		place = False
		campo_price = 0
		campo_stock = 0
		platea_price = 0
		platea_stock = 0
		date = 0
		discount_code = ""
		discount_pct = 0
	
	res = ret()
	if data:
		res.name = data["NAME"]
		res.place = data["PLACE"]
		res.campo_price = data["CAMPO_PRICE"]
		res.campo_stock = data["CAMPO_STOCK"]
		res.platea_price = data["PLATEA_PRICE"]
		res.platea_stock = data["PLATEA_STOCK"]
		res.date = data["DATE"]
		# Compatibilidad por si se lee una fila vieja sin estas columnas
		keys = data.keys()
		res.discount_code = data["DISCOUNT_CODE"] if "DISCOUNT_CODE" in keys else ""
		res.discount_pct = data["DISCOUNT_PCT"] if "DISCOUNT_PCT" in keys else 0
	return res

# CORRECCIÓN AQUÍ: Ahora acepta 9 parámetros con valores por defecto
def create_event(name, place, campo_price, campo_stock, platea_price, platea_stock, date, discount_code="", discount_pct=0):
	if read_event(name).name is False:
		try:
			conn.execute(
				'INSERT INTO EVENTS VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);',
				(name, place, campo_price, campo_stock, platea_price, platea_stock, to_unix(date), discount_code, discount_pct)
			)
			conn.commit()
			return True
		except sqlite3.Error:
			return False
	return False

def purge_event(name):
	if read_event(name).name is not False:
		try:
			conn.execute('DELETE FROM EVENTS WHERE NAME = ?;', (name,))
			conn.commit()
			return True
		except sqlite3.Error:
			return False
	return False

def list_event(part):
	data = conn.execute('SELECT * FROM EVENTS;').fetchall()
	class ret:
		pass
	
	res = ret()
	res.name = [row["NAME"] for row in data]
	res.place = [row["PLACE"] for row in data]
	res.campo_price = [row["CAMPO_PRICE"] for row in data]
	res.campo_stock = [row["CAMPO_STOCK"] for row in data]
	res.platea_price = [row["PLATEA_PRICE"] for row in data]
	res.platea_stock = [row["PLATEA_STOCK"] for row in data]
	res.date = [row["DATE"] for row in data]
	
	keys = data[0].keys() if data else []
	res.discount_code = [row["DISCOUNT_CODE"] if "DISCOUNT_CODE" in keys else "" for row in data]
	res.discount_pct = [row["DISCOUNT_PCT"] if "DISCOUNT_PCT" in keys else 0 for row in data]
	return res

# =========================================
#    Manejo de tickets
# =========================================

def create_ticket(event, user, price, date, platea):
	col_stock = "PLATEA_STOCK" if platea == 1 else "CAMPO_STOCK"
	row = conn.execute(f'SELECT {col_stock} FROM EVENTS WHERE NAME = ?;', (event,)).fetchone()
	
	if row and row[col_stock] > 0:
		try:
			conn.execute('INSERT INTO TICKETS VALUES(?, ?, ?, ?, ?);', (event, user, price, date, platea))
			conn.execute(f'UPDATE EVENTS SET {col_stock} = {col_stock} - 1 WHERE NAME = ?;', (event,))
			conn.commit()
			return True
		except sqlite3.Error:
			return False
	return False

def list_tickets(user):
	data = conn.execute('SELECT * FROM TICKETS WHERE USER = ?;', (user,)).fetchall()
	class ret:
		pass
	
	res = ret()
	res.event = [row["EVENT"] for row in data]
	res.user = [row["USER"] for row in data]
	res.price = [row["PRICE"] for row in data]
	res.date = [row["DATE"] for row in data]
	res.platea = [row["PLATEA"] for row in data]
	return res
