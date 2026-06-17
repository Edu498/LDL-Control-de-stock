# vistas/productos_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers import StockController
from models import Producto
from utils import Alertas
from utils.eventos import Eventos, EVENTO_PRODUCTO_AGREGADO, EVENTO_STOCK_ACTUALIZADO
from utils.database import get_connection

class ProductosWindow:
    def __init__(self, parent, usuario, main_app=None):
        self.parent = parent
        self.usuario = usuario
        self.main_app = main_app
        self.productos = []
        
        if main_app:
            self.window = tk.Frame(parent, bg='#F0F0F0')
            self.window.pack(fill=tk.BOTH, expand=True)
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Gestion de Productos")
            self.window.geometry("1100x650")
            self.window.configure(bg='#F0F0F0')
            self.window.transient(parent.winfo_toplevel())
            self.window.grab_set()
            self.window.focus_force()
        
        self.cargar_datos()
        self.crear_widgets()
        
        Eventos.suscribir(EVENTO_STOCK_ACTUALIZADO, self.refrescar_tabla)
    
    def cargar_datos(self):
        self.productos = StockController.get_all_productos()
        self.categorias = StockController.get_categorias()
        self.proveedores = StockController.get_proveedores()
        self.categorias_dict = {c.id_categoria: c.nombre for c in self.categorias}
    
    def refrescar_tabla(self, datos=None):
        self.cargar_datos()
        self.actualizar_tabla()
    
    def crear_widgets(self):
        tk.Label(self.window, text="GESTION DE PRODUCTOS", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_busqueda = tk.Frame(self.window, bg='#F0F0F0')
        frame_busqueda.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_busqueda, text="Buscar:", bg='#F0F0F0').pack(side=tk.LEFT, padx=5)
        self.entry_busqueda = tk.Entry(frame_busqueda, width=30)
        self.entry_busqueda.pack(side=tk.LEFT, padx=5)
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_productos)
        
        tk.Button(frame_busqueda, text="Nuevo Producto", command=self.nuevo_producto,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
        
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(frame_tabla)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columnas = ('Codigo', 'Producto', 'Categoria', 'Stock', 'Minimo', 'Precio Venta', 'Estado')
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
        
        self.tabla.bind('<Double-Button-1>', self.editar_stock_directo)
        
        frame_botones = tk.Frame(self.window, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(frame_botones, text="Editar Producto", command=self.editar_producto,
                 bg='#FFC107', fg='black', padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="Ver Movimientos", command=self.ver_movimientos,
                 bg='#17A2B8', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
        command_cerrar = self.main_app._mostrar_dashboard if self.main_app else self.window.destroy
        tk.Button(frame_botones, text="Cerrar", command=command_cerrar,
                 bg='#DC3545', fg='white', padx=20).pack(side=tk.RIGHT, padx=5)
        
        tk.Label(self.window, text="Doble clic en cualquier producto para editar el stock", 
                font=("Arial", 9), bg='#F0F0F0', fg='#6C757D').pack(pady=5)
    
    def actualizar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        for p in self.productos:
            estado = p.estado_stock
            icono = p.icono_estado
            categoria_nombre = getattr(self, 'categorias_dict', {}).get(p.id_categoria, '-')
            
            self.tabla.insert('', tk.END, values=(
                p.codigo, p.nombre, categoria_nombre,
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
    
    def editar_stock_directo(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        
        item = self.tabla.item(seleccion[0])
        valores = item['values']
        codigo = valores[0]
        
        producto = next((p for p in self.productos if p.codigo == codigo), None)
        if producto:
            self.mostrar_dialogo_stock(producto)
    
    def mostrar_dialogo_stock(self, producto):
        """Muestra diálogo para ajustar stock - Usando la misma lógica que AjusteStockWindow"""
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Ajuste de Stock - {producto.nombre}")
        dialog.geometry("600x700")
        dialog.configure(bg='#F0F0F0')
        dialog.resizable(False, False)
        dialog.transient(self.window.winfo_toplevel())
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 600) // 2
        y = (dialog.winfo_screenheight() - 700) // 2
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Contenido
        frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        tk.Label(frame, text="AJUSTE DE STOCK", font=("Arial", 16, "bold"), 
                bg='white', fg='#2C3E50').pack(pady=10)
        
        tk.Label(frame, text=producto.nombre, font=("Arial", 14, "bold"), 
                bg='white', fg='#007BFF').pack()
        
        tk.Label(frame, text=f"Código: {producto.codigo}", bg='white', 
                font=("Arial", 10)).pack()
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Stock actual
        stock_frame = tk.Frame(frame, bg='white')
        stock_frame.pack(pady=10)
        
        tk.Label(stock_frame, text="Stock Actual:", font=("Arial", 12), 
                bg='white').pack(side=tk.LEFT)
        
        color_stock = "#28A745" if producto.stock_actual >= producto.stock_minimo else "#DC3545"
        lbl_stock = tk.Label(stock_frame, text=str(producto.stock_actual), 
                            font=("Arial", 28, "bold"), bg='white', fg=color_stock)
        lbl_stock.pack(side=tk.LEFT, padx=15)
        
        tk.Label(stock_frame, text=f"(Mínimo: {producto.stock_minimo})", 
                bg='white', font=("Arial", 10)).pack(side=tk.LEFT)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Tipo de operación
        tk.Label(frame, text="Tipo de Operación:", font=("Arial", 12, "bold"), 
                bg='white').pack(anchor=tk.W, pady=(5,10))
        
        tipo_var = tk.StringVar(value="agregar")
        radio_frame = tk.Frame(frame, bg='white')
        radio_frame.pack(fill=tk.X, pady=5)
        
        rb_agregar = tk.Radiobutton(radio_frame, text="AGREGAR STOCK", variable=tipo_var,
                      value="agregar", bg='white', font=("Arial", 11, "bold"), fg='#28A745',
                      selectcolor='white', indicatoron=1)
        rb_agregar.pack(side=tk.LEFT, padx=10)
        
        rb_quitar = tk.Radiobutton(radio_frame, text="QUITAR STOCK", variable=tipo_var,
                      value="quitar", bg='white', font=("Arial", 11, "bold"), fg='#DC3545',
                      selectcolor='white', indicatoron=1)
        rb_quitar.pack(side=tk.LEFT, padx=10)
        
        rb_conteo = tk.Radiobutton(radio_frame, text="CONTEO FÍSICO", variable=tipo_var,
                      value="conteo", bg='white', font=("Arial", 11, "bold"), fg='#3498DB',
                      selectcolor='white', indicatoron=1)
        rb_conteo.pack(side=tk.LEFT, padx=10)
        
        # Cantidad
        tk.Label(frame, text="Cantidad:", font=("Arial", 12, "bold"), 
                bg='white').pack(anchor=tk.W, pady=(15,5))
        
        spin_frame = tk.Frame(frame, bg='white')
        spin_frame.pack(fill=tk.X, pady=5)
        
        spin_cantidad = tk.Spinbox(spin_frame, from_=1, to=9999, width=15, 
                                    font=("Arial", 16), justify='center')
        spin_cantidad.pack()
        spin_cantidad.delete(0, tk.END)
        spin_cantidad.insert(0, "1")
        
        # Motivo
        tk.Label(frame, text="Motivo del Ajuste:", font=("Arial", 12, "bold"), 
                bg='white').pack(anchor=tk.W, pady=(15,5))
        
        combo_motivo = ttk.Combobox(frame, values=[
            'Ajuste de inventario',
            'Corrección de stock', 
            'Merma o rotura',
            'Devolución de cliente',
            'Ingreso por compra',
            'Egreso por venta',
            'Conteo físico periódico'
        ], width=45, font=("Arial", 11))
        combo_motivo.pack(fill=tk.X, pady=5)
        combo_motivo.set('Ajuste de inventario')
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Stock nuevo estimado
        nuevo_frame = tk.Frame(frame, bg='white')
        nuevo_frame.pack(pady=10)
        
        tk.Label(nuevo_frame, text="Stock Nuevo:", font=("Arial", 12), 
                bg='white').pack(side=tk.LEFT)
        
        lbl_nuevo = tk.Label(nuevo_frame, text=str(producto.stock_actual), 
                            font=("Arial", 28, "bold"), bg='white', fg='#007BFF')
        lbl_nuevo.pack(side=tk.LEFT, padx=15)
        
        def actualizar_estimacion(*args):
            try:
                cantidad = int(spin_cantidad.get())
                if cantidad <= 0:
                    cantidad = 1
                    spin_cantidad.delete(0, tk.END)
                    spin_cantidad.insert(0, "1")
                
                if tipo_var.get() == "quitar":
                    if cantidad > producto.stock_actual:
                        cantidad = producto.stock_actual
                        spin_cantidad.delete(0, tk.END)
                        spin_cantidad.insert(0, str(cantidad))
                    nuevo = producto.stock_actual - cantidad
                    if nuevo < 0:
                        nuevo = 0
                    lbl_nuevo.config(fg='#DC3545')
                elif tipo_var.get() == "conteo":
                    nuevo = cantidad
                    lbl_nuevo.config(fg='#3498DB')
                else:
                    nuevo = producto.stock_actual + cantidad
                    lbl_nuevo.config(fg='#28A745')
                
                lbl_nuevo.config(text=str(nuevo))
            except:
                pass
        
        # Vincular eventos
        spin_cantidad.bind('<KeyRelease>', actualizar_estimacion)
        rb_agregar.config(command=actualizar_estimacion)
        rb_quitar.config(command=actualizar_estimacion)
        rb_conteo.config(command=actualizar_estimacion)
        
        # Botones
        btn_frame = tk.Frame(frame, bg='white')
        btn_frame.pack(pady=20)
        
        def guardar_cambio():
            try:
                cantidad = int(spin_cantidad.get())
                if cantidad <= 0:
                    raise ValueError
            except:
                messagebox.showwarning("Error", "Ingrese una cantidad válida (mayor a 0)")
                return
            
            # ========== DEBUG ==========
            print("\n" + "=" * 50)
            print("🔍 PRODUCTOS_WINDOW - guardar_cambio")
            print(f"   tipo_var.get() = {tipo_var.get()}")
            print(f"   cantidad = {cantidad}")
            print(f"   stock_actual = {producto.stock_actual}")
            # ===========================
            
            # MISMA LÓGICA QUE AJUSTEStockWindow
            if tipo_var.get() == "quitar":
                if cantidad > producto.stock_actual:
                    messagebox.showwarning(
                        "Error",
                        f"No puede quitar más stock del disponible.\n"
                        f"Stock actual: {producto.stock_actual} unidades\n"
                        f"Intenta quitar: {cantidad} unidades"
                    )
                    return
                cantidad_ajuste = -cantidad  # NEGATIVO para SALIDA
                tipo_mov = 4  # Ajuste Negativo
                texto_operacion = f"QUITAR {cantidad} unidades"
            elif tipo_var.get() == "conteo":
                diferencia = cantidad - producto.stock_actual
                if diferencia == 0:
                    messagebox.showwarning("Aviso", "El stock es el mismo, no hay ajuste que hacer.")
                    return
                cantidad_ajuste = diferencia
                tipo_mov = 3 if diferencia > 0 else 4
                texto_operacion = f"CONTEO FÍSICO ({diferencia:+})"
                if combo_motivo.get() == 'Ajuste de inventario':
                    combo_motivo.set('Conteo físico periódico')
            else:
                cantidad_ajuste = cantidad   # POSITIVO para ENTRADA
                tipo_mov = 3  # Ajuste Positivo
                texto_operacion = f"AGREGAR {cantidad} unidades"
            
            # ========== DEBUG ==========
            print(f"   cantidad_ajuste = {cantidad_ajuste}")
            print(f"   tipo_mov = {tipo_mov}")
            print("=" * 50)
            # ===========================
            
            try:
                usuario_actual = "admin"
                if self.usuario:
                    if isinstance(self.usuario, dict):
                        usuario_actual = self.usuario.get('nombre_usuario', 'admin')
                    else:
                        usuario_actual = str(self.usuario)
                
                nuevo_stock = StockController.actualizar_stock(
                    id_producto=producto.id_producto,
                    cantidad=cantidad_ajuste,
                    tipo_movimiento=tipo_mov,
                    usuario=usuario_actual,
                    referencia={'tipo': 'ajuste', 'motivo': combo_motivo.get()}
                )
                
                # Mostrar mensaje de éxito
                msg = f"✅ STOCK ACTUALIZADO CORRECTAMENTE\n\n"
                msg += f"Producto: {producto.nombre}\n"
                msg += f"Operación: {texto_operacion}\n"
                msg += f"Motivo: {combo_motivo.get()}\n\n"
                msg += f"Stock anterior: {producto.stock_actual} unidades\n"
                msg += f"Stock nuevo: {nuevo_stock} unidades"
                
                messagebox.showinfo("Éxito", msg)
                
                # Actualizar el objeto producto
                producto.stock_actual = nuevo_stock
                
                # Notificar cambio
                Eventos.notificar(EVENTO_STOCK_ACTUALIZADO, {
                    'id_producto': producto.id_producto,
                    'stock_nuevo': nuevo_stock
                })
                
                # Refrescar la tabla
                self.cargar_datos()
                self.actualizar_tabla()
                
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}")
                import traceback
                traceback.print_exc()
        
        btn_guardar = tk.Button(btn_frame, text="GUARDAR CAMBIOS", command=guardar_cambio,
                 bg='#28A745', fg='white', font=("Arial", 12, "bold"),
                 padx=35, pady=10, cursor='hand2')
        btn_guardar.pack(side=tk.LEFT, padx=10)
        
        btn_cancelar = tk.Button(btn_frame, text="CANCELAR", command=dialog.destroy,
                 bg='#6C757D', fg='white', font=("Arial", 12),
                 padx=25, pady=10, cursor='hand2')
        btn_cancelar.pack(side=tk.LEFT, padx=10)
        
        def on_enter(e):
            btn_guardar.config(bg='#218838')
        
        def on_leave(e):
            btn_guardar.config(bg='#28A745')
        
        btn_guardar.bind('<Enter>', on_enter)
        btn_guardar.bind('<Leave>', on_leave)
        
        actualizar_estimacion()
    
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


class FormularioProducto:
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
        
        self.window.transient(parent.winfo_toplevel())
        self.window.grab_set()
        
        self.cargar_datos()
        self.crear_widgets()
        self.window.focus_force()
    
    def cargar_datos(self):
        from controllers import StockController
        self.categorias = StockController.get_categorias()
        self.proveedores = StockController.get_proveedores()
        self.categorias_dict = {c.id_categoria: c.nombre for c in self.categorias}
        self.proveedores_dict = {p.id_proveedor: p.nombre for p in self.proveedores}
    
    def crear_widgets(self):
        titulo = "EDITAR PRODUCTO" if self.producto else "NUEVO PRODUCTO"
        tk.Label(self.window, text=titulo, 
                font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        row = 0
        campos = [
            ("Codigo:", "codigo", True),
            ("Nombre:", "nombre", True),
            ("Descripcion:", "descripcion", False),
            ("Categoria:", "categoria", False),
            ("Proveedor:", "proveedor", False),
            ("Precio Compra ($):", "precio_compra", True),
            ("Precio Venta ($):", "precio_venta", True),
            ("Stock Actual:", "stock_actual", True),
            ("Stock Minimo:", "stock_minimo", True),
            ("Ubicacion:", "ubicacion", False),
        ]
        
        self.entries = {}
        
        for label, campo, obligatorio in campos:
            lbl_text = label + (" *" if obligatorio else "")
            tk.Label(frame, text=lbl_text, bg='white', font=("Arial", 10),
                    anchor='w').grid(row=row, column=0, padx=10, pady=8, sticky='w')
            
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
            
            if self.producto:
                valor = getattr(self.producto, campo, '')
                if valor and campo not in ['categoria', 'proveedor']:
                    self.entries[campo].insert(0, str(valor))
            
            row += 1
        
        tk.Label(frame, text="Unidad de Medida:", bg='white', font=("Arial", 10),
                anchor='w').grid(row=row, column=0, padx=10, pady=8, sticky='w')
        self.entry_unidad = ttk.Combobox(frame, values=['unidad', 'kg', 'litro', 'docena', 'par'], width=40)
        self.entry_unidad.grid(row=row, column=1, padx=10, pady=8, sticky='ew')
        if self.producto:
            self.entry_unidad.set(self.producto.unidad_medida)
        else:
            self.entry_unidad.set('unidad')
        
        row += 1
        
        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        row += 1
        
        frame_botones = tk.Frame(frame, bg='white')
        frame_botones.grid(row=row, column=0, columnspan=2, pady=10)
        
        tk.Button(frame_botones, text="Guardar", command=self.guardar,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold"),
                 padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(frame_botones, text="Cancelar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        frame.columnconfigure(1, weight=1)
    
    def guardar(self):
        from controllers import StockController
        
        if not self.entries['codigo'].get().strip():
            Alertas.mostrar_mensaje_advertencia("El codigo es obligatorio")
            return
        
        if not self.entries['nombre'].get().strip():
            Alertas.mostrar_mensaje_advertencia("El nombre es obligatorio")
            return
        
        try:
            precio_compra = float(self.entries['precio_compra'].get() or 0)
            precio_venta = float(self.entries['precio_venta'].get() or 0)
            stock_nuevo = int(self.entries['stock_actual'].get() or 0)
            stock_minimo = int(self.entries['stock_minimo'].get() or 5)
        except ValueError:
            Alertas.mostrar_mensaje_advertencia("Los valores numericos no son validos")
            return
        
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
        
        producto = Producto(
            id_producto=self.producto.id_producto if self.producto else None,
            codigo=self.entries['codigo'].get().strip().upper(),
            nombre=self.entries['nombre'].get().strip(),
            descripcion=self.entries['descripcion'].get().strip(),
            id_categoria=id_categoria,
            id_proveedor=id_proveedor,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock_actual=stock_nuevo,
            stock_minimo=stock_minimo,
            ubicacion=self.entries['ubicacion'].get().strip(),
            unidad_medida=self.entry_unidad.get()
        )
        
        try:
            if self.producto:
                # ========== OBTENER STOCK ANTERIOR ==========
                stock_anterior = self.producto.stock_actual
                diferencia_stock = stock_nuevo - stock_anterior
                
                # ========== DEBUG ==========
                print("\n" + "=" * 50)
                print("🔍 FORMULARIO PRODUCTO - EDITAR")
                print(f"   Producto: {producto.nombre}")
                print(f"   Stock anterior: {stock_anterior}")
                print(f"   Stock nuevo: {stock_nuevo}")
                print(f"   Diferencia: {diferencia_stock}")
                # ===========================
                
                # Actualizar producto en BD
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE productos SET 
                        codigo=%s, nombre=%s, descripcion=%s, id_categoria=%s, id_proveedor=%s,
                        precio_compra=%s, precio_venta=%s, stock_actual=%s, stock_minimo=%s,
                        ubicacion=%s, unidad_medida=%s
                    WHERE id_producto=%s
                """, (producto.codigo, producto.nombre, producto.descripcion,
                    producto.id_categoria, producto.id_proveedor, producto.precio_compra,
                    producto.precio_venta, producto.stock_actual, producto.stock_minimo,
                    producto.ubicacion, producto.unidad_medida, self.producto.id_producto))
                
                # ========== REGISTRAR MOVIMIENTO SI HUBO CAMBIO DE STOCK ==========
                if diferencia_stock != 0:
                    if diferencia_stock > 0:
                        tipo_mov = 3  # Ajuste Positivo (ENTRADA)
                        cantidad_ajuste = diferencia_stock
                        tipo_texto = "ENTRADA"
                    else:
                        tipo_mov = 4  # Ajuste Negativo (SALIDA)
                        cantidad_ajuste = diferencia_stock  # Ya es negativo
                        tipo_texto = "SALIDA"
                    
                    print(f"   Registrando movimiento: {tipo_texto} - Cantidad: {cantidad_ajuste}")
                    
                    cursor.execute("""
                        INSERT INTO movimientos_stock (id_producto, id_tipo_movimiento, cantidad, 
                                                    stock_antes, stock_despues, referencia_tipo, 
                                                    referencia_id, usuario, fecha)
                        VALUES (%s, %s, %s, %s, %s, 'edicion_producto', %s, %s, NOW())
                    """, (self.producto.id_producto, tipo_mov, cantidad_ajuste, 
                        stock_anterior, stock_nuevo, self.producto.id_producto, 
                        self.usuario.get('nombre_usuario', 'admin') if isinstance(self.usuario, dict) else str(self.usuario)))
                
                conn.commit()
                conn.close()
                
                Alertas.mostrar_mensaje_exito("Producto actualizado correctamente")
            else:
                StockController.crear_producto(producto)
                Alertas.mostrar_mensaje_exito("Producto creado correctamente")
            
            Eventos.notificar(EVENTO_PRODUCTO_AGREGADO)
            Eventos.notificar(EVENTO_STOCK_ACTUALIZADO)
            
            if self.callback_refresh:
                self.callback_refresh()
            
            self.window.destroy()
            
        except Exception as e:
            Alertas.mostrar_mensaje_error(f"Error al guardar: {str(e)}")
            import traceback
            traceback.print_exc()
            from controllers import StockController
            
            if not self.entries['codigo'].get().strip():
                Alertas.mostrar_mensaje_advertencia("El codigo es obligatorio")
                return
            
            if not self.entries['nombre'].get().strip():
                Alertas.mostrar_mensaje_advertencia("El nombre es obligatorio")
                return
            
            try:
                precio_compra = float(self.entries['precio_compra'].get() or 0)
                precio_venta = float(self.entries['precio_venta'].get() or 0)
                stock_actual = int(self.entries['stock_actual'].get() or 0)
                stock_minimo = int(self.entries['stock_minimo'].get() or 5)
            except ValueError:
                Alertas.mostrar_mensaje_advertencia("Los valores numericos no son validos")
                return
            
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
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE productos SET 
                            codigo=%s, nombre=%s, descripcion=%s, id_categoria=%s, id_proveedor=%s,
                            precio_compra=%s, precio_venta=%s, stock_actual=%s, stock_minimo=%s,
                            ubicacion=%s, unidad_medida=%s
                        WHERE id_producto=%s
                    """, (producto.codigo, producto.nombre, producto.descripcion,
                        producto.id_categoria, producto.id_proveedor, producto.precio_compra,
                        producto.precio_venta, producto.stock_actual, producto.stock_minimo,
                        producto.ubicacion, producto.unidad_medida, self.producto.id_producto))
                    conn.commit()
                    conn.close()
                    Alertas.mostrar_mensaje_exito("Producto actualizado correctamente")
                else:
                    StockController.crear_producto(producto)
                    Alertas.mostrar_mensaje_exito("Producto creado correctamente")
                
                Eventos.notificar(EVENTO_PRODUCTO_AGREGADO)
                Eventos.notificar(EVENTO_STOCK_ACTUALIZADO)
                
                if self.callback_refresh:
                    self.callback_refresh()
                
                self.window.destroy()
                
            except Exception as e:
                Alertas.mostrar_mensaje_error(f"Error al guardar: {str(e)}")