import sqlite3
from interfaces.login import *

con = sqlite3.connect("data.db")
database = con.cursor()

# instalar rich con "pip install rich"
# en linux (probablemente) exija un argumento mas ""pip install rich --break-system-packages
import rich


if __name__ == '__main__':
    try:
        flujo_login()
    except KeyboardInterrupt:
        console.print(f"\n\n  [dim {GRIS_SUB}]Sesión cancelada. ¡Hasta pronto! ⚽[/]\n")
        sys.exit(0)

    print("test")
#

## un cambio
