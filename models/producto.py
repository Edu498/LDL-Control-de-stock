# -*- coding: utf-8 -*-
"""
Modelo de datos para Productos en el catálogo de Inventario.
"""

class Producto:
    """
    Representa un insumo o producto final dentro del sistema de inventario

    Esta clase gestiona la información detallada de cada artículo, incluyendo sus metricas de stock, categorización,
    precios y la logica de negocio para determinar automaticamente si requiere reposición.
    """
    def __init__(self, id_producto=None, codigo="", nombre="", descripcion="",
                 id_categoria=None, id_proveedor=None, precio_compra=0.0,
                 precio_venta=0.0, stock_actual=0, stock_minimo=5, 
                 stock_maximo=None, ubicacion="", unidad_medida="unidad", activo=True):
        """
        Inicializa una nueva instancia de la clase Producto.

        Args:
            id_producto (int, optional): Identificador único del producto en la base de datos.
            codigo (str, optional): Código de barras o identificador interno. Por defecto "".
            nombre (str, optional): Nombre del producto o insumo. Por defecto "".
            descripcion (str, optional): Detalles adicionales del artículo. Por defecto "".
            id_categoria (int, optional): ID de la categoría a la que pertenece (FK).
            id_proveedor (int, optional): ID del proveedor principal del artículo (FK).
            precio_compra (float, optional): Costo de adquisición del producto. Por defecto 0.0.
            precio_venta (float, optional): Precio de venta al público. Por defecto 0.0.
            stock_actual (int, optional): Cantidad física actual en el local/depósito. Por defecto 0.
            stock_minimo (int, optional): Umbral mínimo para disparar alertas de reposición. Por defecto 5.
            stock_maximo (int, optional): Límite de capacidad en depósito para este artículo.
            ubicacion (str, optional): Pasillo, estante o sector donde se almacena. Por defecto "".
            unidad_medida (str, optional): Ej: "unidad", "kg", "litros". Por defecto "unidad".
            activo (bool, optional): Indica si el producto sigue siendo comercializado/usado. Por defecto True.
        """
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
        """
        Evalúa el stock actual y determina la situación del articulo.

        Returns:
            str: Devuelve el estado del stock ('SIN STOCK', 'STOCK BAJO' o 'NORMAL')
        """
        if self.stock_actual <= 0:
            return ("SIN STOCK")
        elif self.stock_actual <= self.stock_minimo:
            return ("STOCK BAJO")
        else:
            return ("NORMAL")
    
    @property
    def necesita_reposicion(self):
        """
        Verifica si el articulo alcanzo o perforo el stock minimo.

        Returns:
            bool: True si necesita reposicion, False en caso contrario.
        """
        return self.stock_actual <= self.stock_minimo
    
    @property
    def cantidad_recomendada(self):
        """
        Calcula la cantidad de unidades que deberian ordenarse para alcanzar el stock maximo.
        
        Returns:
            int: La diferencia entre el stock maximo y el stock actual. Devuelve 0 si el stock es normal.
         """
        if self.stock_actual < self.stock_minimo:
            return self.stock_minimo - self.stock_actual
        return 0
    
    def to_dict(self):
        """
        Convierte la instancia actual a un diccionario, incluyendo los metodos calculados.

        Es ideal para serializar la informacion del producto y facilitar su transferencia o exibicion.
        
        Returns:
            dict: Diccionario con todos los datos del producto. Incluye el estado del stock, si necesita reposicion y la cantidad recomendada.
        """
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
            'estado': self.estado_stock[0],
            'icono': self.estado_stock[1]
        }