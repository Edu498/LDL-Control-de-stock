# utils/eventos.py
# -*- coding: utf-8 -*-

class Eventos:
    """
    Módulo observador-sujeto que permite comunicar cambios en el sistema 
    sin acoplamiento directo entre módulos.

    Los controladores notifican eventos
    y las interfaces (vistas) se suscriben para actualizarse automáticamente.
    """
    
    _observadores = {}
    
    @classmethod
    def suscribir(cls, evento, callback):
        """
        Suscribe un callback a un evento
        Args:
            evento (str): Nombre del evento al que se suscribe.
            callback (function): Función a ejecutar cuando se notifique el evento.
        """
        if evento not in cls._observadores:
            cls._observadores[evento] = []
        cls._observadores[evento].append(callback)
        
    @classmethod
    def desuscribir(cls, evento, callback):
        """
        Desuscribe un callback de un evento
        Args:
            evento (str): Nombre del evento.
            callback (function): Función a remover.
        """
        if evento in cls._observadores and callback in cls._observadores[evento]:
            cls._observadores[evento].remove(callback)
    
    @classmethod
    def notificar(cls, evento, datos=None):
        """
        Notifica a todos los observadores de un evento
        Args:
            evento (str): Nombre del evento a notificar.
            datos (any, optional): Datos adicionales a pasar a los callbacks.
        """
        if evento in cls._observadores:
            observadores_activos = []
            
            for callback in cls._observadores[evento]:
                # Limpieza automática si el callback pertenece a un Widget destruido de Tkinter
                if hasattr(callback, '__self__'):
                    instancia = callback.__self__
                    if hasattr(instancia, 'window'):
                        widget = instancia.window
                        import tkinter as tk
                        if isinstance(widget, tk.Widget):
                            try:
                                if not widget.winfo_exists():
                                    continue  # Omitir y limpiar este observador
                            except Exception:
                                continue  # Omitir en caso de cualquier error de consulta
                
                observadores_activos.append(callback)
                
                try:
                    if datos:
                        callback(datos)
                    else:
                        callback()
                except Exception as e:
                    print(f"Error en callback: {e}")
            
            # Actualizar la lista con solo los observadores que siguen activos
            cls._observadores[evento] = observadores_activos
    
    @classmethod
    def limpiar(cls):
        """
        Limpia todos los observadores
        """
        cls._observadores = {}

# Eventos disponibles
EVENTO_STOCK_ACTUALIZADO = "stock_actualizado"
EVENTO_VENTA_REGISTRADA = "venta_registrada"
EVENTO_PRODUCTO_AGREGADO = "producto_agregado"
EVENTO_PRODUCTO_EDITADO = "producto_editado"
EVENTO_PEDIDO_CREADO = "pedido_creado"