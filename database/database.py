import sqlite3
from pathlib import Path
# Ubicación de la base de datos
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "aberacas.db"
def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute(
        "PRAGMA foreign_keys = ON"
    )
    return conexion


def crear_base_datos():
    conexion = conectar()
    cursor = conexion.cursor()
    # TABLA USUARIOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            telefono_emergencia TEXT,
            descuento REAL DEFAULT 0,
            fecha_ingreso TEXT,
            genero TEXT,
            estatus TEXT,
            instructor TEXT,
            nivel_nado TEXT,
            hora_asistencia TEXT,
            fecha_fin_registro TEXT
        )
    """)
    # TABLA EMPLEADOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL,
            turno TEXT,
            alberca TEXT,
            activo INTEGER DEFAULT 1
        )
    """)
    # TABLA PRODUCTOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            tipo TEXT,
            unidad TEXT,
            costo_unitario REAL DEFAULT 0,
            iva REAL DEFAULT 0,
            precio_final REAL DEFAULT 0,
            existencia INTEGER DEFAULT 0,
            ventas INTEGER DEFAULT 0,
            fecha_ingreso TEXT,
            descripcion TEXT,
            observaciones TEXT,
            activo INTEGER DEFAULT 1
        )
    """)
    # TABLA VENTAS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT UNIQUE NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            empleado_id INTEGER,
            cliente_id INTEGER,
            subtotal REAL DEFAULT 0,
            descuento REAL DEFAULT 0,
            total REAL DEFAULT 0,
            metodo_pago TEXT,
            estatus TEXT DEFAULT 'Completada',
            FOREIGN KEY (empleado_id)
                REFERENCES empleados(id),
            FOREIGN KEY (cliente_id)
                REFERENCES usuarios(id)
        )
    """)
    # DETALLE DE VENTAS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            descuento REAL DEFAULT 0,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id)
                REFERENCES ventas(id),
            FOREIGN KEY (producto_id)
                REFERENCES productos(id)
        )
    """)
    # ASISTENCIAS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_entrada TEXT,
            hora_salida TEXT,
            permiso_especial TEXT,
            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
        )
    """)
    # CORTES DE CAJA
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortes_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            total_dia REAL DEFAULT 0,
            total_recaudado REAL DEFAULT 0,
            diferencia REAL DEFAULT 0,
            FOREIGN KEY (empleado_id)
                REFERENCES empleados(id)
        )
    """)
    conexion.commit()
    conexion.close()
if __name__ == "__main__":
    crear_base_datos()
    print("Base de datos creada correctamente.")
