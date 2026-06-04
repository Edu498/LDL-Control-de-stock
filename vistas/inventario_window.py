import tkinter as tk
from tkinter import ttk, messagebox
from controllers.stock_controller import StockController
from utils.alertas import Alertas
from utils.eventos import Eventos, EVENTO_STOCK_ACTUALIZADO

class AjusteStockWindow:
    """
    Ventana profesional para ajuste de inventario
    Permite agregar o quitar stock con registro de motivo
    """
    
    def __init__(self, parent, producto, callback_refresh):
        self.parent = parent
        self.producto = producto
        self.callback_refresh = callback_refresh
        
        # Crear ventana principal
        self.window = tk.Toplevel(parent)
        self.window.title(f"Ajuste de Inventario - {producto.nombre}")
        self.window.geometry("550x650")
        self.window.configure(bg='#F0F4F8')
        self.window.resizable(False, False)
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 550) // 2
        y = (self.window.winfo_screenheight() - 650) // 2
        self.window.geometry(f"550x650+{x}+{y}")
        
        # Configurar modal
        self.window.transient(parent.winfo_toplevel())
        self.window.grab_set()
        self.window.focus_force()
        
        # Variable para tipo de ajuste
        self.tipo_ajuste = tk.StringVar(value="entrada")
        
        self.crear_widgets()
        self.actualizar_estimacion()
    
    def crear_widgets(self):
        # HEADER
        header_frame = tk.Frame(self.window, bg='#2C3E50', height=90)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📦", font=("Segoe UI", 32), 
                bg='#2C3E50', fg='white').pack(side=tk.LEFT, padx=20, pady=15)
        
        header_text = tk.Frame(header_frame, bg='#2C3E50')
        header_text.pack(side=tk.LEFT, padx=10)
        
        tk.Label(header_text, text="AJUSTE DE INVENTARIO", 
                font=("Segoe UI", 16, "bold"), bg='#2C3E50', fg='white').pack(anchor=tk.W)
        
        tk.Label(header_text, text="Control preciso de existencias", 
                font=("Segoe UI", 9), bg='#2C3E50', fg='#95A5A6').pack(anchor=tk.W)
        
        # CONTENIDO PRINCIPAL
        main_frame = tk.Frame(self.window, bg='#F0F4F8')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # TARJETA DE PRODUCTO
        producto_card = self._crear_tarjeta(main_frame, " PRODUCTO SELECCIONADO")
        
        tk.Label(producto_card, text=self.producto.nombre, 
                font=("Segoe UI", 14, "bold"), bg='white', fg='#2C3E50').pack(anchor=tk.W, pady=(5, 0))
        
        info_frame = tk.Frame(producto_card, bg='white')
        info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(info_frame, text=f"Código: {self.producto.codigo}", 
                font=("Segoe UI", 10), bg='white', fg='#7F8C8D').pack(side=tk.LEFT)
        
        tk.Label(info_frame, text=f"Stock mínimo: {self.producto.stock_minimo} unidades", 
                font=("Segoe UI", 10), bg='white', fg='#7F8C8D').pack(side=tk.RIGHT)
        
        # TARJETA DE STOCK ACTUAL
        stock_card = self._crear_tarjeta(main_frame, " STOCK ACTUAL")
        
        # Determinar color según estado
        if self.producto.stock_actual <= 0:
            color_stock = "#E74C3C"
            estado_texto = "SIN STOCK - URGENTE!"
        elif self.producto.stock_actual <= self.producto.stock_minimo:
            color_stock = "#F39C12"
            estado_texto = "Stock bajo - Requiere atención"
        else:
            color_stock = "#27AE60"
            estado_texto = "Stock normal"
        
        stock_value_frame = tk.Frame(stock_card, bg='white')
        stock_value_frame.pack(pady=10)
        
        tk.Label(stock_value_frame, text=str(self.producto.stock_actual), 
                font=("Segoe UI", 48, "bold"), bg='white', fg=color_stock).pack(side=tk.LEFT)
        
        tk.Label(stock_value_frame, text="unidades", 
                font=("Segoe UI", 14), bg='white', fg='#7F8C8D').pack(side=tk.LEFT, padx=10)
        
        tk.Label(stock_card, text=estado_texto, 
                font=("Segoe UI", 10, "bold"), bg='white', fg=color_stock).pack(pady=5)
        
        # TARJETA DE OPERACIÓN
        operacion_card = self._crear_tarjeta(main_frame, " TIPO DE OPERACIÓN")
        
        radio_frame = tk.Frame(operacion_card, bg='white')
        radio_frame.pack(fill=tk.X, pady=10)
        
        entrada_radio = tk.Radiobutton(radio_frame, text="AGREGAR STOCK", 
                                       variable=self.tipo_ajuste, value="entrada",
                                       bg='white', font=("Segoe UI", 11, "bold"),
                                       fg='#27AE60', selectcolor='white',
                                       command=self.actualizar_estimacion)
        entrada_radio.pack(side=tk.LEFT, padx=20)
        
        salida_radio = tk.Radiobutton(radio_frame, text="QUITAR STOCK", 
                                      variable=self.tipo_ajuste, value="salida",
                                      bg='white', font=("Segoe UI", 11, "bold"),
                                      fg='#E74C3C', selectcolor='white',
                                      command=self.actualizar_estimacion)
        salida_radio.pack(side=tk.LEFT, padx=20)
        
        # CANTIDAD
        cantidad_frame = tk.Frame(operacion_card, bg='white')
        cantidad_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(cantidad_frame, text="Cantidad:", 
                font=("Segoe UI", 11, "bold"), bg='white').pack(anchor=tk.W)
        
        spin_frame = tk.Frame(cantidad_frame, bg='white')
        spin_frame.pack(fill=tk.X, pady=5)
        
        self.spin_cantidad = tk.Spinbox(spin_frame, from_=1, to=9999, width=15, 
                                         font=("Segoe UI", 16), justify='center')
        self.spin_cantidad.pack(side=tk.LEFT)
        self.spin_cantidad.delete(0, tk.END)
        self.spin_cantidad.insert(0, "1")
        self.spin_cantidad.bind('<KeyRelease>', lambda e: self.actualizar_estimacion())
        
        tk.Label(spin_frame, text="unidades", 
                font=("Segoe UI", 12), bg='white').pack(side=tk.LEFT, padx=15)
        
        # MOTIVO
        motivo_frame = tk.Frame(operacion_card, bg='white')
        motivo_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(motivo_frame, text="Motivo del ajuste:", 
                font=("Segoe UI", 11, "bold"), bg='white').pack(anchor=tk.W)
        
        self.combo_motivo = ttk.Combobox(motivo_frame, values=[
            'Ajuste de inventario', 'Corrección de stock', 
            'Merma o rotura', 'Devolución', 'Ingreso manual'
        ], width=45, font=("Segoe UI", 10))
        self.combo_motivo.pack(fill=tk.X, pady=5)
        self.combo_motivo.set('Ajuste de inventario')
        
        # TARJETA DE RESULTADO
        resultado_card = self._crear_tarjeta(main_frame, " RESULTADO ESTIMADO")
        
        resultado_value_frame = tk.Frame(resultado_card, bg='white')
        resultado_value_frame.pack(pady=10)
        
        self.lbl_nuevo_stock = tk.Label(resultado_value_frame, text=str(self.producto.stock_actual), 
                                         font=("Segoe UI", 42, "bold"), bg='white', fg='#3498DB')
        self.lbl_nuevo_stock.pack(side=tk.LEFT)
        
        tk.Label(resultado_value_frame, text="unidades", 
                font=("Segoe UI", 14), bg='white', fg='#7F8C8D').pack(side=tk.LEFT, padx=10)
        
        self.lbl_mensaje = tk.Label(resultado_card, 
                                    text="Seleccione el tipo de operación y la cantidad",
                                    font=("Segoe UI", 9), bg='white', fg='#7F8C8D')
        self.lbl_mensaje.pack(pady=5)
        
        # BOTONES
        botones_frame = tk.Frame(main_frame, bg='#F0F4F8')
        botones_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(botones_frame, text="GUARDAR CAMBIOS", command=self.guardar_ajuste,
                 bg='#2C3E50', fg='white', font=("Segoe UI", 11, "bold"),
                 padx=40, pady=10, cursor='hand2', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        
        tk.Button(botones_frame, text="CANCELAR", command=self.window.destroy,
                 bg='#95A5A6', fg='white', font=("Segoe UI", 11),
                 padx=30, pady=10, cursor='hand2', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        
        # FOOTER
        footer_frame = tk.Frame(self.window, bg='#F0F4F8', height=35)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(footer_frame, text="Los cambios se reflejarán automáticamente en el inventario", 
                font=("Segoe UI", 8), bg='#F0F4F8', fg='#95A5A6').pack(pady=8)
    
    def _crear_tarjeta(self, parent, titulo):
        """Crea una tarjeta estilizada para secciones"""
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1, padx=15, pady=10)
        frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame, text=titulo, font=("Segoe UI", 9, "bold"), 
                bg='white', fg='#7F8C8D').pack(anchor=tk.W)
        
        return frame
    
    def actualizar_estimacion(self, event=None):
        """Actualiza la estimación del stock nuevo"""
        try:
            cantidad = int(self.spin_cantidad.get())
            if cantidad <= 0:
                cantidad = 1
                self.spin_cantidad.delete(0, tk.END)
                self.spin_cantidad.insert(0, "1")
        except:
            cantidad = 1
            self.spin_cantidad.delete(0, tk.END)
            self.spin_cantidad.insert(0, "1")
        
        if self.tipo_ajuste.get() == "salida":
            cantidad = -cantidad
            nuevo = self.producto.stock_actual + cantidad
            if nuevo < 0:
                nuevo = 0
            self.lbl_mensaje.config(text="Se QUITARÁN unidades del stock actual")
            self.lbl_nuevo_stock.config(fg='#E74C3C')
        else:
            nuevo = self.producto.stock_actual + cantidad
            self.lbl_mensaje.config(text="Se AGREGARÁN unidades al stock actual")
            self.lbl_nuevo_stock.config(fg='#27AE60')
        
        self.lbl_nuevo_stock.config(text=str(nuevo))
    
    def guardar_ajuste(self):
        """Guarda el ajuste de stock y actualiza la base de datos"""
        try:
            cantidad = int(self.spin_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except:
            Alertas.mostrar_mensaje_advertencia("Ingrese una cantidad válida (mayor a 0)")
            return
        
        # Validar operación de salida
        if self.tipo_ajuste.get() == "salida":
            if cantidad > self.producto.stock_actual:
                Alertas.mostrar_mensaje_advertencia(
                    f"No puede quitar más stock del disponible\n\n"
                    f"Stock actual: {self.producto.stock_actual} unidades\n"
                    f"Intenta quitar: {cantidad} unidades"
                )
                return
            cantidad_ajuste = -cantidad
            tipo_movimiento = 4
            operacion_texto = f"QUITAR {cantidad} unidades"
        else:
            cantidad_ajuste = cantidad
            tipo_movimiento = 3
            operacion_texto = f"AGREGAR {cantidad} unidades"
        
        try:
            # Obtener usuario correctamente
            usuario_actual = "admin"
            if hasattr(self.parent, 'usuario'):
                if isinstance(self.parent.usuario, dict):
                    usuario_actual = self.parent.usuario.get('nombre_usuario', 'admin')
                else:
                    usuario_actual = str(self.parent.usuario)
            
            # Realizar actualización
            nuevo_stock = StockController.actualizar_stock(
                id_producto=self.producto.id_producto,
                cantidad=cantidad_ajuste,
                tipo_movimiento=tipo_movimiento,
                usuario=usuario_actual,
                referencia={'tipo': 'ajuste', 'motivo': self.combo_motivo.get().strip()}
            )
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "AJUSTE COMPLETADO",
                f"Stock actualizado correctamente\n\n"
                f"Producto: {self.producto.nombre}\n"
                f"Operación: {operacion_texto}\n"
                f"Stock anterior: {self.producto.stock_actual} unidades\n"
                f"Stock nuevo: {nuevo_stock} unidades\n\n"
                f"Motivo: {self.combo_motivo.get()}"
            )
            
            # Notificar evento para actualizar todas las ventanas
            Eventos.notificar(EVENTO_STOCK_ACTUALIZADO, {
                'id_producto': self.producto.id_producto,
                'stock_nuevo': nuevo_stock,
                'stock_anterior': self.producto.stock_actual
            })
            
            # Actualizar el objeto producto
            self.producto.stock_actual = nuevo_stock
            
            # Actualizar la tabla de productos
            if self.callback_refresh:
                try:
                    self.callback_refresh()
                except Exception as e:
                    print(f"Error en callback: {e}")
            
            # Actualizar el dashboard principal
            if hasattr(self.parent, '_refrescar_datos'):
                try:
                    self.parent._refrescar_datos()
                except Exception as e:
                    print(f"Error refrescando datos: {e}")
            
            # Cerrar ventana
            self.window.destroy()
            
        except ValueError as e:
            Alertas.mostrar_mensaje_error(str(e))
        except Exception as e:
            Alertas.mostrar_mensaje_error(f"Error al actualizar stock: {str(e)}")
            import traceback
            traceback.print_exc()