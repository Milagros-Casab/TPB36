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
import models.stats_event as stats_event
from models.date import from_unix
from models.date import valid_date

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


    # Crear cuenta de administrador si no existe
if database.login_user(ADMIN_EMAIL, "admin1234")==False:
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

def pedir_contrasena(prompt: str) -> str:
    """Pide una contraseña sin mostrar los caracteres, avisando antes por privacidad."""
    console.print(f"  [dim {GRIS_SUB}](Los caracteres no se muestran por privacidad)[/]")
    try:
        return Prompt.ask(f"  [{CELESTE}]{prompt}[/]", console=console, password=True)
    except (KeyboardInterrupt, EOFError):
        raise


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
        if database.check_email(email)==False:
            msg_error("Email invalido."); pausar(); return ""

        contrasena = pedir_contrasena("  Contrasena")
        if not contrasena or len(contrasena) < 4:
            msg_error("La contrasena debe tener al menos 4 caracteres."); pausar(); return ""

        contrasena2 = pedir_contrasena("  Repeti la contrasena")
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

            contrasena = pedir_contrasena("  Contrasena")
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

def evento_finalizado(ev) -> bool:
    """True si la fecha del evento ya pasó."""
    return ev.date <= int(time.time())

def mostrar_eventos(pausa: bool = True, solo_futuros: bool = False) -> None:
    limpiar(); banner()
    separador(" EVENTOS DISPONIBLES ")
    console.print()

    eventos = database.list_event("")
    ahora = int(time.time())

    if solo_futuros:
        indices = [i for i in range(len(eventos.name)) if eventos.date[i] > ahora]
    else:
        indices = list(range(len(eventos.name)))

    if not indices:
        msg_info("No hay eventos disponibles.")
        if pausa: pausar()
        return

    tabla = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 1))
    tabla.add_column("#",       style=f"bold {DORADO}", justify="center", width=4)
    tabla.add_column("Evento",  style=f"bold {BLANCO}", justify="left",   width=22)
    tabla.add_column("Lugar",   style=f"dim {GRIS_SUB}", justify="left",  width=20)
    tabla.add_column("Fecha",   style=BLANCO,            justify="center", width=12)
    tabla.add_column("Estado",  justify="center",        width=22)

    for pos, i in enumerate(indices, 1):
        libres = eventos.campo_stock[i] + eventos.platea_stock[i]
        if eventos.date[i] <= ahora:
            estado = f"[dim {GRIS_SUB}]FINALIZADO[/]"
        elif libres > 0:
            estado = f"[{VERDE}]OK {libres} entradas[/]"
        else:
            estado = f"[{ROJO_ERR}]AGOTADO[/]"
        tabla.add_row(str(pos), eventos.name[i], eventos.place[i], from_unix(eventos.date[i]), estado)

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
        fecha  = pedir_texto("  Fecha (DD/MM/YYYY hh:mm)", minlen=15)
        if not fecha or not valid_date(fecha): return

        separador(" SECTOR CAMPO ")
        campo_price = pedir_entero("  Precio Campo ($)", minval=1)
        campo_stock = pedir_entero("  Capacidad Campo", minval=1)

        separador(" SECTOR PLATEA ")
        platea_price = pedir_entero("  Precio Platea ($)", minval=1)
        platea_stock = pedir_entero("  Capacidad Platea", minval=1)

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
        msg_exito(f"Evento '{nombre}' guardado. Podes agregarle un codigo de promocion desde el menu.")
    else:
        msg_error(f"Ya existe un evento llamado '{nombre}'.")

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: EDITAR EVENTO
# ═══════════════════════════════════════════════════════════════════════════

