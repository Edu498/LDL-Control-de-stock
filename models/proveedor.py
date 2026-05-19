class Proveedor:
    def __init__(self, id_proveedor=None, nombre="", ruc="", telefono="", 
                 email="", direccion="", contacto_nombre="", contacto_telefono="", activo=True):
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