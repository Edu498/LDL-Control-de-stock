# -*- coding: utf-8 -*-
"""
Módulo de conexión y Pool de conexiones a la Base de Datos.

Proporciona un Pool de conexiones thread-safe (DatabasePool) utilizando
mysql.connector y funciones helper globales para obtener conexiones y
ejecutar consultas SQL de manera segura.
"""

import mysql.connector
from mysql.connector import Error, pooling
from config import DB_CONFIG
import threading

class DatabasePool:
    """
    Pool de conexiones a la Base de Datos MySQL (Implementación Singleton y Thread-Safe).

    Gestiona la creación y el mantenimiento de un pool de conexiones concurrentes para evitar
    la sobrecarga de abrir y cerrar conexiones en cada petición al motor.
    """
    
    _instance = None
    _lock = threading.Lock()
    _pool = None
    
    def __new__(cls):
        """
        Garantiza que exista una única instancia de DatabasePool a nivel global (Patrón Singleton).
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Inicializa el DatabasePool y crea el pool de conexiones de base de datos la primera vez.
        """
        if self._initialized:
            return
        self._initialized = True
        self._create_pool()
    
    def _create_pool(self):
        """
        Crea el pool de conexiones usando la configuración especificada en DB_CONFIG.

        Raises:
            mysql.connector.Error: Si ocurre un error al intentar configurar o abrir el pool de conexiones.
        """
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
        """
        Obtiene una conexión libre del pool.

        Returns:
            mysql.connector.pooling.PooledMySQLConnection: Conexión activa a la base de datos.
        """
        if self._pool is None:
            self._create_pool()
        return self._pool.get_connection()
    
    def close_all(self):
        """
        Cierra y remueve de forma segura todas las conexiones gestionadas por el pool.
        """
        if self._pool:
            self._pool._remove_connections()
            self._pool = None

# Singleton para uso global
_db_pool = None

def get_connection():
    """
    Función utilitaria global para obtener una conexión del pool compartido.

    Returns:
        mysql.connector.pooling.PooledMySQLConnection: Una conexión de base de datos del pool único.
    """
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabasePool()
    return _db_pool.get_connection()

def close_connection(conn, cursor=None):
    """
    Cierra la conexión y el cursor de forma segura controlando posibles excepciones.

    Args:
        conn (mysql.connector.connection_cext.CMySQLConnection): Conexión de base de datos a cerrar.
        cursor (mysql.connector.cursor_cext.CMySQLCursor, opcional): Cursor a cerrar.
    """
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
    """
    Ejecuta una consulta SQL genérica, maneja la transacción y cierra recursos opcionalmente.

    Args:
        query (str): Sentencia SQL a ejecutar.
        params (tuple, opcional): Parámetros a inyectar en la consulta.
        fetch_one (bool, opcional): Si es True, retorna solo la primera fila de resultados.
        fetch_all (bool, opcional): Si es True, retorna todas las filas de resultados.
        commit (bool, opcional): Si es True, ejecuta conn.commit() tras ejecutar la sentencia SQL.

    Returns:
        dict, list o mysql.connector.cursor: Depende de los parámetros:
            - dict si fetch_one es True (gracias a dictionary=True).
            - list de dicts si fetch_all es True.
            - mysql.connector.cursor si ambos son False (debe ser cerrado manualmente junto con la conexión).

    Raises:
        mysql.connector.Error: Si ocurre un error en la base de datos (se ejecuta Rollback si conn existe).
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if commit:
            conn.commit()
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor
        
    except Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor and not fetch_one and not fetch_all:
            cursor.close()
        if conn and not fetch_one and not fetch_all:
            conn.close()