def editar_evento() -> None:
    limpiar(); banner()
    separador(" EDITAR EVENTO ")

    nombre_evento = seleccionar_evento(solo_futuros=False)
    if not nombre_evento: return

    ev = database.read_event(nombre_evento)
    if ev.name is False:
        msg_error("El evento ya no existe."); pausar(); return

    console.print()
    msg_info("Dejá vacío cualquier campo para mantener el valor actual.")

    try:
        lugar = Prompt.ask(f"  [{CELESTE}]Lugar[/] [dim](actual: {ev.place})[/]", console=console, default="").strip()
        lugar = lugar if lugar else ev.place

        fecha_actual = from_unix(ev.date)
        fecha = Prompt.ask(f"  [{CELESTE}]Fecha DD/MM/YYYY hh:mm[/] [dim](actual: {fecha_actual})[/]", console=console, default="").strip()
        fecha = fecha if fecha else fecha_actual

        cp = Prompt.ask(f"  [{CELESTE}]Precio Campo[/] [dim](actual: ${ev.campo_price})[/]", console=console, default="").strip()
        campo_price = int(cp) if cp else ev.campo_price

        cs = Prompt.ask(f"  [{CELESTE}]Stock Campo[/] [dim](actual: {ev.campo_stock})[/]", console=console, default="").strip()
        campo_stock = int(cs) if cs else ev.campo_stock

        pp = Prompt.ask(f"  [{CELESTE}]Precio Platea[/] [dim](actual: ${ev.platea_price})[/]", console=console, default="").strip()
        platea_price = int(pp) if pp else ev.platea_price

        ps = Prompt.ask(f"  [{CELESTE}]Stock Platea[/] [dim](actual: {ev.platea_stock})[/]", console=console, default="").strip()
        platea_stock = int(ps) if ps else ev.platea_stock
    except (KeyboardInterrupt, EOFError):
        msg_info("Edicion cancelada."); pausar(); return
    except ValueError:
        msg_error("Valor numerico invalido."); pausar(); return

    console.print()
    separador(" CONFIRMAR CAMBIOS ")
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("Campo", style=f"dim {GRIS_SUB}", width=14)
    t.add_column("Valor", style=BLANCO)
    t.add_row("Evento", f"[bold {CELESTE}]{nombre_evento}[/]")
    t.add_row("Lugar",  lugar)
    t.add_row("Fecha",  fecha)
    t.add_row("Campo",  f"${campo_price:,}  x {campo_stock}")
    t.add_row("Platea", f"${platea_price:,}  x {platea_stock}")
    console.print(t)
    separador()

    try:
        ok = Confirm.ask(f"\n  [{CELESTE}]Guardar los cambios?[/]", console=console)
    except (KeyboardInterrupt, EOFError):
        ok = False

    if not ok:
        msg_info("Edicion cancelada."); pausar(); return

    spinner_carga("Actualizando evento", 1.0)

    fecha_con_hora = fecha if " " in fecha else f"{fecha} 00:00"

    if database.update_event(nombre_evento, lugar, campo_price, campo_stock, platea_price, platea_stock, fecha_con_hora):
        msg_exito("Evento actualizado.")
    else:
        msg_error("No se pudo actualizar el evento.")

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: ELIMINAR EVENTO
# ═══════════════════════════════════════════════════════════════════════════

def eliminar_evento() -> None:
    limpiar(); banner()
    separador(" ELIMINAR EVENTO ")

    nombre_evento = seleccionar_evento(solo_futuros=False)
    if not nombre_evento: return

    try:
        ok = Confirm.ask(
            f"\n  [{ROJO_ERR}]Seguro que querés eliminar '{nombre_evento}'? Esta accion no se puede deshacer.[/]",
            console=console
        )
    except (KeyboardInterrupt, EOFError):
        ok = False

    if not ok:
        msg_info("Operacion cancelada."); pausar(); return

    spinner_carga("Eliminando evento", 1.0)

    if database.purge_event(nombre_evento):
        msg_exito(f"Evento '{nombre_evento}' eliminado.")
    else:
        msg_error("No se pudo eliminar el evento.")

    pausar()


# ═══════════════════════════════════════════════════════════════════════════
#  MODULO: CODIGOS DE PROMOCION
# ═══════════════════════════════════════════════════════════════════════════

def agregar_promocode() -> None:
    limpiar(); banner()
    separador(" AGREGAR CODIGO DE PROMOCION ")

    nombre_evento = seleccionar_evento(solo_futuros=False)
    if not nombre_evento: return

    try:
        codigo = pedir_texto("  Codigo: ", minlen=2).upper()

        console.print()
        tabla = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tabla.add_column("Op", style=f"bold {DORADO}", width=4, justify="center")
        tabla.add_column("Tipo", style=BLANCO)
        tabla.add_row("1", "Descuento porcentual (%)")
        tabla.add_row("2", "Descuento de monto fijo ($)")
        console.print(tabla)

        tipo_op = pedir_entero("  Tipo de descuento (1 o 2)", minval=1)
        while tipo_op not in (1, 2):
            msg_error("Opcion invalida. Ingresa 1 o 2.")
            tipo_op = pedir_entero("  Tipo de descuento (1 o 2)", minval=1)

        if tipo_op == 1:
            valor = pedir_entero("  Porcentaje de descuento (1-100)", minval=1)
            if valor > 100: valor = 100
            tipo_db = 0
        else:
            valor = pedir_entero("  Monto de descuento ($)", minval=1)
            tipo_db = 1
    except (KeyboardInterrupt, EOFError):
        return

    console.print()
    separador(" CONFIRMAR CODIGO ")
    t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    t.add_column("Campo", style=f"dim {GRIS_SUB}", width=14)
    t.add_column("Valor", style=BLANCO)
    t.add_row("Evento", f"[bold {CELESTE}]{nombre_evento}[/]")
    t.add_row("Codigo", codigo)
    t.add_row("Descuento", f"{valor}%" if tipo_db == 0 else f"${valor:,}")
    console.print(t)
    separador()

    try:
        ok = Confirm.ask(f"\n  [{CELESTE}]Guardar el codigo '{codigo}'?[/]", console=console)
    except (KeyboardInterrupt, EOFError):
        ok = False

    if not ok:
        msg_info("Operacion cancelada."); pausar(); return

    spinner_carga("Guardando codigo", 1.0)

    resultado = sales_database.create_sale(codigo, tipo_db, valor, nombre_evento)

    if resultado is True:
        msg_exito(f"Codigo '{codigo}' agregado al evento '{nombre_evento}'.")
    else:
        msg_error("No se pudo agregar el codigo.")

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

