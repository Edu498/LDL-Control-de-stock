# 📦 Sistema de Control de Stock v2.0.0

Bienvenido al **Sistema de Control de Stock**, una solución de escritorio robusta y profesional desarrollada en **Python** utilizando **Tkinter** para la interfaz gráfica y **MySQL** para la persistencia de datos.

Este proyecto ha sido estructurado bajo un patrón de arquitectura **MVC (Modelo-Vista-Controlador)**, garantizando la escalabilidad, mantenibilidad y modularidad del código fuente, ideal para ser evaluado en entornos académicos y profesionales.

---

## 🚀 Características Principales

*   **🔑 Control de Acceso y Roles:** Pantalla de Login con soporte para perfiles diferenciados (`Administrador`, `Vendedor`, `Encargado de Compras`) y validación segura.
*   **📦 Gestión de Inventario (Productos):** Altas, bajas, modificaciones y consultas de productos. Incluye control de códigos de barra/únicos, categorización, asignación de proveedores, precios de compra/venta, cálculo automático de IVA y ubicaciones físicas en depósito.
*   **📊 Movimientos de Stock:** Registro histórico automatizado y detallado de cada entrada/salida (por venta, compra, ajuste manual positivo/negativo, devolución o merma) detallando usuario y fecha.
*   **💰 Módulo de Ventas:** Interfaz dinámica para facturación y salida de stock. Registra transacciones con clientes (con opción de Consumidor Final), cálculo en tiempo real de subtotales, IVA y totales correlativos.
*   **🚚 Órdenes de Compra (Pedidos):** Gestión de compras a proveedores con estados en tiempo real (`Pendiente`, `Enviado`, `Recibido`, `Cancelado`) y actualización automática de existencias al recibir los productos.
*   **⚠️ Alertas de Stock Bajo:** Alertas automáticas visuales para productos por debajo del stock mínimo establecido.
*   **📈 Reportes e Informes:** Estadísticas integradas para facilitar la toma de decisiones (ventas del mes, productos de mayor rotación y alertas de reposición).

---

## 📂 Arquitectura del Proyecto (Patrón MVC)

El proyecto está organizado de manera modular en las siguientes carpetas:

```text
📁 LDL-Control-de-stock/
│
├── 📁 controllers/         # Lógica de negocio y controladores del sistema
│   ├── pedido_controller.py
│   ├── reporte_controller.py
│   ├── stock_controller.py
│   └── venta_controller.py
│
├── 📁 models/              # Clases y estructuras de datos (Entidades)
│   ├── categoria.py
│   ├── pedido.py
│   ├── producto.py
│   ├── proveedor.py
│   ├── usuario.py
│   └── venta.py
│
├── 📁 vistas/              # Interfaces gráficas desarrolladas en Tkinter
│   ├── login_window.py
│   ├── main_window.py
│   ├── inventario_window.py
│   ├── productos_window.py
│   ├── pedidos_window.py
│   ├── ventas_window.py
│   └── reportes_window.py
│
├── 📁 utils/               # Funciones auxiliares, base de datos y eventos
│   ├── database.py         # Pool de conexiones MySQL thread-safe (Singleton)
│   ├── alertas.py          # Gestor de alertas de stock y notificaciones
│   ├── eventos.py          # Manejador de eventos desacoplado
│   └── helpers.py          # Utilidades para formatear moneda, IVA y fechas
│
├── 📁 assets/              # Iconos, imágenes y recursos visuales
├── 📁 docs/                # Documentación del proyecto
│
├── config.py               # Configuración global (Base de datos, IVA, negocio)
├── crear_bd.py             # Script de inicialización de la Base de Datos MySQL
├── diagnosticar.py         # Utilidad de diagnóstico rápido del estado del motor
├── verificar_estructura.py # Validador del árbol de directorios del proyecto
├── prueba_directa.py       # Simulación de operaciones de stock independientes
├── main.py                 # Punto de entrada principal de la aplicación
└── requirements.txt        # Dependencias de Python requeridas
```

---

## 🔄 Flujo de Negocio y Ciclo de Vida del Producto

