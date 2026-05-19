class Categoria:
    def __init__(self, id_categoria=None, nombre="", descripcion="", activo=True):
        self.id_categoria = id_categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.activo = activo
    
    def to_dict(self):
        return {
            'id_categoria': self.id_categoria,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo
        }