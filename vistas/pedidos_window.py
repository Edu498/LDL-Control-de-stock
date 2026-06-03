# vistas/pedidos_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers import StockController, PedidoController
from utils import Alertas, formatear_precio, formatear_fecha
from utils.eventos import Eventos, EVENTO_PEDIDO_CREADO, EVENTO_STOCK_ACTUALIZADO

class PedidosWindow:
    def __init__(self, parent, usuario):
        self.parent = parent
        self.usuario = usuario
        
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Pedidos a Proveedores")
        self.window.geometry("1100x600")
        self.window.configure(bg='#F0F0F0')
        
        self.cargar_datos()
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
    
    def cargar_datos(self):
        self.productos_bajo_stock = StockController.get_productos_con_alerta()
        self.pedidos = PedidoController.get_pedidos_pendientes()
        self.proveedores = StockController.get_proveedores()
        self.historial_pedidos = PedidoController.get_historial_pedidos()
    
    def crear_widgets(self):
        # Título
        tk.Label(self.window, text="📦 GESTIÓN DE PEDIDOS", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Frame de botones superior
        frame_botones = tk.Frame(self.window, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame_botones, text="⚡ Generar Pedido Automático", 
                 command=self.generar_pedido_automatico,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold"),
                 padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="➕ Nuevo Pedido Manual", 
                 command=self.nuevo_pedido,
                 bg='#007BFF', fg='white', font=("Arial", 10, "bold"),
                 padx=20).pack(side=tk.LEFT, padx=5)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña: Productos con stock bajo
        self.frame_stock_bajo = tk.Frame(self.notebook, bg='#F0F0F0')
        self.notebook.add(self.frame_stock_bajo, text="⚠️ Stock Bajo")
        self.crear_tabla_stock_bajo()
        
        # Pestaña: Pedidos pendientes
        self.frame_pedidos = tk.Frame(self.notebook, bg='#F0F0F0')
        self.notebook.add(self.frame_pedidos, text="📋 Pedidos Pendientes")
        self.crear_tabla_pedidos()
        
        # Pestaña: Historial de pedidos
        self.frame_historial = tk.Frame(self.notebook, bg='#F0F0F0')
        self.notebook.add(self.frame_historial, text="📜 Historial")
        self.crear_tabla_historial()
    
    def crear_tabla_stock_bajo(self):
        # Frame para la tabla
        frame_tabla = tk.Frame(self.frame_stock_bajo)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Código', 'Producto', 'Stock', 'Mínimo', 'Faltante', 'Proveedor')
        self.tabla_stock_bajo = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                               yscrollcommand=scrollbar.set, height=15)
        
        for col in columnas:
            self.tabla_stock_bajo.heading(col, text=col)
            ancho = 200 if col == 'Producto' else 100
            self.tabla_stock_bajo.column(col, width=ancho)
        
        scrollbar.config(command=self.tabla_stock_bajo.yview)
        self.tabla_stock_bajo.pack(fill=tk.BOTH, expand=True)
        
        # Botón para generar pedido desde selección
        frame_botones = tk.Frame(self.frame_stock_bajo, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame_botones, text="📦 Generar Pedido para Seleccionados", 
                 command=self.generar_pedido_seleccionados,
                 bg='#28A745', fg='white', padx=20).pack()
        
        self.actualizar_tabla_stock_bajo()
    
    def actualizar_tabla_stock_bajo(self):
        for item in self.tabla_stock_bajo.get_children():
            self.tabla_stock_bajo.delete(item)
        
        for p in self.productos_bajo_stock:
            faltante = max(0, p.get('stock_minimo', 0) - p.get('stock_actual', 0))
            self.tabla_stock_bajo.insert('', tk.END, values=(
                p.get('codigo', '-'), 
                p.get('nombre', '-'), 
                p.get('stock_actual', 0),
                p.get('stock_minimo', 0), 
                faltante, 
                p.get('proveedor', 'Sin proveedor')
            ), tags=('seleccionable',))
        
        self.tabla_stock_bajo.tag_configure('seleccionable', background='#FFF3CD')
    
    def crear_tabla_pedidos(self):
        frame_tabla = tk.Frame(self.frame_pedidos)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('N° Pedido', 'Proveedor', 'Fecha', 'Total', 'Estado', 'Acciones')
        self.tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                           yscrollcommand=scrollbar.set, height=15)
        
        for col in columnas:
            self.tabla_pedidos.heading(col, text=col)
            ancho = 150 if col in ('Proveedor', 'Acciones') else 100
            self.tabla_pedidos.column(col, width=ancho)
        
        scrollbar.config(command=self.tabla_pedidos.yview)
        self.tabla_pedidos.pack(fill=tk.BOTH, expand=True)
        
        # Vincular evento de clic
        self.tabla_pedidos.bind('<ButtonRelease-1>', self.on_click_tabla_pedidos)
        
        self.actualizar_tabla_pedidos()
    
    def actualizar_tabla_pedidos(self):
        for item in self.tabla_pedidos.get_children():
            self.tabla_pedidos.delete(item)
        
        for p in self.pedidos:
            self.tabla_pedidos.insert('', tk.END, iid=p.get('id_pedido'), values=(
                p.get('numero_pedido', 'N/A'),
                p.get('proveedor_nombre', '-'),
                formatear_fecha(p.get('fecha_pedido', '')),
                f"${p.get('total', 0):,.2f}",
                'Pendiente' if p.get('id_estado') == 1 else 'Enviado',
                '📦 Recibir'
            ))
            
    def on_click_tabla_pedidos(self, event):
        region = self.tabla_pedidos.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tabla_pedidos.identify_column(event.x)
            if column == '#6':  # Columna Acciones
                id_pedido = self.tabla_pedidos.identify_row(event.y)
                if id_pedido:
                    pedido = next((p for p in self.pedidos if str(p.get('id_pedido')) == str(id_pedido)), None)
                    if pedido:
                        self.recibir_pedido(pedido)
                        
    def recibir_pedido(self, pedido):
        RecepcionPedidoWindow(self.window, pedido, self.refrescar_datos_locales, self.usuario)
        
    def refrescar_datos_locales(self):
        self.cargar_datos()
        self.actualizar_tabla_pedidos()
        self.actualizar_tabla_stock_bajo()
        self.actualizar_tabla_historial()
    
    def crear_tabla_historial(self):
        frame_tabla = tk.Frame(self.frame_historial)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('N° Pedido', 'Proveedor', 'Fecha', 'Fecha Entrega', 'Total', 'Estado')
        self.tabla_historial = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                              yscrollcommand=scrollbar.set, height=15)
        
        for col in columnas:
            self.tabla_historial.heading(col, text=col)
            self.tabla_historial.column(col, width=120)
        
        scrollbar.config(command=self.tabla_historial.yview)
        self.tabla_historial.pack(fill=tk.BOTH, expand=True)
        
        self.actualizar_tabla_historial()
        
    def actualizar_tabla_historial(self):
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)
            
        for p in self.historial_pedidos:
            fecha_entrega_raw = p.get('fecha_entrega_real')
            fecha_entrega = formatear_fecha(fecha_entrega_raw) if fecha_entrega_raw else 'Pendiente'
            
            self.tabla_historial.insert('', tk.END, values=(
                p.get('numero_pedido', 'N/A'),
                p.get('proveedor_nombre', '-'),
                formatear_fecha(p.get('fecha_pedido', '')),
                fecha_entrega,
                f"${p.get('total', 0):,.2f}",
                p.get('estado_nombre', '-')
            ))
    
    def generar_pedido_automatico(self):
        productos_a_pedir = []
        productos_sin_proveedor = []
        for p in self.productos_bajo_stock:
            if p.get('proveedor') and p.get('proveedor') != 'Sin proveedor':
                productos_a_pedir.append(p)
            else:
                productos_sin_proveedor.append(p.get('nombre'))
                
        if not productos_a_pedir:
            Alertas.mostrar_mensaje_advertencia(
                "No hay productos con stock bajo que tengan un proveedor asignado.",
                parent=self.window
            )
            return
            
        PropuestaPedidoWindow(self.window, productos_a_pedir, self.refrescar_datos_locales, self.usuario)
    
    def generar_pedido_seleccionados(self):
        seleccion = self.tabla_stock_bajo.selection()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione al menos un producto", parent=self.window)
            return
        
        # Obtener los códigos de los productos seleccionados
        codigos_seleccionados = []
        for item in seleccion:
            valores = self.tabla_stock_bajo.item(item, 'values')
            if valores:
                codigos_seleccionados.append(valores[0])
                
        # Encontrar los ids de productos correspondientes
        productos_a_pedir = []
        productos_sin_proveedor = []
        for p in self.productos_bajo_stock:
            if p.get('codigo') in codigos_seleccionados:
                if p.get('proveedor') and p.get('proveedor') != 'Sin proveedor':
                    productos_a_pedir.append(p)
                else:
                    productos_sin_proveedor.append(p.get('nombre'))
                    
        if productos_sin_proveedor:
            nombres_sin_prov = ", ".join(productos_sin_proveedor)
            if not productos_a_pedir:
                Alertas.mostrar_mensaje_advertencia(
                    f"No se puede generar el pedido para los siguientes productos porque no tienen proveedor asignado:\n\n{nombres_sin_prov}",
                    parent=self.window
                )
                return
            else:
                if not Alertas.preguntar_si(
                    f"Los siguientes productos no tienen proveedor asignado y no serán incluidos:\n\n{nombres_sin_prov}\n\n¿Desea continuar con el resto de los productos seleccionados?",
                    parent=self.window
                ):
                    return
                    
        # Abrir la ventana de confirmación de cantidades
        PropuestaPedidoWindow(self.window, productos_a_pedir, self.refrescar_datos_locales, self.usuario)
    
    def nuevo_pedido(self):
        NuevoPedidoWindow(self.window, self.usuario, self.refrescar_datos_locales)


