
import os
import subprocess

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog
)

from database.database import conectar


class HistorialVentasWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "ABERCAS - Historial de Ventas"
        )

        self.resize(1000, 600)

        self.crear_interfaz()
        self.cargar_ventas()

    def crear_interfaz(self):

        layout = QVBoxLayout(self)


        # TÍTULO
        titulo = QLabel("Historial de ventas")
        titulo.setObjectName("tituloPrincipal")

        layout.addWidget(titulo)

        subtitulo = QLabel(
            "Consulta las ventas realizadas en el sistema."
        )

        subtitulo.setObjectName("subtituloPrincipal")

        layout.addWidget(subtitulo)

  
        # BUSCADOR
        filtros = QHBoxLayout()

        self.busqueda = QLineEdit()

        self.busqueda.setPlaceholderText(
            "Buscar por folio, cajero o método de pago..."
        )

        boton_buscar = QPushButton("Buscar")

        boton_buscar.clicked.connect(
            self.cargar_ventas
        )

        boton_actualizar = QPushButton("Actualizar")

        boton_actualizar.clicked.connect(
            self.cargar_ventas
        )

        boton_detalle = QPushButton("Ver detalle")
        boton_detalle.clicked.connect(
        self.ver_detalle
        )

        boton_recibo = QPushButton("Generar recibo")

        boton_recibo.clicked.connect(
        self.generar_recibo
        )

        filtros.addWidget(self.busqueda)
        filtros.addWidget(boton_buscar)
        filtros.addWidget(boton_actualizar)
        filtros.addWidget(boton_detalle)
        filtros.addWidget(boton_recibo)
        layout.addLayout(filtros)
        # RESUMEN
        resumen = QHBoxLayout()
        self.label_total_ventas = QLabel(
            "Ventas encontradas: 0"
        )
        self.label_total_recaudado = QLabel(
            "Total recaudado: $0.00"
        )
        resumen.addWidget(
            self.label_total_ventas
        )
        resumen.addWidget(
            self.label_total_recaudado
        )
        layout.addLayout(resumen)
        # TABLA
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Folio",
            "Fecha",
            "Hora",
            "Cajero",
            "Total",
            "Método de pago",
            "Estatus"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )
        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        layout.addWidget(self.tabla)

   
    # CARGAR VENTAS
    def cargar_ventas(self):
        texto = self.busqueda.text().strip()
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            consulta = """
                SELECT
                    v.id,
                    v.folio,
                    v.fecha,
                    v.hora,
                    COALESCE(e.nombre, 'Sin cajero'),
                    v.total,
                    v.metodo_pago,
                    v.estatus
                FROM ventas v
                LEFT JOIN empleados e
                    ON v.empleado_id = e.id
            """
            parametros = []
            if texto:
                consulta += """
                    WHERE
                        v.folio LIKE ?
                        OR e.nombre LIKE ?
                        OR v.metodo_pago LIKE ?
                """
                buscar = f"%{texto}%"
                parametros = [
                    buscar,
                    buscar,
                    buscar
                ]
            consulta += """
                ORDER BY
                    v.id DESC
            """
            cursor.execute(
                consulta,
                parametros
            )
            ventas = cursor.fetchall()
            self.tabla.setRowCount(0)
            # CALCULAR RESUMEN
            total_ventas = len(ventas)
            total_recaudado = sum(
                venta["total"] or 0
                for venta in ventas
            )
            self.label_total_ventas.setText(
                f"Ventas encontradas: {total_ventas}"
            )
            self.label_total_recaudado.setText(
                f"Total recaudado: ${total_recaudado:.2f}"
            )
            for fila, venta in enumerate(ventas):
                self.tabla.insertRow(fila)
                self.tabla.setItem(
                    fila,
                    0,
                    QTableWidgetItem(
                        venta["folio"]
                    )
                )
                self.tabla.setItem(
                    fila,
                    1,
                    QTableWidgetItem(
                        venta["fecha"]
                    )
                )
                self.tabla.setItem(
                    fila,
                    2,
                    QTableWidgetItem(
                        venta["hora"]
                    )
                )
                self.tabla.setItem(
                    fila,
                    3,
                    QTableWidgetItem(
                        venta[4]
                    )
                )
                self.tabla.setItem(
                    fila,
                    4,
                    QTableWidgetItem(
                    f"${venta['total']:.2f}"
                    )
                )
                self.tabla.setItem(
                    fila,
                    5,
                    QTableWidgetItem(
                        venta["metodo_pago"]
                    )
                )
                self.tabla.setItem(
                    fila,
                    6,
                    QTableWidgetItem(
                        venta["estatus"]
                    )
                )
                    # Guardar el ID de la venta en la fila
                self.tabla.item(
                    fila,
                    0
                    ).setData(
                    Qt.UserRole,
                    venta["id"]
                )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el historial:\n\n{error}"
            )
        finally:
            conexion.close()

    # VER DETALLE DE VENTA
    def ver_detalle(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "Venta no seleccionada",
                "Selecciona una venta de la tabla."
            )
            return

        item = self.tabla.item(
            fila,
            0
        )
        venta_id = item.data(
            Qt.UserRole
        )
        if venta_id is None:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo obtener la venta seleccionada."
            )
            return
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    v.folio,
                    v.fecha,
                    v.hora,
                    COALESCE(e.nombre, 'Sin cajero') AS cajero,
                    v.subtotal,
                    v.descuento,
                    v.total,
                    v.metodo_pago,
                    v.estatus
                FROM ventas v
                LEFT JOIN empleados e
                    ON v.empleado_id = e.id
                WHERE v.id = ?
            """, (venta_id,))
            venta = cursor.fetchone()
            if venta is None:
                QMessageBox.warning(
                    self,
                    "Venta no encontrada",
                    "La venta seleccionada no existe."
                )
                return
            cursor.execute("""
                SELECT
                    p.codigo,
                    p.nombre,
                    dv.cantidad,
                    dv.precio_unitario,
                    dv.subtotal
                FROM detalle_ventas dv
                INNER JOIN productos p
                    ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
            """, (venta_id,))
            detalles = cursor.fetchall()
            mensaje = (
                f"Folio: {venta['folio']}\n"
                f"Fecha: {venta['fecha']}\n"
                f"Hora: {venta['hora']}\n"
                f"Cajero: {venta['cajero']}\n"
                f"Método de pago: {venta['metodo_pago']}\n"
                f"Estatus: {venta['estatus']}\n\n"
                f"PRODUCTOS\n"
                f"------------------------------\n"
            )
            for detalle in detalles:
                mensaje += (
                    f"{detalle['nombre']}\n"
                    f"  Cantidad: {detalle['cantidad']}\n"
                    f"  Precio: ${detalle['precio_unitario']:.2f}\n"
                    f"  Subtotal: ${detalle['subtotal']:.2f}\n\n"
                )
            mensaje += (
                "------------------------------\n"
                f"Subtotal: ${venta['subtotal']:.2f}\n"
                f"Descuento: ${venta['descuento']:.2f}\n"
                f"TOTAL: ${venta['total']:.2f}"
            )
            QMessageBox.information(
                self,
                "Detalle de venta",
                mensaje
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo consultar el detalle:\n\n{error}"
            )
    # GENERAR RECIBO
    def generar_recibo(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(
                self,
                "Venta no seleccionada",
                "Selecciona una venta de la tabla."
            )
            return
        item = self.tabla.item(
            fila,
            0
        )
        venta_id = item.data(
            Qt.UserRole
        )
        if venta_id is None:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo obtener el ID de la venta."
            )
            return
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar recibo",
            f"Recibo_{item.text()}.pdf",
            "Archivos PDF (*.pdf)"
        )
        if not ruta_archivo:
            return
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            # INFORMACIÓN DE LA VENTA
            cursor.execute("""
                SELECT
                    v.folio,
                    v.fecha,
                    v.hora,
                    COALESCE(e.nombre, 'Sin cajero') AS cajero,
                    v.subtotal,
                    v.descuento,
                    v.total,
                    v.metodo_pago,
                    v.estatus
                FROM ventas v
                LEFT JOIN empleados e
                    ON v.empleado_id = e.id
                WHERE v.id = ?
            """, (venta_id,))
            venta = cursor.fetchone()
            if venta is None:
                QMessageBox.warning(
                    self,
                    "Venta no encontrada",
                    "No se encontró la venta seleccionada."
                )
                return
            # PRODUCTOS DE LA VENTA
            cursor.execute("""
                SELECT
                    p.codigo,
                    p.nombre,
                    dv.cantidad,
                    dv.precio_unitario,
                    dv.subtotal
                FROM detalle_ventas dv
                INNER JOIN productos p
                    ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
            """, (venta_id,))
            detalles = cursor.fetchall()
            # GENERAR PDF
            from views.recibo import generar_recibo
            generar_recibo(venta, detalles, ruta_archivo)
            QMessageBox.information(
                self,
                "Recibo Generado",
                f"El recibo se genero correctamente.\n\n"
                f"Archivo:\n{ruta_archivo}"
            )
            try:
                os.startfile(ruta_archivo)
            except Exception as e:
                QMessageBox.warning(
                    "No se pudo abrir el recibo",
                    f"El PDF fue generado correctamente, pero no se pudo abrir automaticamente.\n\n"
                    f"Puedes abrirlo manualmente desde:\n{ruta_archivo}\n\n"
                    f"Error: {e}"
                )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo generar el recibo:\n\n{error}"
            )
        finally:

            conexion.close()
