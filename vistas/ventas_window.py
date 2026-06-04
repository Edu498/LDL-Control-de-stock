# vistas/ventas_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from controllers import StockController, VentaController
from utils import Alertas, formatear_precio, generar_numero_factura
from utils.eventos import Eventos, EVENTO_VENTA_REGISTRADA, EVENTO_STOCK_ACTUALIZADO

class VentasWindow:
    def __init__(self, parent, usuario, main_app=None):
        self.parent = parent
        self.usuario = usuario
        self.main_app = main_app
        self.carrito = []
        self.total = 0.0
        
        if main_app:
            self.window = tk.Frame(parent, bg='#F0F0F0')
            self.window.pack(fill=tk.BOTH, expand=True)
        else:
            self.window = tk.Toplevel(parent)
            self.window.title("Registro de Ventas")
            self.window.geometry("1200x700")
            self.window.configure(bg='#F0F0F0')
            self.window.transient(parent.winfo_toplevel())
            self.window.grab_set()
            self.window.focus_force()
        
        self.cargar_datos()
        self.crear_widgets()
    
    def cargar_datos(self):
        self.productos = StockController.get_all_productos()
        self.productos_dict = {p.codigo: p for p in self.productos}
    
    def crear_widgets(self):
        tk.Label(self.window, text="📝 REGISTRO DE VENTAS", 
                font=("Arial", 16, "bold"), bg='#F0F0F0').pack(pady=10)
        
        frame_principal = tk.Frame(self.window, bg='#F0F0F0')
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        frame_izquierdo = tk.Frame(frame_principal, bg='white', relief=tk.RAISED, bd=1)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        frame_derecho = tk.Frame(frame_principal, bg='white', relief=tk.RAISED, bd=1)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Panel izquierdo
        tk.Label(frame_izquierdo, text="🔍 Buscar Producto:", 
                font=("Arial", 12, "bold"), bg='white').pack(pady=5)
        
        frame_busqueda = tk.Frame(frame_izquierdo, bg='white')
        frame_busqueda.pack(fill=tk.X, padx=10, pady=5)
        
        self.entry_busqueda = tk.Entry(frame_busqueda, font=("Arial", 12), width=30)
        self.entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_productos)
        
        tk.Button(frame_busqueda, text="Buscar", command=self.buscar_productos,
                 bg='#007BFF', fg='white').pack(side=tk.LEFT)
        
        frame_tabla = tk.Frame(frame_izquierdo)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Código', 'Producto', 'Stock', 'Precio')
        self.tabla_productos = ttk.Treeview(frame_tabla, columns=columnas, show='headings',
                                             yscrollcommand=scrollbar.set, height=15)
        
        for col in columnas:
            self.tabla_productos.heading(col, text=col)
            ancho = 150 if col == 'Producto' else 100
            self.tabla_productos.column(col, width=ancho)
        
        scrollbar.config(command=self.tabla_productos.yview)
        self.tabla_productos.pack(fill=tk.BOTH, expand=True)
        
        frame_cantidad = tk.Frame(frame_izquierdo, bg='white')
        frame_cantidad.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_cantidad, text="Cantidad:", bg='white', 
                font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.spin_cantidad = tk.Spinbox(frame_cantidad, from_=1, to=999, width=10, font=("Arial", 10))
        self.spin_cantidad.pack(side=tk.LEFT, padx=5)
        self.spin_cantidad.delete(0, tk.END)
        self.spin_cantidad.insert(0, "1")
        
        tk.Button(frame_cantidad, text="➕ Agregar al Carrito", command=self.agregar_al_carrito,
                 bg='#28A745', fg='white', font=("Arial", 10, "bold"), padx=20).pack(side=tk.RIGHT)
        
        # Panel derecho
        tk.Label(frame_derecho, text="👤 Datos del Cliente:", 
                font=("Arial", 12, "bold"), bg='white').pack(pady=5)
        
        frame_cliente = tk.Frame(frame_derecho, bg='white')
        frame_cliente.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_cliente, text="Nombre:", bg='white').pack(side=tk.LEFT)
        self.entry_cliente = tk.Entry(frame_cliente, width=30)
        self.entry_cliente.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_cliente.insert(0, "CONSUMIDOR FINAL")
        
        tk.Label(frame_derecho, text="🛒 Carrito de Compras:", 
                font=("Arial", 12, "bold"), bg='white').pack(pady=5)
        
        frame_carrito = tk.Frame(frame_derecho)
        frame_carrito.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar_carrito = tk.Scrollbar(frame_carrito)
        scrollbar_carrito.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas_carrito = ('Código', 'Producto', 'Cant.', 'Precio', 'Subtotal')
        self.tabla_carrito = ttk.Treeview(frame_carrito, columns=columnas_carrito, show='headings',
                                           yscrollcommand=scrollbar_carrito.set, height=10)
        
        for col in columnas_carrito:
            self.tabla_carrito.heading(col, text=col)
            ancho = 120 if col == 'Producto' else 80
            self.tabla_carrito.column(col, width=ancho)
        
        scrollbar_carrito.config(command=self.tabla_carrito.yview)
        self.tabla_carrito.pack(fill=tk.BOTH, expand=True)
        
        frame_totales = tk.Frame(frame_derecho, bg='white')
        frame_totales.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_totales, text="Subtotal:", bg='white', 
                font=("Arial", 10)).pack(anchor=tk.E)
        self.lbl_subtotal = tk.Label(frame_totales, text="$0.00", bg='white', 
                                      font=("Arial", 10, "bold"))
        self.lbl_subtotal.pack(anchor=tk.E)
        
        tk.Label(frame_totales, text="IVA (21%):", bg='white', 
                font=("Arial", 10)).pack(anchor=tk.E)
        self.lbl_iva = tk.Label(frame_totales, text="$0.00", bg='white', 
                                 font=("Arial", 10, "bold"))
        self.lbl_iva.pack(anchor=tk.E)
        
        tk.Label(frame_totales, text="TOTAL:", bg='white', 
                font=("Arial", 14, "bold")).pack(anchor=tk.E)
        self.lbl_total = tk.Label(frame_totales, text="$0.00", bg='white', 
                                   font=("Arial", 14, "bold"), fg='#28A745')
        self.lbl_total.pack(anchor=tk.E)
        
        frame_botones = tk.Frame(frame_derecho, bg='white')
        frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_del_carrito,
                 bg='#FFC107', fg='black', padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="🧹 Limpiar Carrito", command=self.limpiar_carrito,
                 bg='#6C757D', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
        if self.main_app:
            tk.Button(frame_botones, text="❌ Volver", command=self.main_app._mostrar_dashboard,
                     bg='#DC3545', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="💾 Registrar Venta", command=self.registrar_venta,
                 bg='#28A745', fg='white', font=("Arial", 12, "bold"), padx=30).pack(side=tk.RIGHT)
        
        self.actualizar_tabla_productos()
    
    def actualizar_tabla_productos(self):
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        for p in self.productos:
            if p.stock_actual > 0:
                self.tabla_productos.insert('', tk.END, values=(
                    p.codigo, p.nombre, p.stock_actual, f"${p.precio_venta:,.2f}"
                ))
    
    def buscar_productos(self, event=None):
        texto = self.entry_busqueda.get().lower()
        
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        for p in self.productos:
            if p.stock_actual > 0 and (texto in p.codigo.lower() or texto in p.nombre.lower()):
                self.tabla_productos.insert('', tk.END, values=(
                    p.codigo, p.nombre, p.stock_actual, f"${p.precio_venta:,.2f}"
                ))
    
    def agregar_al_carrito(self):
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione un producto")
            return
        
        item = self.tabla_productos.item(seleccion[0])
        codigo = item['values'][0]
        producto = self.productos_dict.get(codigo)
        
        if not producto:
            return
        
        try:
            cantidad = int(self.spin_cantidad.get())
        except:
            cantidad = 1
        
        if cantidad <= 0:
            Alertas.mostrar_mensaje_advertencia("La cantidad debe ser mayor a 0")
            return
        
        if cantidad > producto.stock_actual:
            Alertas.mostrar_mensaje_advertencia(f"Stock insuficiente. Solo hay {producto.stock_actual} unidades")
            return
        
        for i, item_carrito in enumerate(self.carrito):
            if item_carrito['id_producto'] == producto.id_producto:
                nueva_cantidad = item_carrito['cantidad'] + cantidad
                if nueva_cantidad > producto.stock_actual:
                    Alertas.mostrar_mensaje_advertencia(f"Stock insuficiente. Solo puede agregar {producto.stock_actual - item_carrito['cantidad']} más")
                    return
                self.carrito[i]['cantidad'] = nueva_cantidad
                self.carrito[i]['subtotal'] = nueva_cantidad * producto.precio_venta
                break
        else:
            self.carrito.append({
                'id_producto': producto.id_producto,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio': producto.precio_venta,
                'subtotal': cantidad * producto.precio_venta
            })
        
        self.actualizar_carrito()
        self.spin_cantidad.delete(0, tk.END)
        self.spin_cantidad.insert(0, "1")
    
    def actualizar_carrito(self):
        for item in self.tabla_carrito.get_children():
            self.tabla_carrito.delete(item)
        
        subtotal = 0
        for item in self.carrito:
            self.tabla_carrito.insert('', tk.END, values=(
                item['codigo'], item['nombre'][:30], item['cantidad'],
                f"${item['precio']:,.2f}", f"${item['subtotal']:,.2f}"
            ))
            subtotal += item['subtotal']
        
        iva = subtotal * 0.21
        total = subtotal + iva
        
        self.lbl_subtotal.config(text=f"${subtotal:,.2f}")
        self.lbl_iva.config(text=f"${iva:,.2f}")
        self.lbl_total.config(text=f"${total:,.2f}")
    
    def eliminar_del_carrito(self):
        seleccion = self.tabla_carrito.selection()
        if not seleccion:
            Alertas.mostrar_mensaje_advertencia("Seleccione un item del carrito")
            return
        
        item = self.tabla_carrito.item(seleccion[0])
        codigo = item['values'][0]
        
        for i, item_carrito in enumerate(self.carrito):
            if item_carrito['codigo'] == codigo:
                del self.carrito[i]
                break
        
        self.actualizar_carrito()
    
    def limpiar_carrito(self):
        if self.carrito and Alertas.preguntar_si("¿Limpiar todo el carrito?"):
            self.carrito = []
            self.actualizar_carrito()
    
    def registrar_venta(self):
        if not self.carrito:
            Alertas.mostrar_mensaje_advertencia("El carrito está vacío")
            return
        
        from models import Venta, DetalleVenta
        
        venta = Venta(
            numero_factura=generar_numero_factura(),
            cliente_nombre=self.entry_cliente.get().strip() or "CONSUMIDOR FINAL",
            usuario=self.usuario['nombre_usuario']
        )
        
        for item in self.carrito:
            venta.agregar_detalle(
                item['id_producto'],
                item['nombre'],
                item['cantidad'],
                item['precio']
            )
        
        try:
            VentaController.registrar_venta(venta)
            
            # NOTIFICAR EVENTOS
            Eventos.notificar(EVENTO_VENTA_REGISTRADA, {
                'factura': venta.numero_factura,
                'total': venta.total
            })
            Eventos.notificar(EVENTO_STOCK_ACTUALIZADO)
            
            Alertas.mostrar_mensaje_exito(f"✅ Venta registrada exitosamente!\nFactura: {venta.numero_factura}\nTotal: ${venta.total:,.2f}")
            
            self.limpiar_carrito()
            self.cargar_datos()
            self.actualizar_tabla_productos()
            self.entry_cliente.delete(0, tk.END)
            self.entry_cliente.insert(0, "CONSUMIDOR FINAL")
            
            # ACTUALIZAR DASHBOARD
            if self.main_app:
                self.main_app._refrescar_datos()
                self.main_app._mostrar_dashboard()
            else:
                if hasattr(self.parent, '_refrescar_datos'):
                    self.parent._refrescar_datos()
                self.window.destroy()
            
        except Exception as e:
            Alertas.mostrar_mensaje_error(f"❌ Error al registrar la venta: {str(e)}")