Para asegurar que el inventario refleje la realidad en todo momento y no se presenten quiebres de stock ocultos, el sistema plantea el siguiente flujo de negocio documentado:

1. **Venta o Salida Real (Tiempo Real):**
   - Las ventas reales del comercio ocurren en un sistema de facturación externo (Punto de Venta o eCommerce).
   - Para evitar la doble carga y los errores humanos, este sistema dispone de una API (ver `api_ventas.py`) que actúa como **contrato de entrada**.
   - Cuando el sistema externo cierra una venta, dispara un evento a la API que se registra inmediatamente en una **tabla intermedia** (`ventas_pendientes_stock`) con estado `pendiente`.
   - *Nota:* El módulo de "Ventas" incluido en la aplicación de escritorio sirve **únicamente como contingencia manual o simulación**.

2. **Proceso de Stock Inmediato y Auditoría:**
   - Un proceso interno lee la tabla intermedia y procesa las ventas pendientes.
   - Descuenta el stock y actualiza el estado en la tabla a `procesada` (o `error` si hay inconsistencias).
   - Automáticamente se genera un registro inmutable en la tabla `movimientos_stock` detallando fecha, usuario, cantidad, y el ID de la transacción externa.

3. **Alerta y Sugerencia de Pedido:**
   - Si el stock, tras una salida, cae por debajo del umbral mínimo, el sistema activa una alerta visual (`SIN STOCK` o `STOCK BAJO`).
   - El módulo de "Pedidos" agrupa estos productos automáticamente y sugiere cantidades óptimas a reponer agrupadas por proveedor.

4. **Confirmación de Compra y Recepción (Ingreso):**
   - El usuario genera y confirma el pedido.
   - Al recibir la mercadería, el usuario va a "Pedidos Pendientes -> Recibir". 
   - Solo al confirmar las cantidades recibidas físicamente, el stock vuelve a aumentar.

5. **Control Físico Periódico (Auditoría):**
   - Periódicamente, el encargado de depósito utiliza la opción **"Conteo Físico"** en la ventana de Ajuste de Inventario. Ingresa la cantidad exacta observada en estantería.
   - El sistema calcula la diferencia automáticamente y ajusta el stock generando un movimiento compensatorio (merma o sobrante) para cuadrar el inventario virtual con el real.

---

## 🔌 Instrucciones para el Sistema Externo (Contrato de Integración)

Para que el sistema de facturación externo se comunique con este módulo de control de stock, debe seguir los siguientes pasos:

1. **Ubicación de la API:** La API (`api_ventas.py`) debe estar en ejecución continua. Escuchará peticiones en `http://<IP_DEL_SERVIDOR>:5000/api/ventas`.
2. **Trigger del Sistema Externo:** El sistema de ventas debe configurarse para que, inmediatamente después de cerrar un ticket o factura exitosamente, realice una petición HTTP `POST` a la URL mencionada.
3. **Mapeo de Datos:** El JSON enviado debe tener la siguiente estructura estricta:
   ```json
   {
       "origen": "SISTEMA_POS_EXTERNO",
       "referencia_externa": "ID_FACTURA_O_TICKET",
       "productos": [
           {"codigo": "CODIGO_DEL_PRODUCTO_1", "cantidad": 2},
           {"codigo": "CODIGO_DEL_PRODUCTO_2", "cantidad": 1}
       ]
   }
   ```
   *Es vital que el campo `codigo` coincida exactamente con los códigos registrados en esta base de datos de control de stock.*
4. **Manejo de Errores:** Si el sistema externo no logra conectarse con la API (ej. caída de red), se recomienda que guarde la venta en una cola local y reintente el envío más tarde. Una vez que la API recibe el JSON, nuestro sistema garantiza la consistencia transaccional y la auditoría.

---

## 🗄️ Modelo y Estructura de la Base de Datos

El script `crear_bd.py` genera de manera automática la base de datos `control_stock` con **13 tablas interrelacionadas** y una **vista optimizada**:

