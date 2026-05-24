# -*- coding: utf-8 -*-
"""
Modelo de datos para los Proveedores del sistema.
"""

class Proveedor:
    """
    Representa a los proveedores o proveedores externos de los cuales el negocio adquiere mercaderia.

    Permite mantener un registro actualizado de datos de contacto, documentacion (RUC), creditos y estado de actividad para agilizar la gestion de compras. 
    """
    def __init__(self, id_proveedor=None, nombre="", ruc="", telefono="", 
                 email="", direccion="", contacto_nombre="", contacto_telefono="", activo=True):
        """
        Inicializa una instancia de Proveedor.

        Args:
            id_proveedor (int, opcional): ID del proveedor en la base de datos.
            nombre (str, opcional): Nombre del proveedor.
            ruc (str, opcional): RUC del proveedor.
            telefono (str, opcional): Telefono del proveedor.
            email (str, opcional): Email del proveedor.
            direccion (str, opcional): Direccion del proveedor.
            contacto_nombre (str, opcional): Nombre del contacto del proveedor.
            contacto_telefono (str, opcional): Telefono del contacto del proveedor.
            activo (bool, opcional): Indica si el proveedor esta activo.
        """
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.ruc = ruc
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.contacto_nombre = contacto_nombre
        self.contacto_telefono = contacto_telefono
        self.activo = activo
    
    def to_dict(self):
        """
        Convierte la instancia de Proveedor a un diccionario.

        Returns:
            dict: Diccionario con los datos del proveedor.
        """
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