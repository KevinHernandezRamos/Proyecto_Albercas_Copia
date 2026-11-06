from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLineEdit
)

from database.database import conectar


class HistorialCortesWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ABERCAS - Historial de cortes")
        self.setMinimumSize(1050, 600)

        self.crear_interfaz()
        self.cargar_cortes()

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        # ==========================================
        # TITULO
        # ==========================================

        titulo = QLabel("Historial de cortes de caja")
        titulo.setObjectName("tituloPrincipal")

        layout_principal.addWidget(titulo)

        subtitulo = QLabel(
            "Consulta los cortes de caja registrados."
        )

        subtitulo.setObjectName("subtituloPrincipal")

        layout_principal.addWidget(subtitulo)

        # ==========================================
        # BUSQUEDA
        # ==========================================

        busqueda_layout = QHBoxLayout()

        self.buscar_input = QLineEdit()

        self.buscar_input.setPlaceholderText(
            "Buscar por empleado o fecha..."
        )

        boton_buscar = QPushButton("Buscar")

        boton_buscar.clicked.connect(
            self.buscar_cortes
        )

        boton_actualizar = QPushButton("Mostrar todo")

        boton_actualizar.clicked.connect(
            self.cargar_cortes
        )

        busqueda_layout.addWidget(self.buscar_input)
        busqueda_layout.addWidget(boton_buscar)
        busqueda_layout.addWidget(boton_actualizar)

        layout_principal.addLayout(busqueda_layout)

        # ==========================================
        # TABLA
        # ==========================================

        self.tabla_cortes = QTableWidget()

        self.tabla_cortes.setColumnCount(7)

        self.tabla_cortes.setHorizontalHeaderLabels([
            "ID",
            "Fecha",
            "Hora",
            "Empleado",
            "Ventas del día",
            "Efectivo contado",
            "Diferencia"
        ])

        self.tabla_cortes.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla_cortes.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla_cortes.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabla_cortes.setSelectionMode(
            QTableWidget.SingleSelection
        )

        layout_principal.addWidget(self.tabla_cortes)

        # ==========================================
        # RESUMEN
        # ==========================================

        self.total_cortes_label = QLabel(
            "Cortes registrados: 0"
        )

        self.total_cortes_label.setObjectName("cardTitle")

        layout_principal.addWidget(
            self.total_cortes_label
        )

    # ==========================================
    # CARGAR CORTES
    # ==========================================

    def cargar_cortes(self):

        self.buscar_input.clear()

        self.consultar_cortes("")

    # ==========================================
    # BUSCAR CORTES
    # ==========================================

    def buscar_cortes(self):

        texto = self.buscar_input.text().strip()

        self.consultar_cortes(texto)

    # ==========================================
    # CONSULTAR BASE DE DATOS
    # ==========================================

    def consultar_cortes(self, texto):

        conexion = conectar()
        cursor = conexion.cursor()

        try:

            cursor.execute("""
                SELECT
                    c.id,
                    c.fecha,
                    c.hora,
                    COALESCE(e.nombre, 'Sin empleado'),
                    c.total_dia,
                    c.total_recaudado,
                    c.diferencia
                FROM cortes_caja c
                LEFT JOIN empleados e
                    ON c.empleado_id = e.id
                WHERE
                    c.fecha LIKE ?
                    OR e.nombre LIKE ?
                ORDER BY c.id DESC
            """, (
                f"%{texto}%",
                f"%{texto}%"
            ))

            cortes = cursor.fetchall()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron consultar los cortes:\n{error}"
            )

            return

        finally:
            conexion.close()

        self.tabla_cortes.setRowCount(len(cortes))

        for fila, corte in enumerate(cortes):

            valores = [
                corte["id"],
                corte["fecha"],
                corte["hora"],
                corte["COALESCE(e.nombre, 'Sin empleado')"],
                f"${corte['total_dia']:.2f}",
                f"${corte['total_recaudado']:.2f}",
                f"${corte['diferencia']:.2f}"
            ]

            for columna, valor in enumerate(valores):

                item = QTableWidgetItem(str(valor))

                item.setTextAlignment(
                    Qt.AlignCenter
                )

                self.tabla_cortes.setItem(
                    fila,
                    columna,
                    item
                )

        self.total_cortes_label.setText(
            f"Cortes registrados: {len(cortes)}"
        )