#!/usr/bin/env python3
"""
ticketMESSI — Estadísticas de la base de datos
"""

import sys
import time
import os

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich.rule import Rule
from rich import box


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models.database as database
from models.date import from_unix

console = Console()

CELESTE  = "#75AADB"
DORADO   = "#F0C040"
BLANCO   = "#F5F5F5"
VERDE    = "#3CB371"
ROJO_ERR = "#E05050"
GRIS_SUB = "#888888"

# Accesorios propios de todas las interfaces


def inicio(texto: str = ""):
    console.clear()

    titulo = Text()
    titulo.append("  ticket", style=f"bold {BLANCO}")
    titulo.append("MESSI", style=f"bold {DORADO}")
    titulo.append(" - Estadisticas  ", style=f"bold {BLANCO}")
    subtitulo = Text("Datos y metricas del sistema", style=f"italic {CELESTE}")
    stars = Text("* * * * * * *", style=DORADO)
    panel = Panel(
        Align.center(Text.assemble(titulo, "\n", subtitulo, "\n\n", stars)),
        border_style=CELESTE, box=box.DOUBLE_EDGE, padding=(1, 6),
    )
    console.print(panel)

    console.print(Rule(texto, style=CELESTE))
    console.print()


def limpiar():
    console.clear()

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

def pausar():
    console.print(f"\n  [dim {GRIS_SUB}]Presiona[/] [bold]Enter[/] [dim {GRIS_SUB}]para continuar.[/]")
    input()

# Calculos

def tickets_con_descuento() -> int:
    eventos = database.list_event("")
    total = 0
    for i in range(len(eventos.name)):
        if eventos.campo_price[i] != 0 or eventos.platea_price[i] != 0:
            pass
    eventos_con_descuento = database.db.execute(
        "SELECT COUNT(*) FROM EVENTS WHERE DISCOUNT_CODE != '' AND DISCOUNT_CODE IS NOT NULL;"
    ).fetchone()[0]
    return eventos_con_descuento

def tickets_por_evento():
    return database.db.execute(
        "SELECT EVENT, COUNT(*), COALESCE(SUM(PRICE), 0) FROM TICKETS GROUP BY EVENT ORDER BY COUNT(*) DESC;"
    ).fetchall()

def stock_total_por_evento():
    eventos = database.list_event("")
    data = []
    for i in range(len(eventos.name)):
        data.append((
            eventos.name[i],
            eventos.campo_stock[i],
            eventos.platea_stock[i],
            eventos.campo_stock[i] + eventos.platea_stock[i],
        ))
    return data

def ocupacion_por_evento():
    eventos = database.list_event("")
    res = []
    for i in range(len(eventos.name)):
        nombre = eventos.name[i]
        vendidos = database.db.execute(
            "SELECT COUNT(*) FROM TICKETS WHERE EVENT=?;", (nombre,)
        ).fetchone()[0]
        capacidad_original = (eventos.campo_stock[i] + eventos.platea_stock[i] + vendidos)
        if capacidad_original > 0:
            pct = round(vendidos / capacidad_original * 100, 1)
        else:
            pct = 0.0
        res.append((nombre, vendidos, capacidad_original, pct))
    return res

def estadisticas_generales():
    inicio(" ESTADISTICAS GENERALES ")

    users = database.db.execute("SELECT COUNT(*) FROM ACCOUNTS;").fetchone()[0]
    events = database.db.execute("SELECT COUNT(*) FROM EVENTS;").fetchone()[0]
    tickets = database.db.execute("SELECT COUNT(*) FROM TICKETS;").fetchone()[0]
    revenue = database.db.execute("SELECT COALESCE(SUM(PRICE), 0) FROM TICKETS;").fetchone()[0]
    desc = tickets_con_descuento()

    tabla = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 2))
    tabla.add_column("Metrica",  style=BLANCO,  justify="left",   width=30)
    tabla.add_column("Valor",    style=BLANCO,  justify="center", width=20)

    tabla.add_row("Usuarios registrados",     f"[bold {CELESTE}]{users}[/]")
    tabla.add_row("Eventos creados",           f"[bold {CELESTE}]{events}[/]")
    tabla.add_row("Entradas vendidas",         f"[bold {VERDE}]{tickets}[/]")
    tabla.add_row("Ingreso total",             f"[bold {DORADO}]${revenue:,}[/]")
    tabla.add_row("Eventos con codigo desc.",  f"[bold]{desc}[/]")
    console.print(tabla)
    console.print()
    pausar()

