# -*- coding: utf-8 -*-
"""
Módulo de conexión a Base de Datos
Sistema de Control de Stock
"""

from controllers import stock_controller
import mysql.connector
from mysql.connector import Error, pooling
from config import DB_CONFIG
import threading

class DatabasePool:
    """Pool de conexiones a Base de Datos - Thread Safe"""
    
    _instance = None
    _lock = threading.Lock()
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._create_pool()
    
    def _create_pool(self):
        """Crea el pool de conexiones"""
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name=DB_CONFIG.get('pool_name', 'mypool'),
                pool_size=DB_CONFIG.get('pool_size', 5),
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                charset=DB_CONFIG.get('charset', 'utf8mb4'),
                use_pure=DB_CONFIG.get('use_pure', True)
            )
        except Error as e:
            print(f"Error al crear pool de conexiones: {e}")
            raise
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        if self._pool is None:
            self._create_pool()
        return self._pool.get_connection()
    
    def close_all(self):
        """Cierra todas las conexiones del pool"""
        if self._pool:
            self._pool._remove_connections()
            self._pool = None

# Singleton para uso global
_db_pool = None

def get_connection():
    """Obtiene una conexión a la base de datos"""
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabasePool()
    return _db_pool.get_connection()

def close_connection(conn, cursor=None):
    """Cierra conexión y cursor de manera segura"""
    if cursor:
        try:
            cursor.close()
        except:
            pass
    if conn:
        try:
            conn.close()
        except:
            pass

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Ejecuta una consulta SQL de manera segura"""
    conn = None
    cursor = None
    resultado = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
        
        if fetch_one:
            resultado = cursor.fetchone()
        elif fetch_all:
            resultado = cursor.fetchall()
        else:
            resultado = cursor

        return resultado
        
    except Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if not(fetch_one is False and fetch_all is False and not commit):
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass