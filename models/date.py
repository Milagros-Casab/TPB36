#=================================================#
#                                                 #
#     models.date - utilidades de fecha           #
#                                                 #
#=================================================#

from datetime import datetime

FORMATO = "%d/%m/%Y %H:%M"

def to_unix(fecha_str):
	"""Convierte 'dd/mm/yyyy HH:MM' a timestamp unix (int)."""
	try:
		dt = datetime.strptime(fecha_str, FORMATO)
		return int(dt.timestamp())
	except (ValueError, TypeError):
		return 0


def from_unix(timestamp):
	"""Convierte timestamp unix (int) a 'dd/mm/yyyy HH:MM'."""
	try:
		return datetime.fromtimestamp(int(timestamp)).strftime(FORMATO)
	except (ValueError, TypeError, OSError):
		return False
