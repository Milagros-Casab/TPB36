#!/usr/bin/env python3
"""
ticketMESSI — Sistema de Recitales
"""

import os
import sys
import time
import sqlite3
from pathlib import Path


from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.align import Align
from rich.rule import Rule
from rich import box
from rich.live import Live
from rich.spinner import Spinner

import models.database as database
import models.sales_database as sales_database

from models.date import from_unix

console = Console()

# ─── Paleta ────────────────────────────────────────────────────────────────
CELESTE  = "#75AADB"
DORADO   = "#F0C040"
BLANCO   = "#F5F5F5"
VERDE    = "#3CB371"
ROJO_ERR = "#E05050"
GRIS_SUB = "#888888"


usuario_activo = ""

# ─── Cuenta de administrador ───────────────────────────────────────────────
ADMIN_EMAIL = "admin@ticketmessi.com"

def es_admin() -> bool:
    return usuario_activo == ADMIN_EMAIL


# ═══════════════════════════════════════════════════════════════════════════
#  INICIALIZACION DE TABLAS
# ═══════════════════════════════════════════════════════════════════════════

def inicializar_db() -> None:
    database.conn.executescript("""
        CREATE TABLE IF NOT EXISTS ACCOUNTS (
            EMAIL    TEXT PRIMARY KEY,
            PASSWORD TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS EVENTS (
            NAME         TEXT PRIMARY KEY,
            PLACE        TEXT NOT NULL,
            CAMPO_PRICE  INTEGER NOT NULL,
            CAMPO_STOCK  INTEGER NOT NULL,
            PLATEA_PRICE INTEGER NOT NULL,
            PLATEA_STOCK INTEGER NOT NULL,
            DATE         INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS TICKETS (
            EVENT  TEXT NOT NULL,
            USER   TEXT NOT NULL,
            PRICE  INTEGER NOT NULL,
            DATE   TEXT NOT NULL,
            TYPE   INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS SALES (
            CODE  TEXT NOT NULL,
            TYPE  INTEGER NOT NULL,
            VALUE INTEGER NOT NULL,
            EVENT TEXT NOT NULL,
            PRIMARY KEY (CODE, EVENT)
        );
    """)

    database.conn.commit()


    # Crear cuenta de administrador si no existe
    if not database.login_user(ADMIN_EMAIL, "admin1234"):
        database.create_user(ADMIN_EMAIL, "admin1234")


# ═══════════════════════════════════════════════════════════════════════════
#  UTILIDADES UI
# ═══════════════════════════════════════════════════════════════════════════

def limpiar():
    console.clear()

def banner():
    titulo = Text()
    titulo.append("  ticket", style=f"bold {BLANCO}")
    titulo.append("MESSI", style=f"bold {DORADO}")
    titulo.append(" - Recitales  ", style=f"bold {BLANCO}")
    subtitulo = Text('El "10" de las entradas', style=f"italic {CELESTE}")
    stars = Text("* * * * * * *", style=DORADO)
    panel = Panel(
        Align.center(Text.assemble(titulo, "\n", subtitulo, "\n\n", stars)),
        border_style=CELESTE, box=box.DOUBLE_EDGE, padding=(1, 6),
    )
    console.print(panel)

def separador(texto: str = ""):
    if texto:
        console.print(Rule(texto, style=CELESTE))
    else:
        console.print(Rule(style=f"dim {GRIS_SUB}"))

def msg_error(msg: str):
    console.print(Panel(f"[bold {ROJO_ERR}]  {msg}[/]", border_style=ROJO_ERR, box=box.ROUNDED, padding=(0, 2)))

def msg_exito(msg: str):
    console.print(Panel(f"[bold {VERDE}]  {msg}[/]", border_style=VERDE, box=box.ROUNDED, padding=(0, 2)))

def msg_info(msg: str):
    console.print(Panel(f"[bold {CELESTE}]  {msg}[/]", border_style=CELESTE, box=box.ROUNDED, padding=(0, 2)))

