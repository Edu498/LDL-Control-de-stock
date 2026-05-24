# -*- coding: utf-8 -*-
"""
Modelo de datos para las Categorías de productos.
"""

class Categoria:
    """
    Representa las distintas categorias o tipos de productos que comercializa el negocio.

    Permite organizar el inventario tematicamente para facilitar la navegacion, el etiquetado y el analisis de ventas por rubro.
    """
    def __init__(self, id_categoria=None, nombre="", descripcion="", activo=True):
        """
        Inicializa una instancia de Categoria.

        Args:
            id_categoria (int, opcional): ID de la categoria en la base de datos.
            nombre (str, opcional): Nombre de la categoria.
            descripcion (str, opcional): Descripcion de la categoria.
            activo (bool, opcional): Indica si la categoria esta activa.
        """
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.activo = activo
    
    def to_dict(self):
        """
        Convierte la instancia de Categoria a un diccionario.

        Returns:
            dict: Diccionario con los datos de la categoria.
        """
        return {
            'id_categoria': self.id_categoria,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo
        }