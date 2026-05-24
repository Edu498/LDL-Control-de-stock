# -*- coding: utf-8 -*-
"""
Paquete de Controladores de la aplicación.

Este paquete agrupa las clases controladoras de negocio siguiendo el patrón MVC,
encargadas de intermediar entre las vistas y los modelos de datos para pedidos,
reportes, stock e inventario, y ventas.
"""

from .stock_controller import StockController
from .venta_controller import VentaController
from .pedido_controller import PedidoController
from .reporte_controller import ReporteController