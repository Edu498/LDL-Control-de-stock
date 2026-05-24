# -*- coding: utf-8 -*-
"""
Modelos de datos para Pedidos y Órdenes de Reposición a Proveedores.
"""

from datetime import datetime

class DetallePedido:
    """
    Representa un item individual dentro de un pedido realizado a un provedor.

    Permite hacer el seguimiento de la cantidad de solicitada frente a la cantidad fisicamente recibida, facilitndo el control de entregas parciales o mercaderia pendiente.
    """
    def __init__(self, id_producto=None, producto_nombre="", cantidad=0, 
                 cantidad_recibida=0, precio_unitario=0.0):
        """
        Inicializa una instancia de DetallePedido.

        Args:
            id_producto (int, opcional): ID del producto pedido
            producto_nombre (str, opcional): Nombre del producto pedido
            cantidad (int, opcional): Cantidad de unidades pedidas
            cantidad_recibida (int, opcional): Cantidad de unidades recibidas
            precio_unitario (float, opcional): Precio unitario del producto
        """
        self.id_producto = id_producto
        self.producto_nombre = producto_nombre
        self.cantidad = cantidad
        self.cantidad_recibida = cantidad_recibida
        self.precio_unitario = float(precio_unitario)
    
    @property
    def subtotal(self):
        """
        Calcula el costo protectado de una linea del pedido.

        Returns:
            float: El resultado de multiplicar la cantidad pedida por el precio unitario.
        """
        return self.cantidad * self.precio_unitario

class Pedido:
    """
    Representa una orden de compra o pedido de reposicion emitido a un provedor.

    Agrupa multiples items (DetallePedido) y gestiona los tiempos de entrega, el estado del tramite y las observaciones relevantes de la compra.
    """
    def __init__(self, id_pedido=None, numero_pedido="", id_proveedor=None,
                 proveedor_nombre="", fecha_pedido=None, fecha_entrega_esperada=None,
                 detalles=None, id_estado=1, observaciones="", usuario=""):
        """
        Inicializa una nueva orden de pedido.

        Args:
            id_pedido (int, opcional): ID de la orden en la base de datos.
            numero_pedido (str, opcional): Numero de la orden de compra.
            id_proveedor (int, opcional): ID del proveedor principal del articulo (FK).
            proveedor_nombre (str, opcional): Nombre del proveedor.
            fecha_pedido (datetime, opcional): Fecha de la orden de pedido.
            fecha_entrega_esperada (datetime, opcional): Fecha de entrega esperada.
            detalles (list, opcional): Lista de DetallePedido.
            id_estado (int, opcional): ID del estado de la orden de pedido.
            observaciones (str, opcional): Observaciones adicionales sobre la orden de pedido.
            usuario (str, opcional): Usuario que realizo la orden de pedido.
        """
        self.id_pedido = id_pedido
        self.numero_pedido = numero_pedido
        self.id_proveedor = id_proveedor
        self.proveedor_nombre = proveedor_nombre
        self.fecha_pedido = fecha_pedido or datetime.now()
        self.fecha_entrega_esperada = fecha_entrega_esperada
        self.detalles = detalles or []
        self.id_estado = id_estado
        self.observaciones = observaciones
        self.usuario = usuario
    
    @property
    def total(self):
        """
        Calcula el costo total estimado de la orden de compra completa.

        Returns:
            float: La suma de los subtotales de todos los detalles incluidos en el pedido.
        """
        return sum(d.subtotal for d in self.detalles)