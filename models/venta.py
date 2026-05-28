from datetime import datetime

class DetalleVenta:
    def __init__(self, id_producto=None, producto_nombre="", cantidad=0, precio_unitario=0.0):
        self.id_producto = id_producto
        self.producto_nombre = producto_nombre
        self.cantidad = cantidad
        self.precio_unitario = float(precio_unitario)
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class Venta:
    def __init__(self, id_venta=None, numero_factura="", fecha_venta=None,
                 cliente_nombre="", detalles=None, id_estado=1, usuario=""):
        self.id_venta = id_venta
        self.numero_factura = numero_factura
        self.fecha_venta = fecha_venta or datetime.now()
        self.cliente_nombre = cliente_nombre or "CONSUMIDOR FINAL"
        self.detalles = detalles or []
        self.id_estado = id_estado
        self.usuario = usuario
    
    @property
    def subtotal(self):
        return sum(d.subtotal for d in self.detalles)
    
    @property
    def iva(self):
        return self.subtotal * 0.21
    
    @property
    def total(self):
        return self.subtotal + self.iva
    
    def agregar_detalle(self, id_producto, nombre, cantidad, precio):
        self.detalles.append(DetalleVenta(id_producto, nombre, cantidad, precio))