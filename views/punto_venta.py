import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
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
    QDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
)


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from database.database import conectar



class PagoDialog(QDialog):

    def __init__(self, total, parent=None):
        super().__init__(parent)

        self.total = total
        self.metodo_pago = None
        self.dinero_recibido = 0
        self.cambio = 0

        self.setWindowTitle("Cobrar venta")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Total
        total_label = QLabel(
            f"Total a pagar: ${self.total:.2f}"
        )

        total_label.setObjectName("totalPago")

        layout.addWidget(total_label)

        # Método de pago
        formulario = QFormLayout()

        self.metodo_combo = QComboBox()

        self.metodo_combo.addItems([
            "Efectivo",
            "Tarjeta",
            "Transferencia"
        ])

        formulario.addRow(
            "Método de pago:",
            self.metodo_combo
        )

        layout.addLayout(formulario)

        # Dinero recibido
        self.recibido_spin = QDoubleSpinBox()

        self.recibido_spin.setDecimals(2)
        self.recibido_spin.setMaximum(999999.99)
        self.recibido_spin.setPrefix("$ ")

        formulario.addRow(
            "Dinero recibido:",
            self.recibido_spin
        )

        # Cambio
        self.cambio_label = QLabel(
            "Cambio: $0.00"
        )

        layout.addWidget(self.cambio_label)

        # Botones
        botones = QHBoxLayout()

        boton_cancelar = QPushButton("Cancelar")
        boton_confirmar = QPushButton("Confirmar pago")

        botones.addWidget(boton_cancelar)
        botones.addWidget(boton_confirmar)

        layout.addLayout(botones)

        # Eventos
        self.metodo_combo.currentTextChanged.connect(
            self.cambiar_metodo
        )

        self.recibido_spin.valueChanged.connect(
            self.calcular_cambio
        )

        boton_cancelar.clicked.connect(
            self.reject
        )

        boton_confirmar.clicked.connect(
            self.confirmar_pago
        )

        self.cambiar_metodo(
            self.metodo_combo.currentText()
        )

    def cambiar_metodo(self, metodo):

        if metodo == "Efectivo":

            self.recibido_spin.setEnabled(True)

            self.calcular_cambio()

        else:

            self.recibido_spin.setValue(0)
            self.recibido_spin.setEnabled(False)

            self.cambio_label.setText(
                "Cambio: $0.00"
            )

    def calcular_cambio(self):
        recibido = self.recibido_spin.value()
        diferencia = recibido - self.total
        if diferencia < 0:
            faltante = abs(diferencia)
            self.cambio_label.setText(
            f"Falta: ${faltante:.2f}"
        )
        else:
            self.cambio_label.setText(
            f"Cambio: ${diferencia:.2f}"
        )


    def confirmar_pago(self):

            metodo = self.metodo_combo.currentText()
            # EFECTIVO
            if metodo == "Efectivo":

                recibido = self.recibido_spin.value()

                if recibido < self.total:

                    QMessageBox.warning(
                        self,
                        "Pago insuficiente",
                        f"El pago recibido es insuficiente.\n\n"
                        f"Total: ${self.total:.2f}\n"
                        f"Recibido: ${recibido:.2f}\n"
                        f"Falta: ${(self.total - recibido):.2f}"
                    )

                    return

                self.dinero_recibido = recibido
                self.cambio = recibido - self.total
        # TARJETA / TRANSFERENCIA
            else:
                self.dinero_recibido = self.total
                self.cambio = 0
        # GUARDAR MÉTODO DE PAGO
            self.metodo_pago = metodo
            self.accept()