def spinner_carga(msg: str = "Procesando", secs: float = 1.5):
    sp = Spinner("dots", text=f"[{CELESTE}]{msg}...[/]", style=CELESTE)
    with Live(Align.center(sp), refresh_per_second=20, console=console):
        time.sleep(secs)

def pausar():
    console.print(f"\n  [dim {GRIS_SUB}]Presiona[/] [bold]Enter[/] [dim {GRIS_SUB}]para continuar.[/]")
    input()

def pedir_texto(prompt: str, minlen: int = 1) -> str:
    while True:
        try:
            val = Prompt.ask(f"  [{CELESTE}]{prompt}[/]", console=console, default="").strip()
        except (KeyboardInterrupt, EOFError):
            return ""
        if len(val) >= minlen:
            return val
        msg_error(f"El campo no puede estar vacio (min {minlen} caracter/es).")

def pedir_entero(prompt: str, minval: int = 1) -> int:
    while True:
        try:
            val = IntPrompt.ask(f"  [{CELESTE}]{prompt}[/]", console=console)
        except (KeyboardInterrupt, EOFError):
            return 0
        if val >= minval:
            return val
        msg_error(f"El valor debe ser mayor o igual a {minval}.")


# ═══════════════════════════════════════════════════════════════════════════
#  PANTALLA DE INICIO
# ═══════════════════════════════════════════════════════════════════════════

def pantalla_inicio() -> str:
    while True:
        limpiar(); banner()
        separador(" BIENVENIDO ")
        console.print()

        tabla = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tabla.add_column("Op",     style=f"bold {DORADO}", width=6,  justify="center")
        tabla.add_column("Accion", style=BLANCO,           width=30)
        tabla.add_row(f"[{DORADO}][1][/]", f"[{CELESTE}]Iniciar sesion[/]")
        tabla.add_row(f"[{DORADO}][2][/]", f"[{VERDE}]Crear cuenta[/]")
        tabla.add_row(f"[{DORADO}][0][/]", f"[{ROJO_ERR}]Salir[/]")
        console.print(tabla)
        separador()

        try:
            opcion = Prompt.ask(f"\n  [{CELESTE}]Tu eleccion[/]", console=console, default="", show_default=False).strip()
        except (KeyboardInterrupt, EOFError):
            opcion = "0"

        if opcion == "1":
            usuario = flujo_login()
            if usuario: return usuario
        elif opcion == "2":
            usuario = flujo_registro()
            if usuario: return usuario
        elif opcion == "0":
            limpiar(); banner()
            console.print(f"\n  [bold {DORADO}]Hasta la proxima!  [/]\n")
            time.sleep(1)
            sys.exit(0)
        else:
            msg_error("Opcion invalida. Ingresa 1, 2 o 0.")
            time.sleep(1)


# ═══════════════════════════════════════════════════════════════════════════
#  REGISTRO 
# ═══════════════════════════════════════════════════════════════════════════

def flujo_registro() -> str:
    limpiar(); banner()
    separador(" CREAR CUENTA ")
    console.print()

    try:
        email = pedir_texto("  Email", minlen=5)
        if not email or "@" not in email:
            msg_error("Email invalido."); pausar(); return ""

        contrasena = Prompt.ask(f"  [{CELESTE}]  Contrasena[/]", console=console, password=True)
        if not contrasena or len(contrasena) < 4:
            msg_error("La contrasena debe tener al menos 4 caracteres."); pausar(); return ""

        contrasena2 = Prompt.ask(f"  [{CELESTE}]  Repeti la contrasena[/]", console=console, password=True)
        if contrasena != contrasena2:
            msg_error("Las contrasenas no coinciden."); pausar(); return ""
    except (KeyboardInterrupt, EOFError):
        return ""

    spinner_carga("Creando cuenta", 1.2)

    if not database.create_user(email, contrasena):
        msg_error(f"El email '{email}' ya esta registrado.")
        pausar(); return ""

    msg_exito(f"Cuenta creada. Bienvenido, {email}!")
    time.sleep(1)
    return email


