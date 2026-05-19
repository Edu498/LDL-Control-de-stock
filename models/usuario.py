class Usuario:
    def __init__(self, id_usuario=None, nombre_usuario="", nombre_completo="", 
                 email="", id_rol=None, rol_nombre="", activo=True):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.nombre_completo = nombre_completo
        self.email = email
        self.id_rol = id_rol
        self.rol_nombre = rol_nombre
        self.activo = activo
    
    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol_nombre,
            'activo': self.activo
        }