class PuntoVentaWindow(QWidget):
    def __init__(self, usuario=None):
            super().__init__()
            self.usuario = usuario
            self.setWindowTitle(
            "ABERCAS - Punto de Venta"
        )
            self.setMinimumSize(
            1100,
            650
        )
            self.carrito = []
            self.crear_interfaz()
            self.cargar_productos()
    # CREAR INTERFAZ
    def crear_interfaz(self):

        layout_principal = QVBoxLayout()

        layout_principal.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout_principal.setSpacing(15)
        # ENCABEZADO
        titulo = QLabel(
            "Punto de Venta"
        )
        titulo.setObjectName(
            "tituloPrincipal"
        )
        subtitulo = QLabel(
            "Venta de productos y servicios"
        )
        subtitulo.setObjectName(
            "subtituloPrincipal"
        )
        layout_principal.addWidget(
            titulo
        )
        layout_principal.addWidget(
            subtitulo
        )
        # BÚSQUEDA
        barra_busqueda = QHBoxLayout()
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText(
            "Buscar producto por código o nombre..."
        )
        boton_buscar = QPushButton(
            "Buscar"
        )
        boton_buscar.clicked.connect(
            self.buscar_productos
        )
        self.buscar_input.textChanged.connect(
            self.buscar_productos
        )
        barra_busqueda.addWidget(
            self.buscar_input
        )
        barra_busqueda.addWidget(
            boton_buscar
        )
        layout_principal.addLayout(
            barra_busqueda
        )
        # TABLA DE PRODUCTOS
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(
            5
        )
        self.tabla_productos.setHorizontalHeaderLabels([
            "Código",
            "Producto",
            "Tipo",
            "Precio",
            "Existencia"
        ])
        self.tabla_productos.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.tabla_productos.setSelectionMode(
            QTableWidget.SingleSelection
        )
        self.tabla_productos.setEditTriggers(
            QTableWidget.NoEditTriggers
        )
        self.tabla_productos.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.tabla_productos.doubleClicked.connect(
            self.agregar_al_carrito
        )
        layout_principal.addWidget(
            self.tabla_productos
        ) 
        # BOTONES
        botones = QHBoxLayout()
        boton_agregar = QPushButton(
            "Agregar al carrito"
        )
        boton_agregar.clicked.connect(
            self.agregar_al_carrito
        )
        boton_limpiar = QPushButton(
            "Limpiar carrito"
        )
        boton_limpiar.clicked.connect(
            self.limpiar_carrito
        )
        boton_cobrar = QPushButton(
            "Cobrar venta"
        )
        boton_cobrar.clicked.connect(
            self.cobrar_venta
        )

        botones.addWidget(
            boton_agregar
        )

        botones.addWidget(
            boton_limpiar
        )

        botones.addWidget(
            boton_cobrar
        )

        botones.addStretch()

        layout_principal.addLayout(
            botones
        )

        # CARRITO
        carrito_titulo = QLabel(
            "Carrito de compra"
        )

        carrito_titulo.setObjectName(
            "subtituloPrincipal"
        )

        layout_principal.addWidget(
            carrito_titulo
        )

        self.tabla_carrito = QTableWidget()

        self.tabla_carrito.setColumnCount(
            5
        )

        self.tabla_carrito.setHorizontalHeaderLabels([
            "Código",
            "Producto",
            "Cantidad",
            "Precio",
            "Subtotal"
        ])

        self.tabla_carrito.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.tabla_carrito.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout_principal.addWidget(
            self.tabla_carrito
        )
        # TOTAL
        total_layout = QHBoxLayout()

        total_layout.addStretch()

        self.total_label = QLabel(
            "TOTAL: $0.00"
        )

        self.total_label.setObjectName(
            "cardValue"
        )

        total_layout.addWidget(
            self.total_label
        )

        layout_principal.addLayout(
            total_layout
        )


        self.setLayout(
            layout_principal
        )



    # CARGAR PRODUCTOS
    def cargar_productos(self):
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                tipo,
                precio_final,
                existencia
            FROM productos
            WHERE activo = 1
            ORDER BY nombre ASC
        """)
        self.productos = cursor.fetchall()
        conexion.close()
        self.mostrar_productos(
            self.productos
        )

    # MOSTRAR PRODUCTOS
    def mostrar_productos(self, productos):
        self.tabla_productos.setRowCount(
            0
        )
        for producto in productos:
            fila = self.tabla_productos.rowCount()
            self.tabla_productos.insertRow(
                fila
            )
            datos = [
                producto["codigo"],
                producto["nombre"],
                producto["tipo"],
                f"${producto['precio_final']:.2f}",
                producto["existencia"]
            ]
            for columna, dato in enumerate(datos):

                item = QTableWidgetItem(
                    str(dato)
                )
                self.tabla_productos.setItem(
                    fila,
                    columna,
                    item
                )
            self.tabla_productos.item(
                fila,
                0
            ).setData(
                256,
                producto["id"]
            )
    # BUSCAR PRODUCTOS
 
    def buscar_productos(self):
        texto = (
            self.buscar_input
            .text()
            .strip()
            .lower()
        )
        if not texto:

            self.mostrar_productos(
                self.productos
            )

            return

        resultados = []

        for producto in self.productos:

            codigo = str(
                producto["codigo"] or ""
            ).lower()

            nombre = str(
                producto["nombre"] or ""
            ).lower()

            if (
                texto in codigo
                or texto in nombre
            ):

                resultados.append(
                    producto
                )

        self.mostrar_productos(
            resultados
        )
    # AGREGAR AL CARRITO
    def agregar_al_carrito(self):

        fila = self.tabla_productos.currentRow()

        if fila < 0:

            QMessageBox.warning(
                self,
                "Selecciona un producto",
                "Selecciona primero un producto."
            )

            return

        producto_id = self.tabla_productos.item(
            fila,
            0
        ).data(256)

        producto = None

        for p in self.productos:

            if p["id"] == producto_id:

                producto = p

                break

        if producto is None:

            return

        for item in self.carrito:

            if item["id"] == producto["id"]:

                if item["cantidad"] < producto["existencia"]:

                    item["cantidad"] += 1

                else:

                    QMessageBox.warning(
                        self,
                        "Existencia insuficiente",
                        "No hay más unidades disponibles."
                    )

                self.mostrar_carrito()

                return

        if producto["existencia"] <= 0:

            QMessageBox.warning(
                self,
                "Sin existencia",
                "Este producto no tiene existencia."
            )

            return

        self.carrito.append({
            "id": producto["id"],
            "codigo": producto["codigo"],
            "nombre": producto["nombre"],
            "cantidad": 1,
            "precio": producto["precio_final"]
        })

        self.mostrar_carrito()
    # MOSTRAR CARRITO
    def mostrar_carrito(self):
        self.tabla_carrito.setRowCount(
            0
        )
        total = 0
        for item_carrito in self.carrito:
            fila = self.tabla_carrito.rowCount()
            self.tabla_carrito.insertRow(
                fila
            )
            subtotal = (
                item_carrito["cantidad"]
                * item_carrito["precio"]
            )
            total += subtotal
            datos = [
                item_carrito["codigo"],
                item_carrito["nombre"],
                item_carrito["cantidad"],
                f"${item_carrito['precio']:.2f}",
                f"${subtotal:.2f}"
            ]
            for columna, dato in enumerate(datos):
                self.tabla_carrito.setItem(
                    fila,
                    columna,
                    QTableWidgetItem(
                        str(dato)
                    )
                )
        self.total_label.setText(
            f"TOTAL: ${total:.2f}"
        )






    # COBRAR VENTA
    def cobrar_venta(self):
        if not self.carrito:
            QMessageBox.warning(
                self,
                "Carrito vacío",
                "Agrega al menos un producto antes de cobrar."
            )
            return
        total = 0
        for item in self.carrito:
            subtotal = (
            item["cantidad"]
                * item["precio"]
    )
            total += subtotal
        dialogo_pago = PagoDialog(
            total,
            self
)
        resultado = dialogo_pago.exec()
        if resultado != QDialog.Accepted:
            return
        metodo_pago = dialogo_pago.metodo_pago
        dinero_recibido = dialogo_pago.dinero_recibido
        cambio = dialogo_pago.cambio
        respuesta = QMessageBox.question(
            self,
            "Confirmar venta",
            f"¿Confirmar venta por ${total:.2f}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return
        conexion = conectar()
        cursor = conexion.cursor()
        try:
            # GENERAR FOLIO
            cursor.execute("""
                SELECT COUNT(*) + 1
                FROM ventas
            """)
            numero = cursor.fetchone()[0]
            folio = f"V-{numero:06d}"
            # FECHA Y HORA
            from datetime import datetime
            ahora = datetime.now()
            fecha = ahora.strftime(
                "%Y-%m-%d"
            )
            hora = ahora.strftime(
                "%H:%M:%S"
            )
            # GUARDAR VENTA
            cursor.execute("""
                INSERT INTO ventas (
                    folio,
                    fecha,
                    hora,
                    empleado_id,
                    subtotal,
                    descuento,
                    total,
                    metodo_pago,
                    estatus
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                folio,
                fecha,
                hora,
                self.usuario["id"] if self.usuario else None,
                total,
                0,
                total,
                metodo_pago,
                "Completada"
            ))
            venta_id = cursor.lastrowid
            # GUARDAR DETALLES
            for item in self.carrito:
                subtotal = (
                    item["cantidad"]
                    * item["precio"]
                )
                cursor.execute("""
                    INSERT INTO detalle_ventas (
                        venta_id,
                        producto_id,
                        cantidad,
                        precio_unitario,
                        descuento,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    venta_id,
                    item["id"],
                    item["cantidad"],
                    item["precio"],
                    0,
                    subtotal
                ))
                # DESCONTAR INVENTARIO
                cursor.execute("""
                    UPDATE productos
                    SET existencia = existencia - ?,
                        ventas = ventas + ?
                    WHERE id = ?
                """, (
                    item["cantidad"],
                    item["cantidad"],
                    item["id"]
                ))


            conexion.commit()

        except Exception as error:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la venta:\n\n{error}"
            )

            conexion.close()

            return

        conexion.close()
        # FINALIZAR
        mensaje = (
        f"La venta se registró correctamente.\n\n"
        f"Folio: {folio}\n"
        f"Total: ${total:.2f}\n"
        f"Método de pago: {metodo_pago}"
)

        if metodo_pago == "Efectivo":
            mensaje += (
                f"\nDinero recibido: ${dinero_recibido:.2f}"
                f"\nCambio: ${cambio:.2f}"
        )
        QMessageBox.information(
            self,
            "Venta completada",
            mensaje
)


        self.carrito.clear()

        self.mostrar_carrito()

        self.cargar_productos()


    # LIMPIAR CARRITO
    def limpiar_carrito(self):
        self.carrito.clear()
        self.mostrar_carrito()
# PRUEBA DIRECTA
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PuntoVentaWindow()
    ventana.show()
    sys.exit(
        app.exec()
    )
