# -*- coding: utf-8 -*-
"""
Modelo de datos para Usuarios del sistema y sus Roles.
"""

class Usuario:
    """
    Representa a los usuarios o empleados que utilizan el sistema de gestion de inventario.

    Permite mantener un registro actualizado de datos de contacto, roles y estado de actividad para agilizar la gestion de usuarios.
    """
    def __init__(self, id_usuario=None, nombre_usuario="", nombre_completo="", 
                 email="", id_rol=None, rol_nombre="", activo=True):
        """
        Inicializa una instancia de Usuario.

        Args:
            id_usuario (int, opcional): ID del usuario en la base de datos.
            nombre_usuario (str, opcional): Nombre de usuario.
            nombre_completo (str, opcional): Nombre completo del usuario.
            email (str, opcional): Email del usuario.
            id_rol (int, opcional): ID del rol del usuario.
            rol_nombre (str, opcional): Nombre del rol del usuario.
            activo (bool, opcional): Indica si el usuario esta activo.
        """
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.nombre_completo = nombre_completo
        self.email = email
        self.id_rol = id_rol
        self.rol_nombre = rol_nombre
        self.activo = activo
    
    def to_dict(self):
        """
        Convierte la instancia de Usuario a un diccionario.

        Returns:
            dict: Diccionario con los datos del usuario.
        """
        return {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol_nombre,
            'activo': self.activo
        }