class NuevoPedidoWindow:
    def __init__(self, parent, usuario, callback_refresh):
        self.parent = parent
        self.usuario = usuario
        self.callback_refresh = callback_refresh
        self.productos_seleccionados = []
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Pedido a Proveedor")
        self.window.geometry("900x600")
        self.window.configure(bg='#F0F0F0')
        
        self.cargar_datos()
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
    
    def cargar_datos(self):
        self.proveedores = StockController.get_proveedores()
        self.productos = StockController.get_all_productos()
    
    def crear_widgets(self):
        # Título
        tk.Label(self.window, text="📝 NUEVO PEDIDO", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        # Frame de datos del pedido
        frame_datos = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame_datos.pack(fill=tk.X, padx=10, pady=10)
        
        # Proveedor
        tk.Label(frame_datos, text="Proveedor:", bg='white', font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.combo_proveedor = ttk.Combobox(frame_datos, values=[p.nombre for p in self.proveedores], width=40)
        self.combo_proveedor.grid(row=0, column=1, padx=10, pady=10)
        
        # Fecha esperada
        tk.Label(frame_datos, text="Fecha entrega esperada:", bg='white').grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        self.entry_fecha = tk.Entry(frame_datos, width=15)
        self.entry_fecha.grid(row=0, column=3, padx=10, pady=10)
        self.entry_fecha.insert(0, "DD/MM/AAAA")
        
        # Observaciones
        tk.Label(frame_datos, text="Observaciones:", bg='white').grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.entry_obs = tk.Entry(frame_datos, width=70)
        self.entry_obs.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky=tk.W)
        
        # Frame para agregar productos
        frame_agregar = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame_agregar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_agregar, text="Agregar Producto:", bg='white', font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        frame_producto = tk.Frame(frame_agregar, bg='white')
        frame_producto.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_producto, text="Producto:", bg='white').pack(side=tk.LEFT, padx=5)
        self.combo_producto = ttk.Combobox(frame_producto, values=[f"{p.codigo} - {p.nombre}" for p in self.productos], width=40)
        self.combo_producto.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_producto, text="Cantidad:", bg='white').pack(side=tk.LEFT, padx=5)
        self.entry_cantidad = tk.Entry(frame_producto, width=10)
        self.entry_cantidad.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad.insert(0, "1")
        
        tk.Button(frame_producto, text="➕ Agregar", command=self.agregar_producto,
                 bg='#28A745', fg='white').pack(side=tk.LEFT, padx=10)
        
        # Tabla de productos del pedido
        tk.Label(self.window, text="Productos del Pedido:", 
                font=("Arial", 10, "bold"), bg='#F0F0F0').pack(anchor=tk.W, padx=10)
        
        frame_tabla = tk.Frame(self.window)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Producto', 'Cantidad', 'Precio Compra', 'Subtotal', 'Acción')
        self.tabla_productos = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                             yscrollcommand=scrollbar.set, height=10)
        
        self.tabla_productos.heading('Producto', text='Producto')
        self.tabla_productos.heading('Cantidad', text='Cantidad')
        self.tabla_productos.heading('Precio Compra', text='Precio Compra')
        self.tabla_productos.heading('Subtotal', text='Subtotal')
        self.tabla_productos.heading('Acción', text='Acción')
        
        self.tabla_productos.column('Producto', width=300)
        self.tabla_productos.column('Cantidad', width=80)
        self.tabla_productos.column('Precio Compra', width=100)
        self.tabla_productos.column('Subtotal', width=100)
        self.tabla_productos.column('Acción', width=80)
        
        scrollbar.config(command=self.tabla_productos.yview)
        self.tabla_productos.pack(fill=tk.BOTH, expand=True)
        
        # Botones finales
        frame_botones = tk.Frame(self.window, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(frame_botones, text="💾 Guardar Pedido", command=self.guardar_pedido,
                 bg='#28A745', fg='white', font=("Arial", 12, "bold"), padx=30).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(frame_botones, text="Cancelar", command=self.window.destroy,
                 bg='#6C757D', fg='white', padx=20).pack(side=tk.RIGHT, padx=5)
    
    def agregar_producto(self):
        seleccion = self.combo_producto.get()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione un producto")
            return
        
        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except:
            Alertas.mostrar_mensaje_advertencia("Ingrese una cantidad válida")
            return
        
        # Buscar producto
        codigo = seleccion.split(' - ')[0]
        producto = next((p for p in self.productos if p.codigo == codigo), None)
        
        if not producto:
            return
        
        # Verificar si ya está agregado
        for i, prod in enumerate(self.productos_seleccionados):
            if prod['id_producto'] == producto.id_producto:
                self.productos_seleccionados[i]['cantidad'] += cantidad
                self.productos_seleccionados[i]['subtotal'] = self.productos_seleccionados[i]['cantidad'] * producto.precio_compra
                break
        else:
            self.productos_seleccionados.append({
                'id_producto': producto.id_producto,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio_compra': producto.precio_compra,
                'subtotal': cantidad * producto.precio_compra
            })
        
        self.actualizar_tabla()
        self.combo_producto.set('')
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "1")
    
    def actualizar_tabla(self):
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        for i, prod in enumerate(self.productos_seleccionados):
            self.tabla_productos.insert('', tk.END, values=(
                f"{prod['codigo']} - {prod['nombre'][:40]}",
                prod['cantidad'],
                f"${prod['precio_compra']:,.2f}",
                f"${prod['subtotal']:,.2f}",
                "🗑️ Eliminar"
            ), tags=(i,))
        
        # Vincular evento de clic para eliminar
        self.tabla_productos.bind('<ButtonRelease-1>', self.on_click_tabla)
    
    def on_click_tabla(self, event):
        region = self.tabla_productos.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tabla_productos.identify_column(event.x)
            if column == '#5':  # Columna Acción
                item = self.tabla_productos.identify_row(event.y)
                if item:
                    valores = self.tabla_productos.item(item, 'values')
                    codigo = valores[0].split(' - ')[0]
                    
                    for i, prod in enumerate(self.productos_seleccionados):
                        if prod['codigo'] == codigo:
                            del self.productos_seleccionados[i]
                            break
                    
                    self.actualizar_tabla()
    
    def guardar_pedido(self):
        if not self.combo_proveedor.get():
            Alertas.mostrar_mensaje_advertencia("Seleccione un proveedor")
            return
        
        if not self.productos_seleccionados:
            Alertas.mostrar_mensaje_advertencia("Agregue al menos un producto")
            return
        
        try:
            # Crear pedido en la base de datos
            conexion = None
            try:
                from utils.database import get_connection
                conexion = get_connection()
                cursor = conexion.cursor()
                
                # Obtener ID del proveedor
                proveedor_nombre = self.combo_proveedor.get()
                proveedor_id = None
                for p in self.proveedores:
                    if p.nombre == proveedor_nombre:
                        proveedor_id = p.id_proveedor
                        break
                
                if not proveedor_id:
                    Alertas.mostrar_mensaje_error("Proveedor no encontrado")
                    return
                
                # Generar número de pedido
                from datetime import datetime
                numero_pedido = f"MAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Insertar pedido
                cursor.execute("""
                    INSERT INTO pedidos (numero_pedido, id_proveedor, fecha_pedido, id_estado, observaciones)
                    VALUES (%s, %s, NOW(), 1, %s)
                """, (numero_pedido, proveedor_id, self.entry_obs.get()))
                
                id_pedido = cursor.lastrowid
                
                # Insertar detalles
                subtotal_total = 0
                for prod in self.productos_seleccionados:
                    subtotal = prod['cantidad'] * prod['precio_compra']
                    subtotal_total += subtotal
                    cursor.execute("""
                        INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_pedido, prod['id_producto'], prod['cantidad'], prod['precio_compra'], subtotal))
                
                # Actualizar totales
                iva = subtotal_total * 0.21
                total = subtotal_total + iva
                cursor.execute("""
                    UPDATE pedidos SET subtotal = %s, iva = %s, total = %s WHERE id_pedido = %s
                """, (subtotal_total, iva, total, id_pedido))
                
                conexion.commit()
                Alertas.mostrar_mensaje_exito(f" Pedido {numero_pedido} creado exitosamente!")
                
                # Notificar evento
                Eventos.notificar(EVENTO_PEDIDO_CREADO)
                
                # Actualizar listas
                if self.callback_refresh:
                    self.callback_refresh()
                
                self.window.destroy()
                
            except Exception as e:
                if conexion:
                    conexion.rollback()
                Alertas.mostrar_mensaje_error(f"Error al guardar pedido: {str(e)}")
            finally:
                if conexion:
                    conexion.close()
                    
        except Exception as e:
            Alertas.mostrar_mensaje_error(f"Error: {str(e)}")


class RecepcionPedidoWindow:
    def __init__(self, parent, pedido, callback_refresh, usuario):
        self.parent = parent
        self.pedido = pedido
        self.callback_refresh = callback_refresh
        self.usuario = usuario
        self.entries = {}
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"📦 Recepción de Pedido - N° {pedido.get('numero_pedido')}")
        self.window.geometry("600x500")
        self.window.configure(bg='#F0F0F0')
        
        self.cargar_datos()
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        
    def cargar_datos(self):
        self.detalles = PedidoController.get_detalles_pedido(self.pedido.get('id_pedido'))
        
    def crear_widgets(self):
        # Título
        tk.Label(self.window, text="📦 REGISTRAR INGRESO DE STOCK", 
                 font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
                 
        # Resumen del pedido
        frame_resumen = tk.Frame(self.window, bg='white', relief=tk.RAISED, bd=1)
        frame_resumen.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(frame_resumen, text=f"Pedido: {self.pedido.get('numero_pedido')}", bg='white', font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Label(frame_resumen, text=f"Proveedor: {self.pedido.get('proveedor_nombre')}", bg='white').grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Scrollable area for products
        frame_productos = tk.Frame(self.window, bg='#F0F0F0')
        frame_productos.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Canvas + Scrollbar
        canvas = tk.Canvas(frame_productos, bg='#F0F0F0', highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_productos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F0F0F0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers in scrollable frame
        frame_headers = tk.Frame(scrollable_frame, bg='#E0E0E0', height=25)
        frame_headers.pack(fill=tk.X, pady=5)
        tk.Label(frame_headers, text="Producto", bg='#E0E0E0', font=("Arial", 9, "bold"), width=35, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        tk.Label(frame_headers, text="Cant. Pedida", bg='#E0E0E0', font=("Arial", 9, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Label(frame_headers, text="Cant. Recibida", bg='#E0E0E0', font=("Arial", 9, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        
        # Rows
        for item in self.detalles:
            id_prod = item.get('id_producto')
            nombre = item.get('producto_nombre', '')
            codigo = item.get('codigo', '')
            cantidad_pedida = item.get('cantidad', 0)
            
            row = tk.Frame(scrollable_frame, bg='white', relief=tk.GROOVE, bd=1)
            row.pack(fill=tk.X, pady=2)
            
            # Nombre prod
            tk.Label(row, text=f"{codigo} - {nombre[:35]}", bg='white', anchor=tk.W, width=35).pack(side=tk.LEFT, padx=5, pady=5)
            # Cantidad pedida
            tk.Label(row, text=str(cantidad_pedida), bg='white', width=12).pack(side=tk.LEFT, padx=5, pady=5)
            
            # Entry for cantidad recibida
            entry_var = tk.StringVar(value=str(cantidad_pedida))
            entry = tk.Entry(row, textvariable=entry_var, width=10, justify=tk.CENTER)
            entry.pack(side=tk.LEFT, padx=15, pady=5)
            
            self.entries[id_prod] = entry
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones
        frame_botones = tk.Frame(self.window, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(frame_botones, text="💾 Confirmar Recepción", command=self.confirmar_recepcion,
                  bg='#28A745', fg='white', font=("Arial", 11, "bold"), padx=20).pack(side=tk.RIGHT, padx=5)
                  
        tk.Button(frame_botones, text="Cancelar", command=self.window.destroy,
                  bg='#6C757D', fg='white', padx=15).pack(side=tk.RIGHT, padx=5)
                  
    def confirmar_recepcion(self):
        cantidades_recibidas = {}
        for id_prod, entry in self.entries.items():
            val = entry.get().strip()
            try:
                cant = int(val)
                if cant < 0:
                    raise ValueError
                cantidades_recibidas[id_prod] = cant
            except ValueError:
                # Find product name
                prod_name = next((p.get('producto_nombre') for p in self.detalles if p.get('id_producto') == id_prod), "Producto")
                Alertas.mostrar_mensaje_advertencia(f"Por favor ingrese una cantidad válida (número entero >= 0) para:\n{prod_name}", parent=self.window)
                return
                
        # Confirm confirmation dialog
        if Alertas.preguntar_si("¿Desea registrar la recepción del pedido con las cantidades indicadas?\n\nEl stock de los productos aumentará en base a las cantidades ingresadas.", parent=self.window):
            try:
                # Obtener usuario de manera segura
                usuario_str = "admin"
                if self.usuario:
                    if isinstance(self.usuario, dict):
                        usuario_str = self.usuario.get('nombre_usuario', 'admin')
                    elif hasattr(self.usuario, 'nombre_usuario'):
                        usuario_str = self.usuario.nombre_usuario
                    else:
                        usuario_str = str(self.usuario)
                        
                exito = PedidoController.recibir_pedido(self.pedido.get('id_pedido'), usuario_str, cantidades_recibidas)
                if exito:
                    Alertas.mostrar_mensaje_exito(f"✅ Pedido N° {self.pedido.get('numero_pedido')} recibido y stock actualizado", parent=self.parent)
                    # Notificar eventos
                    from utils.eventos import Eventos, EVENTO_PEDIDO_CREADO, EVENTO_STOCK_ACTUALIZADO
                    Eventos.notificar(EVENTO_PEDIDO_CREADO)
                    Eventos.notificar(EVENTO_STOCK_ACTUALIZADO)
                    
                    if self.callback_refresh:
                        self.callback_refresh()
                        
                    self.window.destroy()
                else:
                    Alertas.mostrar_mensaje_error("No se pudo registrar la recepción del pedido", parent=self.window)
            except Exception as e:
                Alertas.mostrar_mensaje_error(f"Error al registrar recepción: {str(e)}", parent=self.window)


class PropuestaPedidoWindow:
    def __init__(self, parent, productos, callback_refresh, usuario):
        self.parent = parent
        self.productos = productos
        self.callback_refresh = callback_refresh
        self.usuario = usuario
        self.entries = {}
        
        self.window = tk.Toplevel(parent)
        self.window.title("📝 Confirmar Cantidades del Pedido")
        self.window.geometry("700x500")
        self.window.configure(bg='#F0F0F0')
        
        self.crear_widgets()
        
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()
        
    def crear_widgets(self):
        # Título
        tk.Label(self.window, text="📝 REVISAR CANTIDADES A PEDIR", 
                 font=("Arial", 14, "bold"), bg='#F0F0F0').pack(pady=10)
                 
        # Instrucciones
        tk.Label(self.window, text="Indique las cantidades a solicitar a los proveedores.\n"
                                   "Los productos se agruparán automáticamente por proveedor en distintos pedidos.", 
                 font=("Arial", 9), bg='#F0F0F0', justify=tk.LEFT).pack(anchor=tk.W, padx=15, pady=5)
                 
        # Scrollable area for products
        frame_productos = tk.Frame(self.window, bg='#F0F0F0')
        frame_productos.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        canvas = tk.Canvas(frame_productos, bg='#F0F0F0', highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_productos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F0F0F0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        frame_headers = tk.Frame(scrollable_frame, bg='#E0E0E0', height=25)
        frame_headers.pack(fill=tk.X, pady=5)
        tk.Label(frame_headers, text="Producto", bg='#E0E0E0', font=("Arial", 9, "bold"), width=30, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        tk.Label(frame_headers, text="Proveedor", bg='#E0E0E0', font=("Arial", 9, "bold"), width=20, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        tk.Label(frame_headers, text="Stock / Min", bg='#E0E0E0', font=("Arial", 9, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(frame_headers, text="Cantidad a Pedir", bg='#E0E0E0', font=("Arial", 9, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        
        # Rows
        for item in self.productos:
            id_prod = item.get('id_producto')
            nombre = item.get('nombre', '')
            codigo = item.get('codigo', '')
            proveedor = item.get('proveedor', 'Sin Proveedor')
            stock_actual = item.get('stock_actual', 0)
            stock_minimo = item.get('stock_minimo', 0)
            
            # Cantidad sugerida por defecto: max(5, stock_minimo - stock_actual)
            cantidad_sugerida = max(5, stock_minimo - stock_actual)
            
            row = tk.Frame(scrollable_frame, bg='white', relief=tk.GROOVE, bd=1)
            row.pack(fill=tk.X, pady=2)
            
            # Nombre prod
            tk.Label(row, text=f"{codigo} - {nombre[:28]}", bg='white', anchor=tk.W, width=30).pack(side=tk.LEFT, padx=5, pady=5)
            # Proveedor
            tk.Label(row, text=proveedor[:18], bg='white', anchor=tk.W, width=20).pack(side=tk.LEFT, padx=5, pady=5)
            # Stock / Min
            tk.Label(row, text=f"{stock_actual} / {stock_minimo}", bg='white', width=10).pack(side=tk.LEFT, padx=5, pady=5)
            
            # Entry variable for order quantity
            entry_var = tk.StringVar(value=str(cantidad_sugerida))
            entry = tk.Entry(row, textvariable=entry_var, width=10, justify=tk.CENTER)
            entry.pack(side=tk.LEFT, padx=15, pady=5)
            
            self.entries[id_prod] = entry
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones
        frame_botones = tk.Frame(self.window, bg='#F0F0F0')
        frame_botones.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(frame_botones, text="💾 Generar Pedidos", command=self.generar_pedidos,
                  bg='#28A745', fg='white', font=("Arial", 11, "bold"), padx=20).pack(side=tk.RIGHT, padx=5)
                  
        tk.Button(frame_botones, text="Cancelar", command=self.window.destroy,
                  bg='#6C757D', fg='white', padx=15).pack(side=tk.RIGHT, padx=5)
                  
    def generar_pedidos(self):
        cantidades_pedir = {}
        for id_prod, entry in self.entries.items():
            val = entry.get().strip()
            try:
                cant = int(val)
                if cant < 0:
                    raise ValueError
                if cant > 0:
                    cantidades_pedir[id_prod] = cant
            except ValueError:
                # Find product name
                prod_name = next((p.get('nombre') for p in self.productos if p.get('id_producto') == id_prod), "Producto")
                Alertas.mostrar_mensaje_advertencia(f"Por favor ingrese una cantidad de pedido válida (número entero >= 0) para:\n{prod_name}", parent=self.window)
                return
                
        if not cantidades_pedir:
            Alertas.mostrar_mensaje_advertencia("Debe especificar una cantidad mayor a 0 para al menos un producto.", parent=self.window)
            return
            
        # Confirm confirmation dialog
        if Alertas.preguntar_si("¿Desea generar los pedidos a proveedores con las cantidades ingresadas?\n\nLos productos se agruparán por proveedor.", parent=self.window):
            try:
                ids_a_pedir = list(cantidades_pedir.keys())
                pedidos = PedidoController.generar_pedido_seleccionados(ids_a_pedir, cantidades_pedir)
                if pedidos and len(pedidos) > 0:
                    Alertas.mostrar_mensaje_exito(f"✅ Se han generado {len(pedidos)} pedidos con éxito", parent=self.parent)
                    # Notificar evento
                    from utils.eventos import Eventos, EVENTO_PEDIDO_CREADO
                    Eventos.notificar(EVENTO_PEDIDO_CREADO)
                    
                    if self.callback_refresh:
                        self.callback_refresh()
                        
                    self.window.destroy()
                else:
                    Alertas.mostrar_mensaje_error("No se pudieron generar los pedidos. Verifique que los productos seleccionados tengan un proveedor asignado.", parent=self.window)
            except Exception as e:
                Alertas.mostrar_mensaje_error(f"Error al generar pedidos: {str(e)}", parent=self.window)