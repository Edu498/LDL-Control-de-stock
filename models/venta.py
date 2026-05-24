# -*- coding: utf-8 -*-
"""
Modelos de datos para Ventas y Facturación de Caja.
"""

from datetime import datetime

class DetalleVenta:
    """
        Representa un item individual dentro de una venta.

        Vincula un producto especifico con la cantidad vendida y el precio acordado al momento de la operacion.
        """
    def __init__(self, id_producto=None, producto_nombre="", cantidad=0, precio_unitario=0.0):
        """
        Inicializa una instancia de DetalleVenta.

        Args:
            id_producto (int, opcional): ID del producto vendido
            producto_nombre (str, opcional): Nombre del producto vendido
            cantidad (int, opcional): Cantidad de unidades vendidas
            precio_unitario (float, opcional): Precio unitario del producto
        """
        self.id_producto = id_producto
        self.producto_nombre = producto_nombre
        self.cantidad = cantidad
        self.precio_unitario = float(precio_unitario)
    
    @property
    def subtotal(self):
        """
        Calcula el costo total de esta linea de detalle (cantidad por precio unitario).

        Returns:
            float: El resultado de multiplicar la cantidad por el precio unitario.
        """
        return self.cantidad * self.precio_unitario

class Venta:
    """
    Representa la cabecera de una transaccion comercial o venta.

    Agrupa multiples items (DetalleVenta) y calcula automaticamente los importes totales, incluyendo el calculo impositivo.
    """
    def __init__(self, id_venta=None, numero_factura="", fecha_venta=None,
                 cliente_nombre="", detalles=None, id_estado=1, usuario=""):
        """
        Inicializa una instancia de Venta.

        Args:
            id_venta (int, opcional): ID de la venta en la base de datos.
            numero_factura (str, opcional): Numero de la factura.
            fecha_venta (datetime, opcional): Fecha de la venta.
            cliente_nombre (str, opcional): Nombre del cliente.
            detalles (list, opcional): Lista de DetalleVenta.
            id_estado (int, opcional): ID del estado de la venta.
            usuario (str, opcional): Usuario que realizo la venta.
        """
        self.id_venta = id_venta
        self.numero_factura = numero_factura
        self.fecha_venta = fecha_venta or datetime.now()
        self.cliente_nombre = cliente_nombre or "CONSUMIDOR FINAL"
        self.detalles = detalles or []
        self.id_estado = id_estado
        self.usuario = usuario
    
    @property
    def subtotal(self):
        """
        Calcula la suma de los subtotales de todos los detalles incluidos en la venta.

        Returns:
            float: Importe total de la venta sin aplicar impuestos.
        """
        return sum(d.subtotal for d in self.detalles)
    
    @property
    def iva(self):
        """
        Calcula el Impuesto al Valor Agregado.

        Returns:
            float: El 21% del subtotal de la venta.
        """
        return self.subtotal * 0.21
    
    @property
    def total(self):
        """
        Calcula el importe final a cobrar al cliente.

        Returns:
            float: La suma del subtotal y el IVA.
        """
        return self.subtotal + self.iva
    
    def agregar_detalle(self, id_producto, nombre, cantidad, precio):
        """
        Crea un nuevo objeto DetalleVenta y lo añade a la lista de detalles de esta venta.
        
        Args:
            id_producto (int): ID del producto vendido.
            nombre (str): Nombre descriptivo del producto.
            cantidad (int): Unidades vendidas de este ítem.
            precio (float): Precio unitario acordado para esta venta.
        """
        self.detalles.append(DetalleVenta(id_producto, nombre, cantidad, precio))