### Tablas Principales:
1.  `roles`: Define niveles de privilegios (`Administrador`, `Vendedor`, `Encargado_compras`).
2.  `usuarios`: Datos de usuario, contraseña, estado (`activo/inactivo`) y relación con rol.
3.  `categorias`: Clasificación de productos (Bebidas, Alimentos, Lácteos, etc.).
4.  `proveedores`: Información fiscal y de contacto comercial.
5.  `productos`: Stock actual, stock mínimo/máximo, precios e impuestos.
6.  `tipos_movimiento`: Catálogo de operaciones que alteran el stock (con signo aritmético `+` o `-`).
7.  `movimientos_stock`: Auditoría permanente de cada transacción de inventario.
8.  `ventas` y `detalles_venta`: Cabecera e ítems detallados de transacciones con clientes.
9.  `pedidos` y `detalles_pedido`: Control de compras y reposición de mercadería con proveedores.
10. `estados_venta` y `estados_pedido`: Tablas de estados maestros para consistencia e integridad.

### 👁️ Vista de Alertas:
*   `vw_stock_alertas`: Agrupa y evalúa dinámicamente los productos que requieren reposición urgente, calculando la cantidad recomendada a comprar.

---

## ⚙️ Instalación y Configuración

Sigue estos sencillos pasos para levantar el entorno localmente:

### 1. Requisitos Previos
Asegúrate de tener instalados:
*   [Python 3.8 o superior](https://www.python.org/downloads/)
*   [MySQL Server](https://dev.mysql.com/downloads/mysql/) (Puedes usar XAMPP, WampServer, Laragon o el instalador oficial de MySQL).

### 2. Configurar la Base de Datos
1.  Inicia tu servicio de MySQL Server.
2.  Si es necesario, edita el archivo `config.py` con las credenciales de tu servidor de base de datos local:
    ```python
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root', # Cambia a tu contraseña de MySQL
        'database': 'control_stock',
        'port': 3306
    }
    ```

### 3. Instalar Dependencias
Abre la consola en el directorio raíz del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```
*Las dependencias incluyen `mysql-connector-python` para la conexión a base de datos y `Pillow` para la manipulación de imágenes/assets.*

### 4. Inicializar la Base de Datos (Seed/Semilla)
Crea la base de datos, tablas, relaciones y datos de demostración ejecutando:
```bash
python crear_bd.py
```
*Este comando eliminará cualquier base de datos previa llamada `control_stock` y la reconfigurará desde cero con registros limpios y listos para usar.*

---

## 🔑 Credenciales por Defecto

Una vez inicializada la base de datos, puedes ingresar al sistema con los siguientes datos:
*   **Usuario:** `admin`
*   **Contraseña:** `admin123`

---

## 🖥️ Ejecución y Pruebas

### Ejecutar el Sistema
Para iniciar la interfaz gráfica del programa, ejecuta el archivo principal:
```bash
python main.py
```

### Scripts de Diagnóstico e Integridad
Se incluyen utilidades de consola creadas específicamente para verificar el correcto funcionamiento del software:

1.  **Verificar Integridad de Archivos:**
    ```bash
    python verificar_estructura.py
    ```
    *Comprueba que todas las carpetas y archivos críticos estén ubicados en su lugar correspondiente.*

2.  **Diagnosticar Base de Datos:**
    ```bash
    python diagnosticar.py
    ```
    *Muestra en consola el estado de conexión de la base de datos, la lista de movimientos registrados en el sistema y los productos críticos de forma rápida sin abrir la GUI.*

3.  **Simular Transacciones de Inventario:**
    ```bash
    python prueba_directa.py
    ```
    *Permite simular ingresos y egresos de stock a nivel lógico directamente en la base de datos, verificando que los disparadores lógicos actúen adecuadamente.*

---

## 🛠️ Tecnologías y Buenas Prácticas
*   **Conexión Segura (Pool de Conexiones):** Implementación de un pool thread-safe para optimizar los recursos de conexión TCP a MySQL.
*   **Manejo de Transacciones (ACID):** Rollbacks automáticos ante fallos durante operaciones complejas de facturación o recepción de pedidos.
*   **Interfaces dinámicas con Tkinter:** Uso de elementos adaptativos, binding de eventos de teclado (como presionar `Enter` para ingresar) y efectos interactivos visuales (hover en botones).
