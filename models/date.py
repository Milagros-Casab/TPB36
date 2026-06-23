#=================================================#
#                                                 #
#       models.date (mantenido por Obregon)       #
#                                                 #
#    Para guardar y manejar fechas y horarios     #
#              gracias al UNIX Epoch              #
#                                                 #
#=================================================#


from datetime import datetime

time_format = "%d-%m-%Y %H:%M"



# Turns a date and hour into UNIX timestamp
def to_unix(date, hour):

	return int( datetime.strptime(date + " " + hour, time_format).timestamp() )
#



# Turns UNIX timestamp into a string
def from_unix(seconds):

	return datetime.fromtimestamp(seconds).strftime(time_format)
#