def seleccionar_evento(solo_futuros: bool = False) -> str:
    mostrar_eventos(pausa=False, solo_futuros=solo_futuros)
    eventos = database.list_event("")
    ahora = int(time.time())

    if solo_futuros:
        nombres_disponibles = [n for n, d in zip(eventos.name, eventos.date) if d > ahora]
    else:
        nombres_disponibles = eventos.name

    separador()
    while True:
        try:
            num = IntPrompt.ask(f"\n  [{CELESTE}]Numero del evento[/] [dim](0 para cancelar)[/]", console=console)
        except (KeyboardInterrupt, EOFError):
            return ""
        if num == 0: return ""
        if 1 <= num <= len(nombres_disponibles):
            return nombres_disponibles[num - 1]
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

    nombre_evento = seleccionar_evento(solo_futuros=True)
    if not nombre_evento: return

    ev = database.read_event(nombre_evento)
    if ev.name is False:
        msg_error("El evento ya no existe."); pausar(); return

    if evento_finalizado(ev):
        msg_error("Este evento ya finalizo. No se pueden comprar entradas."); pausar(); return

    platea = seleccionar_sector(ev)
    if platea == -1: return

    precio_base = ev.platea_price if platea == 1 else ev.campo_price
    precio_final = precio_base
    cupon_ingresado = ""

    # Aplicación del código de descuento via sales_database
    hay_promos = sales_database.sales(ev.name) > 0
    if hay_promos:
        while True:
            try:
                cupon_ingresado = Prompt.ask(
                    f"\n  [{CELESTE}]¿Tenés un código de descuento? (Enter para omitir)[/]",
                    console=console, default=""
                ).strip().upper()
            except (KeyboardInterrupt, EOFError):
                cupon_ingresado = ""
                break

            if not cupon_ingresado:
                break

            promo = sales_database.read_sale(cupon_ingresado, ev.name)
            if promo.event == ev.name:
                precio_final = int(round(sales_database.apply_sale(cupon_ingresado, ev.name, precio_base)))
                if precio_final < 0: precio_final = 0
                msg_exito("¡Código válido! Descuento aplicado.")
                time.sleep(1)
                break
            else:
                msg_error("Código inválido o no aplicable a este evento. Probá de nuevo o dejá vacío para omitir.")
                time.sleep(1)

    fecha_compra = time.strftime("%d/%m/%Y %H:%M")

    console.print()
    separador(" RESUMEN DE COMPRA ")
    t = Table(box=box.SIMPLE, padding=(0, 1), show_header=False)
    t.add_column("Campo", style=f"dim {GRIS_SUB}", width=16)
    t.add_column("Valor", style=BLANCO)
    t.add_row("Evento", f"[bold {CELESTE}]{ev.name}[/] ({from_unix(ev.date)})")
    t.add_row("Lugar",  ev.place)
    t.add_row("Sector", "Platea" if platea == 1 else "Campo")
    if precio_final < precio_base:
        t.add_row("Precio Base", f"${precio_base:,}")
        t.add_row("Descuento", f"-${precio_base - precio_final:,} ({cupon_ingresado})")
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
    OPCIONES_USUARIO = {
        "1": ("  Comprar entradas",  comprar_entradas),
        "2": ("   Mis entradas",     mis_entradas),
        "3": ("  Ver eventos",       lambda: mostrar_eventos(pausa=True, solo_futuros=True)),
        "0": ("  Cerrar sesion",     None),
    }
    OPCIONES_ADMIN = {
        "1": ("  Ver eventos",                lambda: mostrar_eventos(pausa=True, solo_futuros=False)),
        "2": ("  Agregar nuevo evento",        agregar_evento),
        "3": ("  Editar evento",               editar_evento),
        "4": ("  Eliminar evento",             eliminar_evento),
        "5": ("  Agregar codigo de promocion", agregar_promocode),
        "6": ("  Ver estadisticas",            ver_estadisticas),
        "0": ("  Cerrar sesion",                None),
    }

    while True:
        limpiar(); banner()
        console.print(f"\n  [{GRIS_SUB}]Sesion iniciada como[/] [bold {DORADO}]{usuario_activo}[/]")
        if es_admin():
            console.print(f"  [bold {ROJO_ERR}][ ADMINISTRADOR ][/]\n")
        else:
            console.print()

        OPCIONES = OPCIONES_ADMIN if es_admin() else OPCIONES_USUARIO

        tabla = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tabla.add_column("Op",     style=f"bold {DORADO}", width=6,  justify="center")
        tabla.add_column("Accion", style=BLANCO,           width=30)
        for op, (desc, _) in OPCIONES.items():
            color = ROJO_ERR if op == "0" else (VERDE if op == "2" else BLANCO)
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
    usuario_activo = pantalla_inicio()
    menu_principal()

