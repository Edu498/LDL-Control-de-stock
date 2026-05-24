# -*- coding: utf-8 -*-
"""
Ventana Principal (Dashboard) del Sistema de Control de Stock.
"""

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

class MainWindow:
    """
    Representa la ventana principal y panel de control (Dashboard) de la aplicación.

    Carga métricas clave (KPIs) en tiempo real, tablas de stock crítico e historial de ventas.
    Gestiona el menú de navegación para abrir el resto de vistas del sistema.
    """

    def __init__(self, usuario):
        """
        Inicializa y construye la ventana principal.

        Args:
            usuario (dict): Diccionario con los datos del usuario autenticado (id, nombre, rol).
        """
        self.usuario = usuario
        self.window = tk.Tk()
        self.window.title(f"Sistema de Control de Stock - {usuario['nombre_completo']}")
        self.window.geometry("1280x720")
        self.window.configure(bg='#F0F4F8')
        
        self._cargar_datos()
        self._verificar_alertas()
        self._crear_menu()
        self._crear_widgets()
        self._mostrar_dashboard()
        
        self.window.mainloop()
    
    def _cargar_datos(self):
        """
        Carga datos desde los controladores correspondientes para poblar el Dashboard.
        """
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
        """
        Muestra la alerta visual de stock crítico si existen productos bajo stock.
        """
        if self.productos_alerta:
            Alertas.mostrar_alerta_stock_bajo(self.productos_alerta, self.window)
    
    def _crear_menu(self):
        """
        Genera la barra de menú superior con opciones de navegación y cierre.
        """
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
        """
        Crea el contenedor base sobre el cual se montarán las diferentes pantallas.
        """
        self.frame_principal = tk.Frame(self.window, bg='#F0F4F8')
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    def _mostrar_dashboard(self):
        """
        Dibuja los componentes visuales del Dashboard (Tarjetas KPI, tabla de alertas y últimas ventas).
        """
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
        """
        Crea y ubica una tarjeta KPI individual en formato cuadrícula.

        Args:
            parent (tk.Frame): Frame contenedor.
            titulo (str): Título de la tarjeta.
            valor (str): Valor principal a destacar.
            subtitulo (str): Texto secundario informativo.
            columna (int): Columna de la cuadrícula donde se posicionará.
        """
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        frame.grid(row=0, column=columna, padx=10, pady=5, sticky='nsew')
        
        tk.Label(frame, text=titulo, font=("Segoe UI", 11), bg='white', fg='#6C757D').pack(pady=(10,5))
        tk.Label(frame, text=valor, font=("Segoe UI", 24, "bold"), bg='white', fg='#007BFF').pack(pady=5)
        tk.Label(frame, text=subtitulo, font=("Segoe UI", 9), bg='white', fg='#6C757D').pack(pady=(5,10))
        
        parent.columnconfigure(columna, weight=1)
    
    def _crear_tabla_alertas(self):
        """
        Genera la tabla (Treeview) de productos que requieren reposición inmediata.
        """
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
        """
        Genera la tabla (Treeview) con el registro de las últimas ventas del día.
        """
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
    
    def _abrir_productos(self):
        """
        Instancia y despliega el ABM de Productos.
        """
        from vistas.productos_window import ProductosWindow
        ProductosWindow(self.window, self.usuario)
    
    def _abrir_ventas(self):
        """
        Instancia y despliega la ventana de registro de Ventas.
        """
        from vistas.ventas_window import VentasWindow
        VentasWindow(self.window, self.usuario)
    
    def _abrir_pedidos(self):
        """
        Instancia y despliega el gestor de Pedidos de reposición.
        """
        from vistas.pedidos_window import PedidosWindow
        PedidosWindow(self.window, self.usuario)
    
    def _reporte_stock(self):
        """
        Abre el visor del reporte del Stock Actual.
        """
        from vistas.reportes_window import ReporteStock
        ReporteStock(self.window)
    
    def _reporte_movimientos(self):
        """
        Abre el visor del reporte de Movimientos de inventario.
        """
        from vistas.reportes_window import ReporteMovimientos
        ReporteMovimientos(self.window)
    
    def _reporte_ventas(self):
        """
        Abre el visor del reporte de Ventas registradas.
        """
        from vistas.reportes_window import ReporteVentas
        ReporteVentas(self.window)
    
    def _salir(self):
        """
        Muestra un cuadro de confirmación para cerrar la aplicación de forma segura.
        """
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir?"):
            self.window.destroy()