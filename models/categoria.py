# models/categoria_modelo.py
# -*- coding: utf-8 -*-

class Categoria:
    def __init__(self, id_categoria=None, nombre="", descripcion="", activo=True, **kwargs):
        # kwargs permite recibir cualquier campo extra (como fecha_creacion) sin error
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.activo = activo
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario (como viene de la BD)"""
        return cls(
            id_categoria=data.get('id_categoria'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            activo=data.get('activo', True)
        )
    
    def to_dict(self):
        return {
            'id_categoria': self.id_categoria,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo
        }