# ═══════════════════════════════════════════════════════════════════════════
#  LOGIN 
# ═══════════════════════════════════════════════════════════════════════════

def flujo_login() -> str:
    MAX_INTENTOS = 3
    intentos = 0

    while intentos < MAX_INTENTOS:
        limpiar(); banner()
        separador(" INICIAR SESION ")
        console.print()

        try:
            email = pedir_texto("  Email", minlen=1)
            if not email: return ""

            contrasena = Prompt.ask(f"  [{CELESTE}]  Contrasena[/]", console=console, password=True)
            if not contrasena:
                msg_error("La contrasena no puede estar vacia.")
                time.sleep(1); continue
        except (KeyboardInterrupt, EOFError):
            return ""

        spinner_carga("Verificando credenciales")

        if database.login_user(email, contrasena):
            msg_exito(f"Bienvenido, {email}!")
            time.sleep(0.8)
            return email
        else:
            intentos += 1
            restantes = MAX_INTENTOS - intentos
            if restantes > 0:
                msg_error(f"Credenciales incorrectas. Te quedan {restantes} intento{'s' if restantes!=1 else ''}.")
            else:
                msg_error("Demasiados intentos fallidos.")
            time.sleep(1.2)

    return ""


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: VER EVENTOS 
# ═══════════════════════════════════════════════════════════════════════════

def mostrar_eventos(pausa: bool = True) -> None:
    limpiar(); banner()
    separador(" EVENTOS DISPONIBLES ")
    console.print()

    eventos = database.list_event("")

    if not eventos.name:
        msg_info("No hay eventos disponibles.")
        if pausa: pausar()
        return

    tabla = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 1))
    tabla.add_column("#",       style=f"bold {DORADO}", justify="center", width=4)
    tabla.add_column("Evento",  style=f"bold {BLANCO}", justify="left",   width=22)
    tabla.add_column("Lugar",   style=f"dim {GRIS_SUB}", justify="left",  width=20)
    tabla.add_column("Fecha",   style=BLANCO,            justify="center", width=12)
    tabla.add_column("Estado",  justify="center",        width=22)

    for i, nombre in enumerate(eventos.name, 1):
        libres = eventos.campo_stock[i - 1] + eventos.platea_stock[i - 1]
        estado = f"[{VERDE}]OK {libres} entradas[/]" if libres > 0 else f"[{ROJO_ERR}]AGOTADO[/]"
        tabla.add_row(str(i), nombre, eventos.place[i - 1], from_unix(eventos.date[i - 1]), estado)

    console.print(tabla)
    if pausa: pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: AGREGAR EVENTO 
# ═══════════════════════════════════════════════════════════════════════════

