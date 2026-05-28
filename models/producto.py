# models/producto_modelo.py
# -*- coding: utf-8 -*-

class Producto:
    def __init__(self, id_producto=None, codigo="", nombre="", descripcion="",
                 id_categoria=None, id_proveedor=None, precio_compra=0.0,
                 precio_venta=0.0, stock_actual=0, stock_minimo=5, 
                 stock_maximo=None, ubicacion="", unidad_medida="unidad", activo=True,
                 **kwargs):
        # kwargs para ignorar campos extras
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_categoria = id_categoria
        self.id_proveedor = id_proveedor
        self.precio_compra = float(precio_compra)
        self.precio_venta = float(precio_venta)
        self.stock_actual = int(stock_actual)
        self.stock_minimo = int(stock_minimo)
        self.stock_maximo = int(stock_maximo) if stock_maximo else None
        self.ubicacion = ubicacion
        self.unidad_medida = unidad_medida
        self.activo = activo
    
    @property
    def estado_stock(self):
        """Retorna el estado del stock como string"""
        if self.stock_actual <= 0:
            return "SIN STOCK"
        elif self.stock_actual <= self.stock_minimo:
            return "STOCK BAJO"
        else:
            return "NORMAL"
    
    @property
    def icono_estado(self):
        """Retorna el icono según el estado del stock"""
        if self.stock_actual <= 0:
            return "🔴"
        elif self.stock_actual <= self.stock_minimo:
            return "🟡"
        else:
            return "🟢"
    
    @property
    def necesita_reposicion(self):
        return self.stock_actual <= self.stock_minimo
    
    @property
    def cantidad_recomendada(self):
        if self.stock_actual < self.stock_minimo:
            return self.stock_minimo - self.stock_actual
        return 0
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario (como viene de la BD)"""
        return cls(
            id_producto=data.get('id_producto'),
            codigo=data.get('codigo', ''),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            id_categoria=data.get('id_categoria'),
            id_proveedor=data.get('id_proveedor'),
            precio_compra=data.get('precio_compra', 0),
            precio_venta=data.get('precio_venta', 0),
            stock_actual=data.get('stock_actual', 0),
            stock_minimo=data.get('stock_minimo', 5),
            stock_maximo=data.get('stock_maximo'),
            ubicacion=data.get('ubicacion', ''),
            unidad_medida=data.get('unidad_medida', 'unidad'),
            activo=data.get('activo', True)
        )
    
    def to_dict(self):
        return {
            'id_producto': self.id_producto,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'id_categoria': self.id_categoria,
            'id_proveedor': self.id_proveedor,
            'precio_compra': self.precio_compra,
            'precio_venta': self.precio_venta,
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'stock_maximo': self.stock_maximo,
            'ubicacion': self.ubicacion,
            'unidad_medida': self.unidad_medida,
            'activo': self.activo,
            'estado': self.estado_stock,
            'icono': self.icono_estado
        }