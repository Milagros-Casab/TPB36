#=================================================#
#                                                 #
#              models.sales_database              #
#              para aplicar ofertas.              #
#                                                 #
#=================================================#



import sqlite3

from models.database import *

database_file = "data.db"

conn = sqlite3.connect(database_file)
conn.row_factory = sqlite3.Row

db = conn.cursor()



# CODE:string   is the promo code
# TYPE:integer  the discount type
# VALUE:integer the discount value (what it means changes from each type)
# EVENT:string  associated event to each code


#	DISCOUNT TYPES:
#	0: percentage discount
#	1: literal discount

def create_sale(code, sale_type, value, event):
	code=code.upper()

	if read_event(event).name!=False:
		try:
			conn.execute(f'INSERT INTO SALES VALUES("{code}", {sale_type}, {value}, "{event}");')
			conn.commit()

		except sqlite3.Error:
			return 0		# False on SQL error

		return True			# True if correctly executed

	return 1			# False if event already exists
#



def read_sale(code, event):
	code=code.upper()

	data = db.execute(f'SELECT * FROM SALES WHERE CODE="{code}" AND EVENT="{event}";').fetchone()

	if data is None:
		class ret:
			code=False
			type=-1
			value=0
			event=False

		return ret

	class ret:
		code = data["CODE"]
		type = data["TYPE"]
		value = data["VALUE"]
		event = data["EVENT"]

	return ret
#



def sales(event):

	return db.execute(f'SELECT COUNT(*) FROM SALES WHERE EVENT="{event}";').fetchone()[0]
	# if it returns "0" then there's no promo codes for it

#


def apply_sale(code, event, price):
	code=code.upper()

	if sales(event)>0:
		promo = read_sale(code, event)

		if(promo.event == event):

			match promo.type:
				case 0: return price * (1-(promo.value/100))
				case 1: return price - promo.value

	#
#
