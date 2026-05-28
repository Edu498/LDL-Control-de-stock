# -*- coding: utf-8 -*-
"""
Funciones auxiliares del Sistema
"""

import re
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from config import FACTURACION_CONFIG

def formatear_precio(valor, decimales=None):
    """
    Formatea un número como precio en pesos argentinos
    
    Args:
        valor: Número a formatear
        decimales: Cantidad de decimales (None usa el valor por defecto)
    
    Returns:
        str: Precio formateado
    """
    if decimales is None:
        decimales = FACTURACION_CONFIG.get('decimales', 2)
    
    try:
        valor_float = float(valor)
        if decimales == 0:
            return f"${valor_float:,.0f}".replace(",", ".")
        else:
            return f"${valor_float:,.{decimales}f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0.00"

def formatear_fecha(fecha, formato="%d/%m/%Y"):
    """
    Formatea una fecha en el formato especificado
    
    Args:
        fecha: Fecha a formatear (datetime, date o string)
        formato: Formato de salida
    
    Returns:
        str: Fecha formateada
    """
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except:
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S').date()
            except:
                return fecha
    elif isinstance(fecha, datetime):
        fecha = fecha.date()
    
    if isinstance(fecha, (datetime, date)):
        return fecha.strftime(formato)
    return str(fecha)

def formatear_datetime(fecha_hora):
    """
    Formatea datetime completo

    Args:
        fecha_hora: Fecha y hora a formatear

    Returns:
        str: Fecha y hora formateada
    """
    if isinstance(fecha_hora, datetime):
        return fecha_hora.strftime("%d/%m/%Y %H:%M")
    return str(fecha_hora)

def validar_codigo(codigo):
    """
    Valida el formato del código de producto
    
    Args:
        codigo: Código a validar
    
    Returns:
        bool: True si es válido
    """
    if not codigo:
        return False
    patron = r'^[A-Z0-9\-]{3,20}$'
    return bool(re.match(patron, codigo.upper()))

def validar_email(email):
    """
    Valida formato de email

    Args:
        email: Email a validar

    Returns:
        bool: True si es válido
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

def validar_ruc(ruc):
    """
    Valida formato de RUC/CUIT

    Args:
        ruc: RUC/CUIT a validar

    Returns:
        bool: True si es válido
    """
    if not ruc:
        return True
    patron = r'^\d{2}-\d{8}-\d$|^\d{11}$'
    return bool(re.match(patron, ruc))

def generar_numero_factura():
    """
    Genera un número de factura único

    Returns:
        str: Número de factura único
    """
    from datetime import datetime
    prefijo = FACTURACION_CONFIG.get('prefijo_factura', 'F')
    anio = datetime.now().strftime('%Y')
    mes = datetime.now().strftime('%m')
    dia = datetime.now().strftime('%d')
    hora = datetime.now().strftime('%H%M%S')
    return f"{prefijo}{anio}{mes}{dia}-{hora}"

def calcular_iva(subtotal, tasa=21.0):
    """
    Calcula el IVA a partir del subtotal
    
    Args:
        subtotal: Subtotal
        tasa: Tasa de IVA

    Returns:
        float: IVA
    """
    return subtotal * tasa / 100

def redondear_decimal(valor, decimales=2):
    """
    Redondea un valor a la cantidad de decimales especificada

    Args:
        valor: Valor a redondear
        decimales: Cantidad de decimales

    Returns:
        float: Valor redondeado
    """
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return float(valor.quantize(Decimal('0.' + '0' * decimales), rounding=ROUND_HALF_UP))

def buscar_productos(lista, texto_busqueda):
    """
    Busca productos por código o nombre
    
    Args:
        lista: Lista de productos
        texto_busqueda: Texto a buscar

    Returns:
        list: Lista de productos encontrados
    """
    if not texto_busqueda:
        return lista
    
    texto = texto_busqueda.lower().strip()
    resultados = []
    
    for producto in lista:
        if texto in producto.codigo.lower() or texto in producto.nombre.lower():
            resultados.append(producto)
    
    return resultados

def paginar_lista(lista, pagina, items_por_pagina=20):
    """
    Pagina una lista de elementos
    
    Args:
        lista: Lista de elementos
        pagina: Página actual
        items_por_pagina: Cantidad de elementos por página

    Returns:
        list: Lista paginada
    """
    inicio = (pagina - 1) * items_por_pagina
    fin = inicio + items_por_pagina
    return lista[inicio:fin]

def obtener_calculo_paginas(total_items, items_por_pagina=20):
    """
    Calcula el número de páginas y la página actual

    Args:
        total_items: Total de elementos
        items_por_pagina: Cantidad de elementos por página

    Returns:
        int: Número de páginas
    """
    total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina
    return total_paginas