def agregar_evento() -> None:
    limpiar(); banner()
    separador(" AGREGAR NUEVO EVENTO ")
    console.print()

    try:
        nombre = pedir_texto("  Nombre del evento", minlen=2)
        if not nombre: return
        lugar  = pedir_texto("  Lugar / Estadio", minlen=2)
        if not lugar: return
        fecha  = pedir_texto("  Fecha (dd/mm/yyyy)", minlen=8)
        if not fecha: return

        separador(" SECTOR CAMPO ")
        campo_price = pedir_entero("  Precio Campo ($)", minval=1)
        campo_stock = pedir_entero("  Capacidad Campo", minval=1)

        separador(" SECTOR PLATEA ")
        platea_price = pedir_entero("  Precio Platea ($)", minval=1)
        platea_stock = pedir_entero("  Capacidad Platea", minval=1)

        separador(" CONFIGURACIÓN DE DESCUENTO ")
        disc_code = Prompt.ask(f"  [{CELESTE}]Código de descuento (Enter para omitir)[/]", console=console, default="").strip().upper()
        disc_pct = 0
        if disc_code:
            disc_pct = pedir_entero("  Porcentaje de beneficio (1-100%)", minval=1)
            if disc_pct > 100: disc_pct = 100

    except (KeyboardInterrupt, EOFError):
        return

    console.print()
    separador(" RESUMEN DEL NUEVO EVENTO ")
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("Campo", style=f"dim {GRIS_SUB}", width=14)
    t.add_column("Valor", style=BLANCO)
    t.add_row("Evento", f"[bold {CELESTE}]{nombre}[/]")
    t.add_row("Lugar",  lugar)
    t.add_row("Fecha",  fecha)
    t.add_row("Campo",  f"${campo_price:,}  x {campo_stock}")
    t.add_row("Platea", f"${platea_price:,}  x {platea_stock}")
    t.add_row("Cupón",  f"{disc_code} (-{disc_pct}%)" if disc_code else "Ninguno")
    console.print(t)
    separador()

    try:
        ok = Confirm.ask(f"\n  [{CELESTE}]Guardar este evento?[/]", console=console)
    except (KeyboardInterrupt, EOFError):
        ok = False

    if not ok:
        msg_info("Operacion cancelada."); pausar(); return

    spinner_carga("Guardando en la base de datos", 1.2)

    fecha_con_hora = fecha if " " in fecha else f"{fecha} 00:00"

    if database.create_event(nombre, lugar, campo_price, campo_stock, platea_price, platea_stock, fecha_con_hora):
        if disc_code:
            # Registrar el código en la tabla SALES (tipo 0 = porcentaje)
            sales_database.create_sale(disc_code, 0, disc_pct, nombre)
        msg_exito(f"Evento '{nombre}' guardado.")
    else:
        msg_error(f"Ya existe un evento llamado '{nombre}'.")

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: ESTADISTICAS
# ═══════════════════════════════════════════════════════════════════════════

def ver_estadisticas() -> None:
    limpiar(); banner()
    separador(" ESTADISTICAS DE VENTAS ")

    nombre_evento = seleccionar_evento()
    if not nombre_evento: return

    stats = stats_event.estadisticas_evento(nombre_evento)

    console.print()
    separador(f" {nombre_evento} ")
    t = Table(box=box.SIMPLE, padding=(0, 1), show_header=False)
    t.add_column("Campo", style=f"dim {GRIS_SUB}", width=20)
    t.add_column("Valor", style=BLANCO)
    t.add_row("Entradas vendidas", f"[bold {DORADO}]{stats.total_vendidas}[/]")
    t.add_row("Recaudacion total", f"[bold {VERDE}]${stats.recaudacion:,}[/]")
    t.add_row("Campo",  f"{stats.campo_vendidas} entradas (${stats.campo_recaudacion:,})")
    t.add_row("Platea", f"{stats.platea_vendidas} entradas (${stats.platea_recaudacion:,})")
    console.print(t)
    separador()

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: COMPRA
# ═══════════════════════════════════════════════════════════════════════════

def seleccionar_evento() -> str:
    mostrar_eventos(pausa=False)
    eventos = database.list_event("")
    separador()
    while True:
        try:
            num = IntPrompt.ask(f"\n  [{CELESTE}]Numero del evento[/] [dim](0 para cancelar)[/]", console=console)
        except (KeyboardInterrupt, EOFError):
            return ""
        if num == 0: return ""
        if 1 <= num <= len(eventos.name):
            return eventos.name[num - 1]
        msg_error("Evento no encontrado.")

