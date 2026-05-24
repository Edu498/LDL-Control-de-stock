# -*- coding: utf-8 -*-
"""
Configuración del Sistema de Control de Stock
Autor: Sistema Profesional de Gestión
Versión: 2.0.0

Este módulo contiene todos los diccionarios de configuración necesarios para el
correcto funcionamiento del sistema (base de datos, aplicación, IVA, stock y facturación).
"""

# Configuración de Base de Datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Arcangeles369',
    'database': 'stock',
    'port': 3306,
    'charset': 'utf8mb4',
    'use_pure': True,
    'autocommit': False,
    'pool_name': 'mypool',
    'pool_size': 5
}
"""dict: Configuración de conexión para la base de datos MySQL, incluyendo credenciales y pool de conexiones."""

# Configuración de la Aplicación
APP_CONFIG = {
    'nombre': 'Sistema de Control de Stock',
    'version': '2.0.0',
    'empresa': 'Sistema Profesional de Gestión',
    'desarrollador': 'Engineering Team',
    'year': 2024
}
"""dict: Datos informativos y metadatos generales de la aplicación."""

# Configuración de IVA
IVA_CONFIG = {
    'tasa_default': 21.0,
    'tasas': {
        1: 21.0,
        2: 10.5,
        3: 0.0
    }
}
"""dict: Tasas de IVA aplicables a los productos y tasa por defecto."""

# Configuración de Stock
STOCK_CONFIG = {
    'stock_minimo_default': 5,
    'alerta_stock_bajo': True,
    'alerta_sin_stock': True,
    'dias_para_reposicion': 7
}
"""dict: Parámetros del gestor de stock, incluyendo mínimos y alertas."""

# Configuración de Facturación
FACTURACION_CONFIG = {
    'prefijo_factura': 'F',
    'longitud_numero': 8,
    'incluir_iva': True,
    'decimales': 2
}
"""dict: Opciones de formato de factura y precisión decimal para cálculos financieros."""