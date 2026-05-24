# -*- coding: utf-8 -*-
"""
Paquete de Vistas de la aplicación (Interfaz de Usuario).

Agrupa todas las ventanas y diálogos de Tkinter que componen la interfaz
gráfica del sistema: login, ventana principal, gestión de productos, ventas,
pedidos, reportes y ajustes de inventario.
"""

from .login_window import LoginWindow
from .main_window import MainWindow
from .productos_window import ProductosWindow, FormularioProducto
from .ventas_window import VentasWindow
from .pedidos_window import PedidosWindow, NuevoPedidoWindow
from .reportes_window import ReporteStock, ReporteMovimientos, ReporteVentas
from .inventario_window import AjusteStockWindow

__all__ = [
    'LoginWindow',
    'MainWindow',
    'ProductosWindow',
    'FormularioProducto',
    'VentasWindow',
    'PedidosWindow',
    'NuevoPedidoWindow',
    'ReporteStock',
    'ReporteMovimientos',
    'ReporteVentas',
    'AjusteStockWindow'
]