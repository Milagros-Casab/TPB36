import sqlite3
import hashlib

conn = sqlite3.connect("data.db")
conn.row_factory = sqlite3.Row
db = conn.cursor()

def process_password(password):

	hash_object = hashlib.blake2b(password.encode('utf-8'))

	return hash_object.hexdigest()

#


def read_user(email):

	data = db.execute(f'SELECT * FROM ACCOUNTS WHERE EMAIL = "{email}";').fetchone()

	if data is None:
		return False

	return data["EMAIL"], data["PASSWORD"]

#


def create_user(email, password):

	hash_password = process_password(password)

	if read_user(email)==False :
		try:
			conn.execute(f'INSERT INTO ACCOUNTS (EMAIL, PASSWORD) VALUES("{email}", "{hash_password}");')
			conn.commit();
			return True

		except sqlite3.Error as e:
			return False

		return False
	return False
#



def check_login(email, password):

	hash_password = process_password(password)

	if read_user(email)!=False :

		if(read_user(email)[1] == hash_password):
			return True

	return False
#
