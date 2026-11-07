import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox
)

from database.database import conectar


class CorteCajaWindow(QWidget):

    def __init__(self, usuario=None):
        super().__init__()

        self.usuario = usuario

        self.total_ventas = 0.0
        self.ventas_efectivo = 0.0
        self.total_recaudado = 0.0
        self.diferencia = 0.0

        self.setWindowTitle("ABERCAS - Corte de Caja")
        self.setMinimumSize(900, 650)

        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)


        # TITULO
        titulo = QLabel("Corte de caja")
        titulo.setObjectName("tituloPrincipal")

        layout_principal.addWidget(titulo)

        subtitulo = QLabel(
            "Consulta y registra el corte de caja del día."
        )

        subtitulo.setObjectName("subtituloPrincipal")

        layout_principal.addWidget(subtitulo)

   
        # RESUMEN
        resumen_layout = QHBoxLayout()

        self.total_ventas_label = QLabel(
            "Ventas del día: $0.00"
        )

        self.ventas_efectivo_label = QLabel(
            "Ventas en efectivo: $0.00"
        )

        self.total_recaudado_label = QLabel(
            "Efectivo contado: $0.00"
        )

        self.diferencia_label = QLabel(
            "Diferencia: $0.00"
        )

        for etiqueta in [
            self.total_ventas_label,
            self.ventas_efectivo_label,
            self.total_recaudado_label,
            self.diferencia_label
        ]:

            etiqueta.setObjectName("cardValue")
            etiqueta.setAlignment(Qt.AlignCenter)

            resumen_layout.addWidget(etiqueta)

        layout_principal.addLayout(resumen_layout)


        # DENOMINACIONES
        titulo_denominaciones = QLabel(
            "Conteo de efectivo"
        )

        titulo_denominaciones.setObjectName("cardTitle")

        layout_principal.addWidget(titulo_denominaciones)

        self.tabla_denominaciones = QTableWidget()

        self.tabla_denominaciones.setColumnCount(3)

        self.tabla_denominaciones.setHorizontalHeaderLabels([
            "Denominación",
            "Cantidad",
            "Total"
        ])

        self.tabla_denominaciones.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        denominaciones = [
            1, 2, 5, 10, 20,
            50, 100, 200, 500, 1000
        ]

        self.tabla_denominaciones.setRowCount(
            len(denominaciones)
        )

        for fila, denominacion in enumerate(denominaciones):

            denominacion_item = QTableWidgetItem(
                f"${denominacion:.2f}"
            )

            denominacion_item.setTextAlignment(
                Qt.AlignCenter
            )

            denominacion_item.setFlags(
                denominacion_item.flags() &
                ~Qt.ItemIsEditable
            )

            self.tabla_denominaciones.setItem(
                fila, 0, denominacion_item
            )

            cantidad_item = QTableWidgetItem("0")

            cantidad_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.tabla_denominaciones.setItem(
                fila, 1, cantidad_item
            )

            total_item = QTableWidgetItem("$0.00")

            total_item.setTextAlignment(
                Qt.AlignCenter
            )

            total_item.setFlags(
                total_item.flags() &
                ~Qt.ItemIsEditable
            )

            self.tabla_denominaciones.setItem(
                fila, 2, total_item
            )

        layout_principal.addWidget(
            self.tabla_denominaciones
        )


        # BOTONES
        botones_layout = QHBoxLayout()

        boton_calcular = QPushButton(
            "Calcular efectivo"
        )

        boton_calcular.clicked.connect(
            self.calcular_efectivo
        )

        boton_guardar = QPushButton(
            "Guardar corte"
        )

        boton_guardar.clicked.connect(
            self.guardar_corte
        )

        boton_historial = QPushButton(
            "Historial de cortes"
        )

        boton_historial.clicked.connect(
            self.abrir_historial
        )
        botones_layout.addWidget(boton_calcular)
        botones_layout.addWidget(boton_guardar)
        botones_layout.addWidget(boton_historial)

        layout_principal.addLayout(botones_layout)


    # CARGAR DATOS
    def cargar_datos(self):

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM ventas
            WHERE fecha = date('now', 'localtime')
            AND estatus = 'Completada'
        """)

        self.total_ventas = float(
            cursor.fetchone()[0] or 0
        )

        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM ventas
            WHERE fecha = date('now', 'localtime')
            AND estatus = 'Completada'
            AND metodo_pago = 'Efectivo'
        """)

        self.ventas_efectivo = float(
            cursor.fetchone()[0] or 0
        )

        conexion.close()

        self.total_ventas_label.setText(
            f"Ventas del día: ${self.total_ventas:.2f}"
        )

        self.ventas_efectivo_label.setText(
            f"Ventas en efectivo: ${self.ventas_efectivo:.2f}"
        )


    # CALCULAR EFECTIVO
    def calcular_efectivo(self):

        total_efectivo = 0

        for fila in range(
            self.tabla_denominaciones.rowCount()
        ):

            denominacion_texto = (
                self.tabla_denominaciones
                .item(fila, 0).text()
            )

            cantidad_item = (
                self.tabla_denominaciones
                .item(fila, 1)
            )

            try:

                denominacion = float(
                    denominacion_texto.replace("$", "")
                )

                cantidad = int(
                    cantidad_item.text().strip()
                )

                if cantidad < 0:
                    raise ValueError

            except (ValueError, AttributeError):

                QMessageBox.warning(
                    self,
                    "Cantidad inválida",
                    "Las cantidades deben ser números "
                    "enteros mayores o iguales a cero."
                )

                return False

            total = denominacion * cantidad

            total_efectivo += total

            total_item = QTableWidgetItem(
                f"${total:.2f}"
            )

            total_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.tabla_denominaciones.setItem(
                fila, 2, total_item
            )

        self.total_recaudado = total_efectivo

        self.diferencia = (
            self.total_recaudado - self.ventas_efectivo
        )

        self.total_recaudado_label.setText(
            f"Efectivo contado: ${self.total_recaudado:.2f}"
        )

        self.diferencia_label.setText(
            f"Diferencia: ${self.diferencia:.2f}"
        )

        return True




    def abrir_historial(self):
        from views.historial_cortes import HistorialCortesWindow
        self.ventana_historial = HistorialCortesWindow()
        self.ventana_historial.show()


    # GUARDAR CORTE
    def guardar_corte(self):

        if not self.calcular_efectivo():
            return

        conexion = conectar()
        cursor = conexion.cursor()

        ahora = datetime.now()

        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")

        empleado_id = None

        if self.usuario:
            empleado_id = self.usuario.get("id")

        try:

            cursor.execute("""
                INSERT INTO cortes_caja (
                    empleado_id,
                    fecha,
                    hora,
                    total_dia,
                    total_recaudado,
                    diferencia
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                empleado_id,
                fecha,
                hora,
                self.total_ventas,
                self.total_recaudado,
                self.diferencia
            ))
            conexion.commit()
            QMessageBox.information(
                self,
                "Corte guardado",
                "El corte de caja se guardó correctamente."
            )
        except Exception as error:
            conexion.rollback()
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar el corte:\n{error}"
            )
        finally:
            conexion.close()
# EJECUTAR VENTANA PARA PRUEBAS
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CorteCajaWindow()
    ventana.show()
    sys.exit(app.exec())
