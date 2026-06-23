#=================================================#
#                                                 #
#     models.database (mantenido por Obregon)     #
#                                                 #
#      Todas las funciones necesarias que         #
#       usan la base de datos están aquí.         #
#                                                 #
#=================================================#

import sqlite3
import hashlib

database_file = "data.db"

conn = sqlite3.connect(database_file)
conn.row_factory = sqlite3.Row

db = conn.cursor()



def process_password(password):

	hash_object = hashlib.blake2b(password.encode('utf-8'))

	return hash_object.hexdigest()

#



# =========================================
#    Manejo de cuentas de usuario
# =========================================



def read_user(email):

	data = db.execute(f'SELECT * FROM ACCOUNTS WHERE EMAIL = "{email}";').fetchone()

	if data is None:
		class ret:
			email=False
			password=False

		return ret

	class ret:
		email = data["EMAIL"]
		password= data["PASSWORD"]

	return ret

#



def create_user(email, password):

	hash_password = process_password(password)

	if read_user(email).email==False:
		try:
			conn.execute(f'INSERT INTO ACCOUNTS VALUES("{email}", "{hash_password}");')
			conn.commit();

		except sqlite3.Error:
			return False

		return True

	return False
#



def purge_user(email):

	if read_user(email)!=False:
		try:
			conn.execute(f'DELETE FROM ACCOUNTS WHERE EMAIL="{email}"')
			conn.commit();

		except sqlite3.Error:
			return False

		return True

	return False



def login_user(email, password):

	hash_password = process_password(password)

	if read_user(email).email != False:

		if(read_user(email).password == hash_password):
			return True

	return False
#



# =========================================
#    Manejo de eventos
# =========================================



def read_event(ev_name):

	data = db.execute(f'SELECT * FROM EVENTS WHERE NAME="{ev_name}";').fetchone()

	if data is None:
		class ret:
			name=False
			place=False
			campo_price=0
			campo_stock=0
			campo_price=0
			campo_stock=0

		return ret

	class ret:
		name= data["NAME"]
		place= data["PLACE"]
		campo_price=data["CAMPO_PRICE"]
		campo_stock=data["CAMPO_STOCK"]
		platea_price=data["PLATEA_PRICE"]
		platea_stock=data["PLATEA_STOCK"]

	return ret




def create_event(name, place, campo_price, campo_stock, platea_price, platea_stock):

	if read_event(name).name==False:
		try:
			conn.execute(f'INSERT INTO EVENTS VALUES("{name}", "{place}", {campo_price}, {campo_stock}, {platea_price}, {platea_stock});')
			conn.commit();

		except sqlite3.Error:
			return False		# False on SQL error

		return True			# True if correctly executed

	return False			# False if event already exists


def purge_event(name):

	ev = read_event(name)

	if ev.name!=False:
		try:
			conn.execute(f'DELETE FROM EVENTS WHERE NAME="{name}"')
			conn.commit();

		except sqlite3.Error:
			return False

		return True

	return False



def list_event(part):

	data = db.execute('SELECT * FROM EVENTS;').fetchall()


	class ret:
		name =         []
		place =        []
		campo_price =  []
		campo_stock =  []
		platea_price = []
		platea_stock = []

	for row in data:
		ret.name.append(row["NAME"])
		ret.place.append(row["PLACE"])
		ret.campo_price.append(row["CAMPO_PRICE"])
		ret.campo_stock.append(row["CAMPO_STOCK"])
		ret.platea_price.append(row["PLATEA_PRICE"])
		ret.platea_stock.append(row["PLATEA_STOCK"])

	return ret



#
#
#



def create_ticket(event, user, price, date, platea):

	selected_event = db.execute(f'SELECT * FROM EVENTS WHERE NAME="{event}";').fetchone()
	stock = 0


	if(platea == 1): stock = db.execute(f'SELECT PLATEA_STOCK FROM EVENTS WHERE NAME="{event}";').fetchone()["PLATEA_STOCK"]
	else: stock = db.execute(f'SELECT CAMPO_STOCK FROM EVENTS WHERE NAME="{event}";').fetchone()["CAMPO_STOCK"]


	if stock == None:
		return False

	if stock>0 :
		try:
			conn.execute(f'INSERT INTO TICKETS VALUES("{event}", "{user}", {price}, "{date}", {platea});')
			conn.commit()

		except sqlite3.Error:
			return False

		else:
			if(platea == 1):
				conn.execute(f'UPDATE EVENTS SET PLATEA_STOCK=(PLATEA_STOCK-1) WHERE NAME="{event}";')
				conn.commit()
			else:
				conn.execute(f'UPDATE EVENTS SET CAMPO_STOCK=(CAMPO_STOCK-1) WHERE NAME="{event}";')
				conn.commit()

		return True

