from pathlib import Path
from openpyxl import load_workbook
from database import conectar


# Ubicación del archivo Excel
BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "Abercas.xlsm"


def importar_empleados(wb, conexion):
    hoja = wb["BD"]

    cursor = conexion.cursor()

    contador = 0

    for fila in hoja.iter_rows(min_row=2, values_only=True):

        usuario = fila[0]
        password = fila[1]
        rol = fila[2]
        nombre = fila[5]
        turno = fila[6]
        alberca = fila[7]

        if not usuario:
            continue

        # Evitar duplicados
        cursor.execute(
            "SELECT id FROM empleados WHERE usuario = ?",
            (str(usuario),)
        )

        existe = cursor.fetchone()

        if existe:
            continue

        cursor.execute("""
            INSERT INTO empleados
            (usuario, password, nombre, rol, turno, alberca, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            str(usuario),
            str(password) if password else "",
            str(nombre) if nombre else str(usuario),
            str(rol) if rol else "Cajero",
            str(turno) if turno else "",
            str(alberca) if alberca else ""
        ))

        contador += 1

    conexion.commit()

    print(f"Empleados importados: {contador}")


def importar_usuarios(wb, conexion):
    hoja = wb["Usuarios"]

    cursor = conexion.cursor()

    contador = 0

    for fila in hoja.iter_rows(min_row=2, values_only=True):

        codigo = fila[0]

        if not codigo:
            continue

        cursor.execute(
            "SELECT id FROM usuarios WHERE codigo = ?",
            (str(codigo),)
        )

        existe = cursor.fetchone()

        if existe:
            continue

        cursor.execute("""
            INSERT INTO usuarios (
                codigo,
                nombre,
                direccion,
                telefono,
                telefono_emergencia,
                descuento,
                fecha_ingreso,
                genero,
                estatus,
                instructor,
                nivel_nado,
                hora_asistencia,
                fecha_fin_registro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(codigo),
            str(fila[1]) if fila[1] else "",
            str(fila[2]) if fila[2] else "",
            str(fila[3]) if fila[3] else "",
            str(fila[4]) if fila[4] else "",
            float(fila[5]) if isinstance(fila[5], (int, float)) else 0,
            str(fila[6]) if fila[6] else "",
            str(fila[7]) if fila[7] else "",
            str(fila[8]) if fila[8] else "",
            str(fila[9]) if fila[9] else "",
            str(fila[10]) if fila[10] else "",
            str(fila[11]) if fila[11] else "",
            str(fila[12]) if fila[12] else ""
        ))

        contador += 1

    conexion.commit()

    print(f"Usuarios importados: {contador}")


def importar_productos(wb, conexion):
    hoja = wb["PuntoDeVenta"]

    cursor = conexion.cursor()

    contador = 0

    for fila in hoja.iter_rows(min_row=2, values_only=True):

        codigo = fila[0]

        if not codigo:
            continue

        cursor.execute(
            "SELECT id FROM productos WHERE codigo = ?",
            (str(codigo),)
        )

        existe = cursor.fetchone()

        if existe:
            continue

        def numero(valor):
            if isinstance(valor, (int, float)):
                return float(valor)
            return 0

        cursor.execute("""
            INSERT INTO productos (
                codigo,
                nombre,
                tipo,
                unidad,
                costo_unitario,
                iva,
                precio_final,
                existencia,
                ventas,
                fecha_ingreso,
                descripcion,
                observaciones,
                activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            str(codigo),
            str(fila[1]) if fila[1] else "",
            str(fila[2]) if fila[2] else "",
            str(fila[3]) if fila[3] else "",
            numero(fila[4]),
            numero(fila[5]),
            numero(fila[6]),
            int(fila[7]) if isinstance(fila[7], (int, float)) else 0,
            int(fila[8]) if isinstance(fila[8], (int, float)) else 0,
            str(fila[9]) if fila[9] else "",
            str(fila[10]) if fila[10] else "",
            str(fila[11]) if fila[11] else ""
        ))

        contador += 1

    conexion.commit()

    print(f"Productos importados: {contador}")


def main():

    print("====================================")
    print("     IMPORTACIÓN DE ABERCAS")
    print("====================================")

    if not EXCEL_PATH.exists():
        print()
        print("ERROR: No se encontró Abercas.xlsm")
        print(f"Ruta buscada: {EXCEL_PATH}")
        return

    print("Excel encontrado.")
    print("Cargando información...")

    wb = load_workbook(
        EXCEL_PATH,
        data_only=True,
        read_only=True
    )

    conexion = conectar()

    try:

        importar_empleados(wb, conexion)
        importar_usuarios(wb, conexion)
        importar_productos(wb, conexion)

        print()
        print("====================================")
        print("IMPORTACIÓN TERMINADA CORRECTAMENTE")
        print("====================================")

    except Exception as e:

        conexion.rollback()

        print()
        print("ERROR DURANTE LA IMPORTACIÓN:")
        print(e)

    finally:

        conexion.close()
        wb.close()


if __name__ == "__main__":
    main()