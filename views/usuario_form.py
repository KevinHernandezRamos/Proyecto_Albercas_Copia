import sys
from pathlib import Path
from PySide6.QtCore import Qt


from PySide6.QtWidgets import(
    QApplication,
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QHBoxLayout,
    QMessageBox
)

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.database import conectar


class UsuarioForm(QDialog):

    def __init__(self, usuario_id=None, parent=None):
        super().__init__(parent)

        self.usuario_id = usuario_id

        if usuario_id:
            self.setWindowTitle("ABERCAS - Editar usuario")
        else:
            self.setWindowTitle("ABERCAS - Nuevo usuario")

        self.setMinimumWidth(500)

        self.crear_interfaz()

        if self.usuario_id:
            self.cargar_usuario()

    # ==========================================
    # INTERFAZ
    # ==========================================

    def crear_interfaz(self):

        layout_principal = QVBoxLayout()

        formulario = QFormLayout()

        # Código

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText(
            "Ejemplo: USR-001"
        )

        formulario.addRow(
            "Código:",
            self.codigo
        )

        # Nombre

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText(
            "Nombre completo"
        )

        formulario.addRow(
            "Nombre:",
            self.nombre
        )

        # Dirección

        self.direccion = QLineEdit()

        formulario.addRow(
            "Dirección:",
            self.direccion
        )

        # Teléfono

        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText(
            "Teléfono"
        )

        formulario.addRow(
            "Teléfono:",
            self.telefono
        )

        # Teléfono emergencia

        self.telefono_emergencia = QLineEdit()

        formulario.addRow(
            "Tel. emergencia:",
            self.telefono_emergencia
        )

        # Descuento

        self.descuento = QDoubleSpinBox()

        self.descuento.setRange(
            0,
            100
        )

        self.descuento.setDecimals(
            2
        )

        self.descuento.setSuffix(
            " %"
        )

        formulario.addRow(
            "Descuento:",
            self.descuento
        )

        # Fecha ingreso

        self.fecha_ingreso = QLineEdit()

        self.fecha_ingreso.setPlaceholderText(
            "YYYY-MM-DD"
        )

        formulario.addRow(
            "Fecha de ingreso:",
            self.fecha_ingreso
        )

        # Género

        self.genero = QComboBox()

        self.genero.addItems([
            "",
            "Masculino",
            "Femenino",
            "Otro"
        ])

        formulario.addRow(
            "Género:",
            self.genero
        )

        # Estatus

        self.estatus = QComboBox()

        self.estatus.addItems([
            "Activo",
            "Inactivo"
        ])

        formulario.addRow(
            "Estatus:",
            self.estatus
        )

        # Instructor

        self.instructor = QLineEdit()

        formulario.addRow(
            "Instructor:",
            self.instructor
        )

        # Nivel

        self.nivel_nado = QComboBox()

        self.nivel_nado.addItems([
            "",
            "Principiante",
            "Intermedio",
            "Avanzado"
        ])

        formulario.addRow(
            "Nivel de nado:",
            self.nivel_nado
        )

        # Hora asistencia

        self.hora_asistencia = QLineEdit()

        self.hora_asistencia.setPlaceholderText(
            "Ejemplo: 08:00"
        )

        formulario.addRow(
            "Hora asistencia:",
            self.hora_asistencia
        )

        # Fecha final

        self.fecha_fin_registro = QLineEdit()

        self.fecha_fin_registro.setPlaceholderText(
            "YYYY-MM-DD"
        )

        formulario.addRow(
            "Fecha fin registro:",
            self.fecha_fin_registro
        )

        layout_principal.addLayout(
            formulario
        )

        # ==========================================
        # BOTONES
        # ==========================================

        botones = QHBoxLayout()

        botones.addStretch()

        boton_cancelar = QPushButton(
            "Cancelar"
        )

        boton_cancelar.clicked.connect(
            self.reject
        )

        boton_guardar = QPushButton(
            "Guardar"
        )

        boton_guardar.clicked.connect(
            self.guardar
        )

        botones.addWidget(
            boton_cancelar
        )

        botones.addWidget(
            boton_guardar
        )

        layout_principal.addLayout(
            botones
        )

        self.setLayout(
            layout_principal
        )

    # ==========================================
    # CARGAR USUARIO PARA EDITAR
    # ==========================================

    def cargar_usuario(self):

        conexion = conectar()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id = ?
            """,
            (self.usuario_id,)
        )

        usuario = cursor.fetchone()

        conexion.close()

        if usuario is None:

            QMessageBox.warning(
                self,
                "Error",
                "No se encontró el usuario."
            )

            self.reject()

            return

        self.codigo.setText(
            usuario["codigo"] or ""
        )

        self.nombre.setText(
            usuario["nombre"] or ""
        )

        self.direccion.setText(
            usuario["direccion"] or ""
        )

        self.telefono.setText(
            usuario["telefono"] or ""
        )

        self.telefono_emergencia.setText(
            usuario["telefono_emergencia"] or ""
        )

        self.descuento.setValue(
            float(usuario["descuento"] or 0)
        )

        self.fecha_ingreso.setText(
            usuario["fecha_ingreso"] or ""
        )

        self.seleccionar_combo(
            self.genero,
            usuario["genero"]
        )

        self.seleccionar_combo(
            self.estatus,
            usuario["estatus"]
        )

        self.instructor.setText(
            usuario["instructor"] or ""
        )

        self.seleccionar_combo(
            self.nivel_nado,
            usuario["nivel_nado"]
        )

        self.hora_asistencia.setText(
            usuario["hora_asistencia"] or ""
        )

        self.fecha_fin_registro.setText(
            usuario["fecha_fin_registro"] or ""
        )

    # ==========================================
    # SELECCIONAR OPCIÓN COMBO
    # ==========================================

    def seleccionar_combo(self, combo, valor):

        if not valor:
            combo.setCurrentIndex(0)
            return

        indice = combo.findText(
            str(valor),
            Qt.MatchFixedString
        )

        if indice >= 0:
            combo.setCurrentIndex(indice)

    # ==========================================
    # GUARDAR
    # ==========================================

    def guardar(self):

        codigo = self.codigo.text().strip()

        nombre = self.nombre.text().strip()

        if not codigo:

            QMessageBox.warning(
                self,
                "Dato faltante",
                "El código es obligatorio."
            )

            self.codigo.setFocus()

            return

        if not nombre:

            QMessageBox.warning(
                self,
                "Dato faltante",
                "El nombre es obligatorio."
            )

            self.nombre.setFocus()

            return

        conexion = conectar()

        cursor = conexion.cursor()

        try:

            if self.usuario_id:

                # ==================================
                # ACTUALIZAR
                # ==================================

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET
                        codigo = ?,
                        nombre = ?,
                        direccion = ?,
                        telefono = ?,
                        telefono_emergencia = ?,
                        descuento = ?,
                        fecha_ingreso = ?,
                        genero = ?,
                        estatus = ?,
                        instructor = ?,
                        nivel_nado = ?,
                        hora_asistencia = ?,
                        fecha_fin_registro = ?
                    WHERE id = ?
                    """,
                    (
                        codigo,
                        nombre,
                        self.direccion.text().strip(),
                        self.telefono.text().strip(),
                        self.telefono_emergencia.text().strip(),
                        self.descuento.value(),
                        self.fecha_ingreso.text().strip(),
                        self.genero.currentText(),
                        self.estatus.currentText(),
                        self.instructor.text().strip(),
                        self.nivel_nado.currentText(),
                        self.hora_asistencia.text().strip(),
                        self.fecha_fin_registro.text().strip(),
                        self.usuario_id
                    )
                )

            else:

                # ==================================
                # INSERTAR
                # ==================================

                cursor.execute(
                    """
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
                    """,
                    (
                        codigo,
                        nombre,
                        self.direccion.text().strip(),
                        self.telefono.text().strip(),
                        self.telefono_emergencia.text().strip(),
                        self.descuento.value(),
                        self.fecha_ingreso.text().strip(),
                        self.genero.currentText(),
                        self.estatus.currentText(),
                        self.instructor.text().strip(),
                        self.nivel_nado.currentText(),
                        self.hora_asistencia.text().strip(),
                        self.fecha_fin_registro.text().strip()
                    )
                )

            conexion.commit()

            QMessageBox.information(
                self,
                "Correcto",
                "Usuario guardado correctamente."
            )

            self.accept()

        except Exception as error:

            conexion.rollback()

            QMessageBox.critical(
                self,
                "Error",
                f"No fue posible guardar el usuario.\n\n{error}"
            )

        finally:

            conexion.close()


# ==========================================
# PRUEBA
# ==========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    ventana = UsuarioForm()

    ventana.show()

    sys.exit(
        app.exec()
    )