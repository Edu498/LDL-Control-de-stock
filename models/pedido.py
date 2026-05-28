from datetime import datetime

class DetallePedido:
    def __init__(self, id_producto=None, producto_nombre="", cantidad=0, 
                 cantidad_recibida=0, precio_unitario=0.0):
        self.id_producto = id_producto
        self.producto_nombre = producto_nombre
        self.cantidad = cantidad
        self.cantidad_recibida = cantidad_recibida
        self.precio_unitario = float(precio_unitario)
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class Pedido:
    def __init__(self, id_pedido=None, numero_pedido="", id_proveedor=None,
                 proveedor_nombre="", fecha_pedido=None, fecha_entrega_esperada=None,
                 detalles=None, id_estado=1, observaciones="", usuario=""):
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
        return sum(d.subtotal for d in self.detalles)