# models/proveedor_modelo.py
# -*- coding: utf-8 -*-

class Proveedor:
    def __init__(self, id_proveedor=None, nombre="", ruc="", telefono="", 
                 email="", direccion="", contacto_nombre="", contacto_telefono="", 
                 activo=True, **kwargs):
        # kwargs permite recibir cualquier campo extra (como fecha_creacion) sin error
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.ruc = ruc
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.contacto_nombre = contacto_nombre
        self.contacto_telefono = contacto_telefono
        self.activo = activo
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario (como viene de la BD)"""
        return cls(
            id_proveedor=data.get('id_proveedor'),
            nombre=data.get('nombre', ''),
            ruc=data.get('ruc', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            direccion=data.get('direccion', ''),
            contacto_nombre=data.get('contacto_nombre', ''),
            contacto_telefono=data.get('contacto_telefono', ''),
            activo=data.get('activo', True)
        )
    
    def to_dict(self):
        return {
            'id_proveedor': self.id_proveedor,
            'nombre': self.nombre,
            'ruc': self.ruc,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'contacto_nombre': self.contacto_nombre,
            'contacto_telefono': self.contacto_telefono,
            'activo': self.activo
        }