def seleccionar_sector(ev) -> int:
    separador(f" {ev.name} - Sectores ")
    console.print()

    tabla = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 1))
    tabla.add_column("#",           justify="center", width=4,  style=f"bold {DORADO}")
    tabla.add_column("Sector",      justify="left",   width=14, style=BLANCO)
    tabla.add_column("Precio",      justify="right",  width=12, style=VERDE)
    tabla.add_column("Disponibles", justify="center", width=13)

    disp_campo  = f"[{VERDE}]{ev.campo_stock}[/]"  if ev.campo_stock  > 0 else f"[{ROJO_ERR}]AGOTADO[/]"
    disp_platea = f"[{VERDE}]{ev.platea_stock}[/]" if ev.platea_stock > 0 else f"[{ROJO_ERR}]AGOTADO[/]"
    tabla.add_row("1", "Campo",  f"${ev.campo_price:,}",  disp_campo)
    tabla.add_row("2", "Platea", f"${ev.platea_price:,}", disp_platea)

    console.print(tabla)
    separador()

    while True:
        try:
            op = IntPrompt.ask(f"\n  [{CELESTE}]Numero del sector[/] [dim](0 para cancelar)[/]", console=console)
        except (KeyboardInterrupt, EOFError):
            return -1
        if op == 0: return -1
        if op == 1:
            if ev.campo_stock <= 0: msg_error("El sector 'Campo' esta agotado."); continue
            return 0
        if op == 2:
            if ev.platea_stock <= 0: msg_error("El sector 'Platea' esta agotado."); continue
            return 1
        msg_error("Sector invalido.")

def comprar_entradas() -> None:
    limpiar(); banner()
    separador(" COMPRA DE ENTRADAS ")

    nombre_evento = seleccionar_evento()
    if not nombre_evento: return

    ev = database.read_event(nombre_evento)
    if ev.name is False:
        msg_error("El evento ya no existe."); pausar(); return

    platea = seleccionar_sector(ev)
    if platea == -1: return

    precio_base = ev.platea_price if platea == 1 else ev.campo_price

    # Aplicación del código de descuento via sales_database
    descuento_aplicado = 0
    cupon_ingresado = ""
    hay_promos = sales_database.sales(ev.name) > 0
    if hay_promos:
        try:
            cupon_ingresado = Prompt.ask(
                f"\n  [{CELESTE}]¿Tenés un código de descuento? (Enter para omitir)[/]",
                console=console, default=""
            ).strip().upper()
            if cupon_ingresado:
                promo = sales_database.read_sale(cupon_ingresado, ev.name)
                if promo.event == ev.name:
                    precio_con_descuento = sales_database.apply_sale(cupon_ingresado, ev.name, precio_base)
                    descuento_aplicado = int(round(100 * (1 - precio_con_descuento / precio_base))) if precio_base else 0
                    msg_exito(f"¡Código válido! Descuento aplicado ({descuento_aplicado}%).")
                    time.sleep(1)
                else:
                    msg_error("Código inválido o no aplicable a este evento.")
                    cupon_ingresado = ""
                    time.sleep(1)
        except (KeyboardInterrupt, EOFError):
            pass

    precio_final = precio_base * (100 - descuento_aplicado) // 100
    fecha_compra = time.strftime("%d/%m/%Y %H:%M")

    console.print()
    separador(" RESUMEN DE COMPRA ")
    t = Table(box=box.SIMPLE, padding=(0, 1), show_header=False)
    t.add_column("Campo", style=f"dim {GRIS_SUB}", width=16)
    t.add_column("Valor", style=BLANCO)
    t.add_row("Evento", f"[bold {CELESTE}]{ev.name}[/] ({from_unix(ev.date)})")
    t.add_row("Lugar",  ev.place)
    t.add_row("Sector", "Platea" if platea == 1 else "Campo")
    if descuento_aplicado > 0:
        t.add_row("Precio Base", f"${precio_base:,}")
        t.add_row("Descuento", f"-{descuento_aplicado}% ({cupon_ingresado})")
    t.add_row("Precio Total", f"[bold {DORADO}]${precio_final:,}[/]")
    console.print(t)
    separador()

    try:
        ok = Confirm.ask(f"\n  [{CELESTE}]Confirmas la compra?[/]", console=console)
    except (KeyboardInterrupt, EOFError):
        ok = False

    if not ok:
        msg_info("Compra cancelada."); pausar(); return

    spinner_carga("Procesando pago", 1.8)

    if database.create_ticket(ev.name, usuario_activo, precio_final, fecha_compra, platea):
        msg_exito("Compra exitosa!")
        console.print(f"  [dim {GRIS_SUB}]Podes verla en 'Mis entradas'.[/]")
    else:
        msg_error("No quedan entradas disponibles para ese sector.")

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: MIS ENTRADAS 
# ═══════════════════════════════════════════════════════════════════════════

