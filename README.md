# Sistema de entradas para recitales

#### Trabajo integrador de python | grupo B36

## Integrantes:
- Thiago Jeremías obregon
- Thiago Holzman Zorzon   
- Máximo Amir Ramirez
- Vallejos Sanchez Gabriel Omar
- Casabuena Milagros Sofía

## Definicion:
El sistema permite administrar entradas para eventos musicales. La solución contempla selección de sectores, cálculo de importes, control de capacidad y aplicación de promociones o descuentos.
También incorpora estadísticas de ventas y sectores más demandados.

## Requisitos:
- Python 3.x
- Librería `rich` (ver requirements.txt)

## Instalación
1. Clonar el repositorio
2. Instalar librerías necesarias:
`pip install rich`
3. Ejecutar el programa: 
`python -m interfaces.ticketMESSI_recitales`

## Funcionalidades:
- Registro e inicio de sesión
- Compra de entradas por sector (Campo/Platea)
- Códigos de descuento
- Ver entradas compradas
- Panel de administrador: agregar eventos y ver estadísticas

## Credenciales de administrador:
- Email: admin@ticketmessi.com
- Contraseña: admin1234

## Estructura del proyecto:
- `interfaces/` -> pantallas y menú del sistema
- `models/` -> manejo de datos y conexión con la base de datos
- `data.db` -> base de datos SQLite
------
