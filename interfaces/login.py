#!/usr/bin/env python3
"""
ticketMESSI - CLI Login Interface
Usando Python + Rich
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich.rule import Rule
from rich import box
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich.style import Style


console = Console()

# Paleta de colores temática (Argentina / fútbol)
CELESTE   = "#75AADB"   # celeste argentino
DORADO    = "#F0C040"   # dorado (trofeo)
BLANCO    = "#F5F5F5"   # blanco camiseta
VERDE     = "#3CB371"   # verde campo
ROJO_ERR  = "#E05050"   # errores
GRIS_SUB  = "#888888"   # subtextos

# ─── Credenciales demo ──────────────────────────────────────────────────────
USUARIOS_DEMO = {
    "messi10":   "LaLiga2023!",
    "admin":     "admin123",
    "fanático":  "arg2022",
}


def limpiar():
    console.clear()


def encabezado():
    """Dibuja el banner principal de ticketMESSI."""
    titulo = Text()
    titulo.append("⚽  ticket", style=f"bold {BLANCO}")
    titulo.append("MESSI", style=f"bold {DORADO}")
    titulo.append("  ⚽", style=f"bold {BLANCO}")

    subtitulo = Text('El "10" de las entradas', style=f"italic {CELESTE}")

    stars = Text("★ ★ ★ ★ ★ ★ ★", style=DORADO)

    panel = Panel(
        Align.center(
            Text.assemble(
                titulo, "\n",
                subtitulo, "\n\n",
                stars
            )
        ),
        border_style=CELESTE,
        box=box.DOUBLE_EDGE,
        padding=(1, 6),
    )
    console.print(panel)


def separador(texto: str = ""):
    rule = Rule(texto, style=CELESTE) if texto else Rule(style=f"dim {GRIS_SUB}")
    console.print(rule)


def mostrar_error(mensaje: str):
    console.print(
        Panel(
            f"[bold {ROJO_ERR}]✗  {mensaje}[/]",
            border_style=ROJO_ERR,
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )


def mostrar_exito(mensaje: str):
    console.print(
        Panel(
            f"[bold {VERDE}]✔  {mensaje}[/]",
            border_style=VERDE,
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )


def animacion_carga(mensaje: str = "Verificando credenciales", segundos: float = 2.0):
    """Muestra un spinner animado mientras 'procesa' el login."""
    spinner = Spinner("dots", text=f"[{CELESTE}]{mensaje}…[/]", style=CELESTE)
    with Live(Align.center(spinner), refresh_per_second=20, console=console):
        time.sleep(segundos)


def formulario_login() -> tuple[str, str]:
    """Muestra el formulario y captura usuario/contraseña."""
    console.print()
    separador(" INICIAR SESIÓN ")
    console.print()

    usuario = Prompt.ask(
        f"  [{CELESTE}]👤  Usuario[/]",
        console=console,
        default="",
    ).strip()

    if not usuario:
        mostrar_error("El usuario no puede estar vacío.")
        raise ValueError("usuario_vacío")

    contrasena = Prompt.ask(
        f"  [{CELESTE}]🔒  Contraseña[/]",
        console=console,
        password=True,
    )

    if not contrasena:
        mostrar_error("La contraseña no puede estar vacía.")
        raise ValueError("contraseña_vacía")

    return usuario, contrasena


def validar_credenciales(usuario: str, contrasena: str) -> bool:
    return USUARIOS_DEMO.get(usuario) == contrasena


def pantalla_bienvenida(usuario: str):
    """Pantalla post-login con resumen de cuenta."""
    limpiar()
    encabezado()
    console.print()

    # Mensaje de bienvenida
    bienvenida = Text()
    bienvenida.append("  ¡Bienvenido, ", style=BLANCO)
    bienvenida.append(usuario, style=f"bold {DORADO}")
    bienvenida.append("! 🏆", style=BLANCO)
    console.print(bienvenida)
    console.print()

    # Tarjeta de eventos disponibles
    tabla = Table(
        title=f"[bold {CELESTE}]Próximos Eventos[/]",
        box=box.SIMPLE_HEAVY,
        border_style=CELESTE,
        header_style=f"bold {DORADO}",
        show_footer=False,
        padding=(0, 1),
    )
    tabla.add_column("Fecha",    style=BLANCO,    justify="center", width=12)
    tabla.add_column("Partido",  style=BLANCO,    justify="left",   width=32)
    tabla.add_column("Estadio",  style=GRIS_SUB,  justify="left",   width=22)
    tabla.add_column("Entradas", style=VERDE,      justify="center", width=10)

    eventos = [
        ("21 Jun", "Argentina vs Brasil",         "Monumental, BsAs", "✔ Disponible"),
        ("05 Jul", "Semifinal Copa América",       "Estadio Único, LP", "✔ Disponible"),
        ("19 Jul", "Final Copa América",           "MetLife, NY",       "⚡ Últimas!"),
        ("12 Ago", "Argentina vs Francia (amist)", "Allianz Arena",     "✔ Disponible"),
    ]

    for fecha, partido, estadio, entradas in eventos:
        color_entrada = VERDE if "✔" in entradas else DORADO
        tabla.add_row(
            fecha, partido, estadio,
            f"[{color_entrada}]{entradas}[/]"
        )

    console.print(tabla)
    console.print()

    # Acciones rápidas
    separador(" ACCIONES RÁPIDAS ")
    console.print()

    acciones = [
        Panel("[bold]🎟  Comprar Entradas[/]",   border_style=CELESTE, box=box.ROUNDED, padding=(0, 2)),
        Panel("[bold]📋  Mis Tickets[/]",         border_style=CELESTE, box=box.ROUNDED, padding=(0, 2)),
        Panel("[bold]⚙  Mi Perfil[/]",            border_style=GRIS_SUB, box=box.ROUNDED, padding=(0, 2)),
        Panel(f"[bold {ROJO_ERR}]⏻  Cerrar Sesión[/]", border_style=ROJO_ERR, box=box.ROUNDED, padding=(0, 2)),
    ]
    console.print(Columns(acciones, equal=True, expand=True))

    console.print()
    separador()
    console.print(
        f"  [dim {GRIS_SUB}]Esta es una demo. Presioná[/] [bold]Enter[/] [dim {GRIS_SUB}]para salir.[/]"
    )
    input()


def menu_opciones() -> str:
    """Pequeño menú bajo el formulario."""
    console.print()
    console.print(
        f"  [{GRIS_SUB}]¿Olvidaste tu contraseña?[/] [bold {CELESTE}][R] Recuperar[/]   "
        f"[{GRIS_SUB}]¿No tenés cuenta?[/] [bold {CELESTE}][C] Crear cuenta[/]   "
        f"[{GRIS_SUB}][Q] Salir[/]"
    )
    console.print()
    return Prompt.ask(
        f"  [{GRIS_SUB}]Opción (Enter para continuar)[/]",
        console=console,
        default="",
        show_default=False,
    ).strip().upper()


def flujo_login():
    MAX_INTENTOS = 3
    intentos = 0

    while intentos < MAX_INTENTOS:
        limpiar()
        encabezado()

        try:
            usuario, contrasena = formulario_login()
        except ValueError:
            time.sleep(1)
            continue

        # Menú secundario
        opcion = menu_opciones()
        if opcion == "Q":
            console.print(f"\n  [dim {GRIS_SUB}]¡Hasta la próxima! ⚽[/]\n")
            sys.exit(0)
        elif opcion == "R":
            console.print(f"\n  [{DORADO}]📧 Se enviará un link de recuperación a tu email registrado.[/]\n")
            time.sleep(2)
            continue
        elif opcion == "C":
            console.print(f"\n  [{VERDE}]🔗 Redirigiendo al registro… (demo)[/]\n")
            time.sleep(2)
            continue

        # Validar
        console.print()
        animacion_carga()

        if validar_credenciales(usuario, contrasena):
            mostrar_exito("Autenticación exitosa")
            time.sleep(0.8)
            pantalla_bienvenida(usuario)
            return
        else:
            intentos += 1
            restantes = MAX_INTENTOS - intentos
            console.print()
            if restantes > 0:
                mostrar_error(
                    f"Usuario o contraseña incorrectos. "
                    f"Te quedan {restantes} intento{'s' if restantes > 1 else ''}."
                )
            else:
                mostrar_error("Demasiados intentos fallidos. Cuenta bloqueada temporalmente.")
                console.print(
                    f"\n  [{GRIS_SUB}]Intentá de nuevo en 15 minutos o recuperá tu contraseña.[/]\n"
                )
                sys.exit(1)
            time.sleep(1.5)

    console.print()


def main():
    try:
        flujo_login()
    except KeyboardInterrupt:
        console.print(f"\n\n  [dim {GRIS_SUB}]Sesión cancelada. ¡Hasta pronto! ⚽[/]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()