def mis_entradas() -> None:
    limpiar(); banner()
    separador(" MIS ENTRADAS ")

    tickets = database.list_ticket(usuario_activo)

    if not tickets.event:
        msg_info("No tenes entradas compradas todavia.")
        pausar(); return

    for i, evento in enumerate(tickets.event, 1):
        console.print()
        tabla = Table(
            title=f"[bold {DORADO}]  Ticket #{i:04d}[/]",
            box=box.ROUNDED, border_style=CELESTE,
            show_header=False, padding=(0, 1),
        )
        tabla.add_column("Campo", style=f"dim {GRIS_SUB}", width=16)
        tabla.add_column("Valor", style=BLANCO)
        tabla.add_row("Evento",   f"[bold {CELESTE}]{evento}[/]")
        tabla.add_row("Sector",   "Platea" if tickets.platea[i - 1] else "Campo")
        tabla.add_row("Precio",   f"[bold {DORADO}]${tickets.price[i - 1]:,}[/]")
        tabla.add_row("Comprado", f"[dim]{from_unix(tickets.date[i - 1])}[/]")
        console.print(tabla)

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MENU PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def menu_principal() -> None:
    OPCIONES_BASE = {
        "1": ("  Comprar entradas",  comprar_entradas),
        "2": ("   Mis entradas",     mis_entradas),
        "3": ("  Ver eventos",       lambda: mostrar_eventos(pausa=True)),
        "0": ("  Cerrar sesion",     None),
    }
    OPCIONES_ADMIN = {
        "4": ("  Agregar nuevo evento", agregar_evento),
        "5": ("  Ver estadisticas",     ver_estadisticas),
    }

    while True:
        limpiar(); banner()
        console.print(f"\n  [{GRIS_SUB}]Sesion iniciada como[/] [bold {DORADO}]{usuario_activo}[/]")
        if es_admin():
            console.print(f"  [bold {ROJO_ERR}][ ADMINISTRADOR ][/]\n")
        else:
            console.print()

        # Construir el dict de opciones según el rol
        OPCIONES = dict(OPCIONES_BASE)
        if es_admin():
            OPCIONES.update(OPCIONES_ADMIN)
        # Asegurar que "0" queda al final
        OPCIONES = {k: v for k, v in OPCIONES.items() if k != "0"}
        OPCIONES["0"] = OPCIONES_BASE["0"]

        tabla = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tabla.add_column("Op",     style=f"bold {DORADO}", width=6,  justify="center")
        tabla.add_column("Accion", style=BLANCO,           width=30)
        for op, (desc, _) in OPCIONES.items():
            color = ROJO_ERR if op == "0" else (VERDE if op == "4" else BLANCO)
            tabla.add_row(f"[{DORADO}][{op}][/]", f"[{color}]{desc}[/]")
        console.print(tabla)
        separador()

        try:
            opcion = Prompt.ask(f"\n  [{CELESTE}]Tu eleccion[/]", console=console, default="", show_default=False).strip()
        except (KeyboardInterrupt, EOFError):
            opcion = "0"

        if opcion not in OPCIONES:
            msg_error("Opcion invalida.")
            time.sleep(1); continue

        if opcion == "0":
            limpiar(); banner()
            console.print(f"\n  [bold {DORADO}]Hasta la proxima, {usuario_activo}!  [/]\n")
            time.sleep(1); break

        _, accion = OPCIONES[opcion]
        accion()


# ═══════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    global usuario_activo
    inicializar_db()
    usuario_activo = pantalla_inicio()
    menu_principal()


if __name__ == "__main__":
    main()
 
