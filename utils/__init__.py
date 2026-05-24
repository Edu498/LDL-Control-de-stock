
# -*- coding: utf-8 -*-
"""
Paquete de Utilidades del Sistema.

Este paquete agrupa herramientas auxiliares de uso transversal en la aplicación:
- Manejo y pool de conexiones a Base de Datos (database.py).
- Ventanas emergentes y notificaciones al usuario (alertas.py).
- Funciones helper para fechas, precios y validaciones generales (helpers.py).
"""

from .database import get_connection, close_connection, execute_query
from .helpers import *
from .alertas import Alertas

__all__ = [
    'get_connection',
    'close_connection',
    'execute_query',
    'Alertas'
]