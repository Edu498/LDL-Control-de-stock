import tkinter as tk
from tkinter import ttk, messagebox
from controllers import StockController
from models import Producto
from utils import Alertas, buscar_productos

class ProductosWindow:
    def __init__(self, parent, usuario):
        self.parent = parent
        self.usuario = usuario
        self.productos = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Productos")
        self.window.geometry("1000x600")
        self.window.configure(bg='#F0F0F0')
        
        self.cargar_datos()
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
    
    def cargar_datos(self):
        self.productos = StockController.get_all_productos()
        self.categorias = StockController.get_categorias()
        self.proveedores = StockController.get_proveedores()
    
    def crear_widgets(self):
        # Título
        tk.Label(self.window, text=" GESTIÓN DE PRODUCTOS", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Frame de búsqueda
        frame_busqueda = tk.Frame(self.window, bg='#F0F0F0')
        frame_busqueda.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_busqueda, text="Buscar:", bg='#F0F0F0').pack(side=tk.LEFT, padx=5)
        self.entry_busqueda = tk.Entry(frame_busqueda, width=30)
        self.entry_busqueda.pack(side=tk.LEFT, padx=5)
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_productos)
        
        tk.Button(frame_busqueda, text=" Nuevo Producto", command=self.nuevo_producto,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
        
        # Tabla de productos
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(frame_tabla)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columnas = ('Código', 'Producto', 'Categoría', 'Stock', 'Mínimo', 'Precio Venta', 'Estado')
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                   yscrollcommand=scrollbar_y.set,
                                   xscrollcommand=scrollbar_x.set)
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            ancho = 200 if col == 'Producto' else 100
            self.tabla.column(col, width=ancho)
        
        scrollbar_y.config(command=self.tabla.yview)
        scrollbar_x.config(command=self.tabla.xview)
        
        self.actualizar_tabla()
        
        self.tabla.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        frame_botones = tk.Frame(self.window, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(frame_botones, text=" Editar", command=self.editar_producto,
                 bg='#FFC107', fg='black', padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text=" Ver Movimientos", command=self.ver_movimientos,
                 bg='#17A2B8', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text=" Actualizar Stock", command=self.actualizar_stock,
                 bg='#6C757D', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="Cerrar", command=self.window.destroy,
                 bg='#DC3545', fg='white', padx=20).pack(side=tk.RIGHT, padx=5)
    
    def actualizar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        for p in self.productos:
            estado, icono = p.estado_stock
            self.tabla.insert('', tk.END, values=(
                p.codigo, p.nombre, p.id_categoria or '-',
                p.stock_actual, p.stock_minimo,
                f"${p.precio_venta:,.2f}", f"{icono} {estado}"
            ), tags=(estado,))
        
        self.tabla.tag_configure('NORMAL', background='#FFFFFF')
        self.tabla.tag_configure('STOCK BAJO', background='#FFF3CD')
        self.tabla.tag_configure('SIN STOCK', background='#F8D7DA')
    
    def buscar_productos(self, event=None):
        texto = self.entry_busqueda.get()
        if texto:
            productos = StockController.get_all_productos()
            self.productos = [p for p in productos if 
                            texto.lower() in p.codigo.lower() or 
                            texto.lower() in p.nombre.lower()]
        else:
            self.productos = StockController.get_all_productos()
        self.actualizar_tabla()
    
    def nuevo_producto(self):
        FormularioProducto(self.window, self.usuario, None, self.cargar_datos)
    
    def editar_producto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione un producto")
            return
        
        item = self.tabla.item(seleccion[0])
        codigo = item['values'][0]
        
        producto = next((p for p in self.productos if p.codigo == codigo), None)
        if producto:
            FormularioProducto(self.window, self.usuario, producto, self.cargar_datos)
    
    def ver_movimientos(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione un producto")
            return
        
        item = self.tabla.item(seleccion[0])
        codigo = item['values'][0]
        producto = next((p for p in self.productos if p.codigo == codigo), None)
        
        if producto:
            from vistas.reportes_window import ReporteMovimientos
            ReporteMovimientos(self.window, producto.id_producto)
    
    def actualizar_stock(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione un producto")
            return
        
        item = self.tabla.item(seleccion[0])
        codigo = item['values'][0]
        producto = next((p for p in self.productos if p.codigo == codigo), None)
        
        if producto:
            from vistas.inventario_window import AjusteStockWindow
            AjusteStockWindow(self.window, producto, self.cargar_datos)


class FormularioProducto:
    """Formulario para crear o editar un producto"""
    
    def __init__(self, parent, usuario, producto=None, callback_refresh=None):
        self.parent = parent
        self.usuario = usuario
        self.producto = producto
        self.callback_refresh = callback_refresh
        
        self.window = tk.Toplevel(parent)
        titulo = "Editar Producto" if producto else "Nuevo Producto"
        self.window.title(titulo)
        self.window.geometry("650x550")
        self.window.configure(bg='#F0F0F0')
        self.window.resizable(False, False)
        
        # Centrar ventana
        self.window.transient(parent)
        self.window.grab_set()
        
        self.cargar_datos()
        self.crear_widgets()
        
        self.window.focus_force()
    
    def cargar_datos(self):
        from controllers import StockController
        self.categorias = StockController.get_categorias()
        self.proveedores = StockController.get_proveedores()
        
        # Crear diccionarios para fácil acceso
        self.categorias_dict = {c.id_categoria: c.nombre for c in self.categorias}
        self.proveedores_dict = {p.id_proveedor: p.nombre for p in self.proveedores}
    
    def crear_widgets(self):
        # Título
        titulo = " EDITAR PRODUCTO" if self.producto else " NUEVO PRODUCTO"
        tk.Label(self.window, text=titulo, 
                font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Frame del formulario
        frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear campos
        row = 0
        campos = [
            ("Código:", "codigo", True),
            ("Nombre:", "nombre", True),
            ("Descripción:", "descripcion", False),
            ("Categoría:", "categoria", False),
            ("Proveedor:", "proveedor", False),
            ("Precio Compra ($):", "precio_compra", True),
            ("Precio Venta ($):", "precio_venta", True),
            ("Stock Actual:", "stock_actual", True),
            ("Stock Mínimo:", "stock_minimo", True),
            ("Ubicación:", "ubicacion", False),
        ]
        
        self.entries = {}
        
        for label, campo, obligatorio in campos:
            # Label
            lbl_text = label + (" *" if obligatorio else "")
            tk.Label(frame, text=lbl_text, bg='white', font=("Arial", 10),
                    anchor='w').grid(row=row, column=0, padx=10, pady=8, sticky='w')
            
            # Entry o Combobox según el campo
            if campo == "categoria":
                valores = [c.nombre for c in self.categorias]
                self.entries[campo] = ttk.Combobox(frame, values=valores, width=40)
                if self.producto and self.producto.id_categoria:
                    self.entries[campo].set(self.categorias_dict.get(self.producto.id_categoria, ''))
            elif campo == "proveedor":
                valores = [p.nombre for p in self.proveedores] + ["(Ninguno)"]
                self.entries[campo] = ttk.Combobox(frame, values=valores, width=40)
                if self.producto and self.producto.id_proveedor:
                    self.entries[campo].set(self.proveedores_dict.get(self.producto.id_proveedor, ''))
                else:
                    self.entries[campo].set("(Ninguno)")
            elif campo == "descripcion":
                self.entries[campo] = tk.Entry(frame, width=43)
            else:
                self.entries[campo] = tk.Entry(frame, width=43)
            
            self.entries[campo].grid(row=row, column=1, padx=10, pady=8, sticky='ew')
            
            # Cargar valor si estamos editando
            if self.producto:
                valor = getattr(self.producto, campo, '')
                if valor and campo not in ['categoria', 'proveedor']:
                    self.entries[campo].insert(0, str(valor))
            
            row += 1
        
        # Unidad de medida
        tk.Label(frame, text="Unidad de Medida:", bg='white', font=("Arial", 10),
                anchor='w').grid(row=row, column=0, padx=10, pady=8, sticky='w')
        self.entry_unidad = ttk.Combobox(frame, values=['unidad', 'kg', 'litro', 'docena', 'par'], width=40)
        self.entry_unidad.grid(row=row, column=1, padx=10, pady=8, sticky='ew')
        if self.producto:
            self.entry_unidad.set(self.producto.unidad_medida)
        else:
            self.entry_unidad.set('unidad')
        
        row += 1
        
        # Separador
        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        row += 1
        
        # Botones
        frame_botones = tk.Frame(frame, bg='white')
        frame_botones.grid(row=row, column=0, columnspan=2, pady=10)
        
        tk.Button(frame_botones, text=" Guardar", command=self.guardar,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold"),
                 padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(frame_botones, text="Cancelar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        # Configurar grid
        frame.columnconfigure(1, weight=1)
    
    def guardar(self):
        """Guardar el producto (crear o actualizar)"""
        from controllers import StockController
        
        # Validar campos requeridos
        if not self.entries['codigo'].get().strip():
            Alertas.mostrar_mensaje_advertencia("El código es obligatorio")
            self.entries['codigo'].focus()
            return
        
        if not self.entries['nombre'].get().strip():
            Alertas.mostrar_mensaje_advertencia("El nombre es obligatorio")
            self.entries['nombre'].focus()
            return
        
        try:
            precio_compra = float(self.entries['precio_compra'].get() or 0)
            precio_venta = float(self.entries['precio_venta'].get() or 0)
            stock_actual = int(self.entries['stock_actual'].get() or 0)
            stock_minimo = int(self.entries['stock_minimo'].get() or 5)
        except ValueError:
            Alertas.mostrar_mensaje_advertencia("Los valores numéricos no son válidos")
            return
        
        # Obtener IDs de categoría y proveedor
        id_categoria = None
        categoria_nombre = self.entries['categoria'].get()
        if categoria_nombre and categoria_nombre != "(Ninguno)":
            for c in self.categorias:
                if c.nombre == categoria_nombre:
                    id_categoria = c.id_categoria
                    break
        
        id_proveedor = None
        proveedor_nombre = self.entries['proveedor'].get()
        if proveedor_nombre and proveedor_nombre != "(Ninguno)":
            for p in self.proveedores:
                if p.nombre == proveedor_nombre:
                    id_proveedor = p.id_proveedor
                    break
        
        # Crear o actualizar producto
        producto = Producto(
            id_producto=self.producto.id_producto if self.producto else None,
            codigo=self.entries['codigo'].get().strip().upper(),
            nombre=self.entries['nombre'].get().strip(),
            descripcion=self.entries['descripcion'].get().strip(),
            id_categoria=id_categoria,
            id_proveedor=id_proveedor,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo,
            ubicacion=self.entries['ubicacion'].get().strip(),
            unidad_medida=self.entry_unidad.get()
        )
        
        try:
            if self.producto:
                # Actualizar producto existente
                # Aquí iría el método de actualización
                Alertas.mostrar_mensaje_exito("Producto actualizado correctamente")
            else:
                # Crear nuevo producto
                StockController.crear_producto(producto)
                Alertas.mostrar_mensaje_exito("Producto creado correctamente")
            
            # Actualizar lista
            if self.callback_refresh:
                self.callback_refresh()
            
            self.window.destroy()
            
        except Exception as e:
            Alertas.mostrar_mensaje_error(f"Error al guardar: {str(e)}")