# utils/alertas.py
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox

class Alertas:
    """Clase para manejar todas las alertas del sistema"""
    
    @staticmethod
    def mostrar_alerta_stock_bajo(productos_bajo_stock, parent=None):
        """
        Muestra alerta visual cuando hay productos con stock bajo
        
        Args:
            productos_bajo_stock: Lista de productos con stock crítico
            parent: Ventana padre para la alerta
        """
        if not productos_bajo_stock:
            return
        
        # Contar productos por estado
        sin_stock = [p for p in productos_bajo_stock if p.get('stock_actual', 0) <= 0]
        stock_bajo = [p for p in productos_bajo_stock if 0 < p.get('stock_actual', 0) <= p.get('stock_minimo', 0)]
        
        # Crear ventana de alerta
        ventana = tk.Toplevel(parent) if parent else tk.Tk()
        ventana.title("⚠️ ALERTA DE STOCK CRÍTICO")
        ventana.geometry("600x500")
        ventana.configure(bg='#FFF3CD')
        ventana.attributes('-topmost', True)
        
        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() - 600) // 2
        y = (ventana.winfo_screenheight() - 500) // 2
        ventana.geometry(f"600x500+{x}+{y}")
        
        # Icono y título
        frame_titulo = tk.Frame(ventana, bg='#FFF3CD')
        frame_titulo.pack(fill=tk.X, pady=10)
        
        tk.Label(frame_titulo, text="⚠️", font=("Segoe UI", 32), 
                bg='#FFF3CD', fg='#DC3545').pack()
        
        tk.Label(frame_titulo, text="¡ALERTA DE STOCK CRÍTICO!", 
                font=("Segoe UI", 16, "bold"), bg='#FFF3CD', fg='#856404').pack()
        
        # Resumen
        frame_resumen = tk.Frame(ventana, bg='#FFF3CD')
        frame_resumen.pack(pady=10)
        
        tk.Label(frame_resumen, text=f"🔴 Sin stock: {len(sin_stock)} productos", 
                font=("Segoe UI", 11), bg='#FFF3CD', fg='#DC3545').pack()
        tk.Label(frame_resumen, text=f"🟡 Stock bajo: {len(stock_bajo)} productos", 
                font=("Segoe UI", 11), bg='#FFF3CD', fg='#FFC107').pack()
        
        # Frame para lista con scroll
        canvas = tk.Canvas(ventana, bg='#FFF3CD')
        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFF3CD')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Productos sin stock
        if sin_stock:
            tk.Label(scrollable_frame, text="🔴 PRODUCTOS SIN STOCK", 
                    font=("Segoe UI", 12, "bold"), bg='#FFF3CD', fg='#DC3545').pack(anchor=tk.W, pady=(10,5))
            
            for p in sin_stock:
                frame_prod = tk.Frame(scrollable_frame, bg='#FFF3CD')
                frame_prod.pack(fill=tk.X, padx=10, pady=2)
                
                tk.Label(frame_prod, text=f"• {p.get('nombre', '-')}", 
                        font=("Segoe UI", 10), bg='#FFF3CD', fg='#DC3545', 
                        anchor='w', width=40).pack(side=tk.LEFT)
                
                tk.Label(frame_prod, text=f"Stock: {p.get('stock_actual', 0)}", 
                        font=("Segoe UI", 10), bg='#FFF3CD', fg='#DC3545').pack(side=tk.RIGHT)
        
        # Productos con stock bajo
        if stock_bajo:
            tk.Label(scrollable_frame, text="🟡 PRODUCTOS CON STOCK BAJO", 
                    font=("Segoe UI", 12, "bold"), bg='#FFF3CD', fg='#FFC107').pack(anchor=tk.W, pady=(10,5))
            
            for p in stock_bajo:
                frame_prod = tk.Frame(scrollable_frame, bg='#FFF3CD')
                frame_prod.pack(fill=tk.X, padx=10, pady=2)
                
                tk.Label(frame_prod, text=f"• {p.get('nombre', '-')}", 
                        font=("Segoe UI", 10), bg='#FFF3CD', fg='#856404', 
                        anchor='w', width=40).pack(side=tk.LEFT)
                
                tk.Label(frame_prod, text=f"Stock: {p.get('stock_actual', 0)}/{p.get('stock_minimo', 0)}", 
                        font=("Segoe UI", 10), bg='#FFF3CD', fg='#856404').pack(side=tk.RIGHT)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Botón de acción
        tk.Button(ventana, text="📦 Generar Pedido Automático", 
                 bg='#28A745', fg='white', font=("Segoe UI", 11, "bold"),
                 command=lambda: Alertas._sugerir_pedido(ventana)).pack(pady=10)
        
        tk.Button(ventana, text="Cerrar", command=ventana.destroy,
                 bg='#6C757D', fg='white', width=20).pack(pady=10)
        
        if not parent:
            ventana.mainloop()
    
    @staticmethod
    def _sugerir_pedido(parent):
        """
        Sugiere generar un pedido automático
        Args:
            parent: Ventana padre
        """
        respuesta = messagebox.askyesno(
            "Generar Pedido",
            "¿Desea generar un pedido automático con los productos faltantes?\n\n"
            "Esto creará un pedido pendiente para su revisión."
        )
        if respuesta:
            messagebox.showinfo("Pedido Sugerido", 
                               "Se ha generado una sugerencia de pedido.\n"
                               "Revise la sección 'Pedidos' para confirmar.")
        parent.destroy()
    
    @staticmethod
    def mostrar_mensaje_exito(mensaje, titulo="Éxito"):
        """
        Muestra mensaje de éxito
        Args:
            mensaje: Mensaje a mostrar
            titulo: Título de la alerta
        """
        messagebox.showinfo(titulo, mensaje)
    
    @staticmethod
    def mostrar_mensaje_error(mensaje, titulo="Error"):
        """
        Muestra mensaje de error
        Args:
            mensaje: Mensaje a mostrar
            titulo: Título de la alerta
        """
        messagebox.showerror(titulo, mensaje)
    
    @staticmethod
    def mostrar_mensaje_advertencia(mensaje, titulo="Advertencia"):
        """
        Muestra mensaje de advertencia
        Args:
            mensaje: Mensaje a mostrar
            titulo: Título de la alerta
        """
        messagebox.showwarning(titulo, mensaje)
    
    @staticmethod
    def mostrar_mensaje_informacion(mensaje, titulo="Información"):
        """
        Muestra mensaje informativo
        Args:
            mensaje: Mensaje a mostrar
            titulo: Título de la alerta
        """
        messagebox.showinfo(titulo, mensaje)
    
    @staticmethod
    def preguntar_si(mensaje, titulo="Confirmar"):
        """
        Pregunta al usuario si/no
        Args:
            mensaje: Mensaje a mostrar
            titulo: Título de la alerta
        Returns:
            bool: True si el usuario responde sí, False si responde no
        """
        return messagebox.askyesno(titulo, mensaje)