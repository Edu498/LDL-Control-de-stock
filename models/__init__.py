# -*- coding: utf-8 -*-
"""
Paquete de Modelos de Datos del Sistema.

Este paquete agrupa las clases de entidad de negocio que representan los datos del sistema:
productos, categorías, proveedores, ventas (y sus detalles), pedidos (y sus detalles)
y usuarios.
"""

from .producto import Producto
from .categoria import Categoria
from .proveedor import Proveedor
from .venta import Venta, DetalleVenta
from .pedido import Pedido, DetallePedido
from .usuario import Usuario

__all__ = [
    'Producto',
    'Categoria',
    'Proveedor',
    'Venta',
    'DetalleVenta',
    'Pedido',
    'DetallePedido',
    'Usuario'
]