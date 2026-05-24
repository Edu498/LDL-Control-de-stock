# -*- coding: utf-8 -*-
"""
Funciones auxiliares y utilitarias del Sistema.

Proporciona métodos transversales para formatear precios, formatear y parsear fechas,
validar expresiones regulares comunes (emails, códigos de barra, RUC) y gestionar paginación.
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
        # Obtener la cantidad de decimales de la configuración
        decimales = FACTURACION_CONFIG.get('decimales', 2)
    
    try:
        # Convertir el valor a float para asegurar que sea un número
        valor_float = float(valor)
        if decimales == 0:
            # Formatear el valor a 0 decimales
            return f"${valor_float:,.0f}".replace(",", ".")
        else:
            # Se formatea el valor a la cantidad de decimales especificada
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
        # Intentar convertir la fecha en string a date
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except:
            # Intentar convertir la fecha en string a datetime
            try:
                # Se intenta convertir la fecha en string a datetime
                fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S').date()
            except:
                # Si no se puede convertir la fecha, se devuelve el valor original
                return fecha
    elif isinstance(fecha, datetime):
        # Si la fecha es un datetime, se convierte a date
        fecha = fecha.date()
    
    if isinstance(fecha, (datetime, date)):
        # Se formatea la fecha
        return fecha.strftime(formato)
    return str(fecha)

def formatear_datetime(fecha_hora):
    """
    Formatea un objeto datetime en formato de cadena 'dd/mm/aaaa HH:MM'.

    Args:
        fecha_hora (datetime): Objeto fecha y hora a formatear.

    Returns:
        str: Fecha y hora formateadas, o representación en cadena del valor de entrada si no es datetime.
    """
    if isinstance(fecha_hora, datetime):
        # Si la fecha es un datetime, se convierte a date
        return fecha_hora.strftime("%d/%m/%Y %H:%M")
    return str(fecha_hora)

def validar_codigo(codigo):
    """
    Valida si un código de producto cumple con el patrón alfanumérico permitido.

    El código debe contener entre 3 y 20 caracteres (letras, números y guiones).

    Args:
        codigo (str): Código del producto a validar.

    Returns:
        bool: True si el código cumple con el formato requerido, False en caso contrario.
    """
    if not codigo:
        return False
    patron = r'^[A-Z0-9\-]{3,20}$'
    return bool(re.match(patron, codigo.upper()))

def validar_email(email):
    """
    Valida si una dirección de correo electrónico tiene un formato sintácticamente válido.

    Args:
        email (str): Dirección de correo a validar.

    Returns:
        bool: True si el formato es correcto, False en caso contrario.
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

def validar_ruc(ruc):
    """
    Valida si un número de identificación RUC o CUIT tiene el formato legal correcto.

    Admite formatos con guiones (XX-XXXXXXXX-X) o sin guiones (11 dígitos continuos).

    Args:
        ruc (str): Número identificador RUC/CUIT a validar.

    Returns:
        bool: True si es vacío o si cumple con el patrón esperado, False en caso contrario.
    """
    if not ruc:
        return True
    patron = r'^\d{2}-\d{8}-\d$|^\d{11}$'
    return bool(re.match(patron, ruc))

def generar_numero_factura():
    """
    Genera un número de factura único basado en la fecha y la hora actual del sistema.

    Usa el prefijo configurado en `config.FACTURACION_CONFIG` (ej: 'F') seguido
    de la fecha en formato 'AAAAMMDD-HHMMSS'.

    Returns:
        str: Número correlativo único generado.
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
    Calcula el importe impositivo (IVA) aplicable sobre un subtotal dado.

    Args:
        subtotal (float): Monto neto de la venta sobre el que se calcula el impuesto.
        tasa (float, opcional): Porcentaje de IVA a aplicar. Por defecto es 21.0.

    Returns:
        float: Monto calculado correspondiente al impuesto.
    """
    return subtotal * tasa / 100

def redondear_decimal(valor, decimales=2):
    """
    Redondea un número flotante de forma exacta usando aritmética de precisión (Decimal).

    Aplica redondeo ROUND_HALF_UP para evitar errores de coma flotante de IEEE 754.

    Args:
        valor (float o Decimal): Número a redondear.
        decimales (int, opcional): Cantidad de cifras decimales deseadas. Por defecto es 2.

    Returns:
        float: El valor redondeado.
    """
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return float(valor.quantize(Decimal('0.' + '0' * decimales), rounding=ROUND_HALF_UP))

def buscar_productos(lista, texto_busqueda):
    """
    Filtra una lista de productos buscando ocurrencias del texto en el código o nombre.

    Búsqueda insensible a mayúsculas y minúsculas (case-insensitive) y sin espacios laterales.

    Args:
        lista (list): Lista de objetos Producto.
        texto_busqueda (str): Cadena de texto a buscar.

    Returns:
        list: Sublista con los productos que coinciden con el criterio de búsqueda.
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
    Obtiene una porción o página específica de elementos de una lista.

    Args:
        lista (list): Lista completa de elementos a paginar.
        pagina (int): Número de página solicitado (basado en 1).
        items_por_pagina (int, opcional): Cantidad de elementos por página. Por defecto es 20.

    Returns:
        list: Sublista correspondiente a la página seleccionada.
    """
    inicio = (pagina - 1) * items_por_pagina
    fin = inicio + items_por_pagina
    return lista[inicio:fin]

def obtener_calculo_paginas(total_items, items_por_pagina=20):
    """
    Calcula la cantidad total de páginas requeridas para albergar un número de elementos.

    Args:
        total_items (int): Cantidad total de elementos.
        items_por_pagina (int, opcional): Cantidad de elementos por página. Por defecto es 20.

    Returns:
        int: Número total de páginas (mínimo 0).
    """
    total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina
    return total_paginas