# vistas/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Agregar path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.stock_controller import StockController
from controllers.venta_controller import VentaController
from controllers.pedido_controller import PedidoController
from utils.alertas import Alertas
from utils.helpers import formatear_precio, formatear_fecha
from utils.eventos import Eventos, EVENTO_VENTA_REGISTRADA, EVENTO_STOCK_ACTUALIZADO, EVENTO_PEDIDO_CREADO

class MainWindow:
    def __init__(self, usuario):
        self.usuario = usuario
        self.window = tk.Tk()
        self.window.title(f"Sistema de Control de Stock - {usuario['nombre_completo']}")
        self.window.geometry("1280x720")
        self.window.configure(bg='#F0F4F8')
        
        # Variable para controlar alertas mostradas
        self.alertas_mostradas = set()
        
        self._cargar_datos()
        self._verificar_alertas()
        self._crear_menu()
        self._crear_widgets()
        self._mostrar_dashboard()
        
        # Suscribirse a eventos
        Eventos.suscribir(EVENTO_VENTA_REGISTRADA, self._actualizar_dashboard)
        Eventos.suscribir(EVENTO_STOCK_ACTUALIZADO, self._actualizar_dashboard)
        Eventos.suscribir(EVENTO_PEDIDO_CREADO, self._actualizar_dashboard)
        
        # Iniciar auto-refresh
        self._iniciar_auto_refresh()
        
        self.window.mainloop()
    
    def _cargar_datos(self):
        try:
            self.productos_alerta = StockController.get_productos_con_alerta()
            self.ventas_hoy = VentaController.get_ventas_hoy()
            self.resumen_ventas = VentaController.get_resumen_dia()
            self.pedidos_pendientes = PedidoController.get_pedidos_pendientes()
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.productos_alerta = []
            self.ventas_hoy = []
            self.resumen_ventas = {'monto_total': 0, 'total_ventas': 0}
            self.pedidos_pendientes = []
    
    def _verificar_alertas(self):
        if not self.productos_alerta:
            return
        
        # Obtener IDs de productos con alerta actual
        alertas_actuales = {p.get('id_producto') for p in self.productos_alerta if p.get('id_producto')}
        
        # Verificar si hay productos NUEVOS con alerta
        nuevas_alertas = alertas_actuales - self.alertas_mostradas
        
        if nuevas_alertas:
            # Solo mostrar alerta si hay productos nuevos
            productos_nuevos = [p for p in self.productos_alerta if p.get('id_producto') in nuevas_alertas]
            Alertas.mostrar_alerta_stock_bajo(productos_nuevos, self.window)
            self.alertas_mostradas = alertas_actuales
    
    def _crear_menu(self):
        menubar = tk.Menu(self.window)
        
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Dashboard", command=self._mostrar_dashboard)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self._salir)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        
        menu_operaciones = tk.Menu(menubar, tearoff=0)
        menu_operaciones.add_command(label="Productos", command=self._abrir_productos)
        menu_operaciones.add_command(label="Ventas", command=self._abrir_ventas)
        menu_operaciones.add_command(label="Pedidos", command=self._abrir_pedidos)
        menubar.add_cascade(label="Operaciones", menu=menu_operaciones)
        
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menu_reportes.add_command(label="Stock Actual", command=self._reporte_stock)
        menu_reportes.add_command(label="Movimientos", command=self._reporte_movimientos)
        menu_reportes.add_command(label="Ventas", command=self._reporte_ventas)
        menubar.add_cascade(label="Reportes", menu=menu_reportes)
        
        self.window.config(menu=menubar)
    
    def _crear_widgets(self):
        self.frame_principal = tk.Frame(self.window, bg='#F0F4F8')
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    def _mostrar_dashboard(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        tk.Label(self.frame_principal, text="📊 DASHBOARD PRINCIPAL", 
                font=("Segoe UI", 20, "bold"), bg='#F0F4F8', fg='#2C3E50').pack(pady=10)
        
        frame_kpi = tk.Frame(self.frame_principal, bg='#F0F4F8')
        frame_kpi.pack(fill=tk.X, pady=15)
        
        self._crear_tarjeta(frame_kpi, "💰 VENTAS HOY", 
                           formatear_precio(self.resumen_ventas.get('monto_total', 0)),
                           f"{self.resumen_ventas.get('total_ventas', 0)} ventas", 0)
        
        self._crear_tarjeta(frame_kpi, "⚠️ STOCK CRÍTICO", 
                           str(len([p for p in self.productos_alerta if p.get('stock_actual', 0) <= 0])),
                           f"{len([p for p in self.productos_alerta if p.get('stock_actual', 0) > 0])} con stock bajo", 1)
        
        self._crear_tarjeta(frame_kpi, "📦 PEDIDOS", 
                           str(len(self.pedidos_pendientes)),
                           "pedidos pendientes", 2)
        
        tk.Label(self.frame_principal, text="🔔 PRODUCTOS CON ALERTA", 
                font=("Segoe UI", 14, "bold"), bg='#F0F4F8', fg='#DC3545').pack(anchor=tk.W, pady=(15,5))
        self._crear_tabla_alertas()
        
        tk.Label(self.frame_principal, text="🕒 ÚLTIMAS VENTAS", 
                font=("Segoe UI", 14, "bold"), bg='#F0F4F8', fg='#2C3E50').pack(anchor=tk.W, pady=(15,5))
        self._crear_tabla_ventas()
    
    def _crear_tarjeta(self, parent, titulo, valor, subtitulo, columna):
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        frame.grid(row=0, column=columna, padx=10, pady=5, sticky='nsew')
        
        tk.Label(frame, text=titulo, font=("Segoe UI", 11), bg='white', fg='#6C757D').pack(pady=(10,5))
        tk.Label(frame, text=valor, font=("Segoe UI", 24, "bold"), bg='white', fg='#007BFF').pack(pady=5)
        tk.Label(frame, text=subtitulo, font=("Segoe UI", 9), bg='white', fg='#6C757D').pack(pady=(5,10))
        
        parent.columnconfigure(columna, weight=1)
    
    def _crear_tabla_alertas(self):
        frame = tk.Frame(self.frame_principal, bg='#F0F4F8')
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Código', 'Producto', 'Stock', 'Mínimo', 'Estado')
        tabla = ttk.Treeview(frame, columns=columnas, show='headings', yscrollcommand=scrollbar.set, height=8)
        
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=250 if col == 'Producto' else 100)
        
        for p in self.productos_alerta:
            tabla.insert('', tk.END, values=(
                p.get('codigo', '-'), p.get('nombre', '-')[:45],
                p.get('stock_actual', 0), p.get('stock_minimo', 0),
                p.get('estado_stock', 'NORMAL')
            ))
        
        tabla.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tabla.yview)
    
    def _crear_tabla_ventas(self):
        frame = tk.Frame(self.frame_principal, bg='#F0F4F8')
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columnas = ('Factura', 'Cliente', 'Fecha', 'Total')
        tabla = ttk.Treeview(frame, columns=columnas, show='headings', yscrollcommand=scrollbar.set, height=6)
        
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=180)
        
        for v in self.ventas_hoy[:10]:
            tabla.insert('', tk.END, values=(
                v.get('numero_factura', 'N/A'),
                v.get('cliente_nombre', 'CF'),
                formatear_fecha(v.get('fecha_venta', '')),
                formatear_precio(v.get('total', 0))
            ))
        
        tabla.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tabla.yview)
    
    def _actualizar_dashboard(self, datos=None):
        """Actualiza el dashboard en tiempo real"""
        self.window.after(100, self._refrescar_datos)
    
    def _refrescar_datos(self):
        """Recarga los datos y actualiza la interfaz"""
        self._cargar_datos()
        self._mostrar_dashboard()
        self._verificar_alertas()
        self.window.update_idletasks()
    
    def _iniciar_auto_refresh(self):
        """Inicia la actualización automática periódica"""
        def auto_refresh():
            if hasattr(self, 'window') and self.window.winfo_exists():
                self._refrescar_datos()
                self.window.after(10000, auto_refresh)  # Cada 10 segundos
        
        self.window.after(5000, auto_refresh)  # Primera actualización a los 5 segundos
    
    def _abrir_productos(self):
        from vistas.productos_window import ProductosWindow
        ProductosWindow(self.window, self.usuario)
    
    def _abrir_ventas(self):
        from vistas.ventas_window import VentasWindow
        VentasWindow(self.window, self.usuario)
    
    def _abrir_pedidos(self):
        from vistas.pedidos_window import PedidosWindow
        PedidosWindow(self.window, self.usuario)
    
    def _reporte_stock(self):
        from vistas.reportes_window import ReporteStock
        ReporteStock(self.window)
    
    def _reporte_movimientos(self):
        from vistas.reportes_window import ReporteMovimientos
        ReporteMovimientos(self.window)
    
    def _reporte_ventas(self):
        from vistas.reportes_window import ReporteVentas
        ReporteVentas(self.window)
    
    def _salir(self):
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir?"):
            self.window.destroy()