def estadisticas_por_evento():
    inicio(" ENTRADAS VENDIDAS POR EVENTO ")

    ## COLUMNAS

    rows = tickets_por_evento()
    if not rows:
        msg_info("No hay ventas registradas.")
        pausar(); return


    ## TABLA
    tabla = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 1))
    tabla.add_column("Evento",       style=f"bold {BLANCO}", justify="left",   width=24)
    tabla.add_column("Entradas",     style=VERDE,            justify="center", width=10)
    tabla.add_column("Ingreso",      style=DORADO,           justify="right",  width=14)

    for ev, cnt, ing in rows:
        tabla.add_row(ev, str(cnt), f"${ing:,}")
    console.print(tabla)
    console.print()
    pausar()

    inicio(" OCUPACION POR EVENTO ")

    ocupacion = ocupacion_por_evento()
    if not ocupacion:
        msg_info("No hay datos de ocupacion.")
        pausar(); return

    tabla2 = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 1))
    tabla2.add_column("Evento",       style=f"bold {BLANCO}", justify="left",   width=24)
    tabla2.add_column("Vendidas",     style=VERDE,            justify="center", width=10)
    tabla2.add_column("Capacidad",    style=BLANCO,           justify="center", width=10)
    tabla2.add_column("Ocupacion",    style=DORADO,           justify="center", width=10)

    for nombre, vend, cap, pct in ocupacion:
        color_pct = VERDE if pct < 80 else (DORADO if pct < 95 else ROJO_ERR)
        tabla2.add_row(nombre, str(vend), str(cap), f"[{color_pct}]{pct}%[/]")
    console.print(tabla2)
    console.print()
    pausar()

    inicio(" STOCK ACTUAL POR EVENTO ")

    stocks = stock_total_por_evento()
    if not stocks:
        msg_info("No hay eventos registrados.")
        pausar(); return

    tabla3 = Table(box=box.SIMPLE_HEAVY, border_style=CELESTE, header_style=f"bold {DORADO}", padding=(0, 1))
    tabla3.add_column("Evento",         style=f"bold {BLANCO}", justify="left",   width=24)
    tabla3.add_column("Campo disp.",    style=VERDE,            justify="center", width=12)
    tabla3.add_column("Platea disp.",   style=VERDE,            justify="center", width=12)
    tabla3.add_column("Stock total",    style=BLANCO,           justify="center", width=12)

    for nombre, campo, platea, total in stocks:
        tabla3.add_row(nombre, str(campo), str(platea), str(total))
    console.print(tabla3)
    console.print()
    pausar()

def menu_principal():

    ## OPCIONES A AGREGAR MAS: POR USUA 

    OPCIONES = {
        "1": ("Estadisticas generales",         estadisticas_generales),
        "2": ("Por evento",               estadisticas_por_evento),
        "0": ("Salir",                    None),
    }

    while True:
        inicio()

        tabla = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tabla.add_column("Op",     style=f"bold {DORADO}", width=6,  justify="center")
        tabla.add_column("Accion", style=BLANCO,           width=30)
        for op, (desc, _) in OPCIONES.items():
            color = ROJO_ERR if op == "0" else BLANCO
            tabla.add_row(f"[{DORADO}][{op}][/]", f"[{color}]{desc}[/]")
        console.print(tabla)
        console.print(Rule(style=f"dim {GRIS_SUB}"))

        try:
            opcion = Prompt.ask(f"\n  [{CELESTE}]Tu eleccion[/]", console=console, default="", show_default=False).strip()
        except (KeyboardInterrupt, EOFError):
            opcion = "0"

        if opcion not in OPCIONES:
            msg_error("Opcion invalida.")
            time.sleep(1)
            continue

        if opcion == "0":
            inicio()
            console.print(f"\n  [bold {DORADO}]Hasta la proxima!  [/]\n")
            time.sleep(1)
            break

        _, accion = OPCIONES[opcion]
        accion()

def flujo_stats():
    menu_principal()

if __name__ == "__main__":
    flujo_stats()
