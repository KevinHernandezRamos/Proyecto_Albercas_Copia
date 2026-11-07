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
    QMessageBox,
    QHeaderView,
    QDialog,
)
from PySide6.QtCore import Qt
# RUTA DEL PROYECTO 
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from database.database import conectar
# VENTANA DE USUARIOS
class UsuariosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "ABERCAS - Usuarios"
        )
        self.setMinimumSize(
            1100,
            650
        )
        self.crear_interfaz()
        self.cargar_usuarios()

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
            "Usuarios"
        )
        titulo.setObjectName(
            "tituloPrincipal"
        )
        subtitulo = QLabel(
            "Administración de usuarios de la alberca"
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
        # BARRA DE HERRAMIENTAS
        barra = QHBoxLayout()
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText(
            "Buscar por código o nombre..."
        )
        self.buscar_input.textChanged.connect(
            self.buscar_usuarios
        )
        boton_actualizar = QPushButton(
            "Actualizar"
        )
        boton_actualizar.clicked.connect(
            self.cargar_usuarios
        )
        boton_nuevo = QPushButton(
            "Nuevo usuario"
        )
        boton_nuevo.clicked.connect(
            self.nuevo_usuario
        )
        barra.addWidget(
            self.buscar_input
        )
        barra.addWidget(
            boton_actualizar
        )
        barra.addWidget(
            boton_nuevo
        )
        layout_principal.addLayout(
            barra
        )
        # TABLA
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Código",
            "Nombre",
            "Teléfono",
            "Descuento",
            "Estatus",
            "Instructor",
            "Nivel",
            "Fecha fin"
        ])
        self.tabla.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.tabla.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.tabla.setEditTriggers(
            QTableWidget.NoEditTriggers
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabla.doubleClicked.connect(
            self.editar_usuario
        )

        layout_principal.addWidget(
            self.tabla
        )
        # BOTONES INFERIORES
        botones = QHBoxLayout()
        botones.addStretch()
        boton_editar = QPushButton(
            "Editar seleccionado"
        )

        boton_editar.clicked.connect(
            self.editar_usuario
        )
        boton_desactivar = QPushButton(
            "Desactivar"
        )
        boton_desactivar.clicked.connect(
            self.desactivar_usuario
        )
        botones.addWidget(
            boton_editar
        )
        botones.addWidget(
            boton_desactivar
        )
        layout_principal.addLayout(
            botones
        )
        self.setLayout(
            layout_principal
        )
    # CARGAR USUARIOS
    def cargar_usuarios(self):
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT
                id,
                codigo,
                nombre,
                telefono,
                descuento,
                estatus,
                instructor,
                nivel_nado,
                fecha_fin_registro
            FROM usuarios
            ORDER BY nombre ASC
        """)

        self.usuarios = cursor.fetchall()

        conexion.close()

        self.mostrar_usuarios(
            self.usuarios
        )

    # MOSTRAR USUARIOS
    def mostrar_usuarios(self, usuarios):
        self.tabla.setRowCount(0)
        for usuario in usuarios:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(
                fila
            )
            datos = [
                usuario["codigo"],
                usuario["nombre"],
                usuario["telefono"],
                f"{usuario['descuento']}%",
                usuario["estatus"],
                usuario["instructor"],
                usuario["nivel_nado"],
                usuario["fecha_fin_registro"]
            ]
            for columna, dato in enumerate(datos):

                item = QTableWidgetItem(
                    str(dato) if dato is not None else ""
                )
                self.tabla.setItem(
                    fila,
                    columna,
                    item
                )
            # Guardar ID del usuario
            self.tabla.item(
                fila,
                0
            ).setData(
                Qt.UserRole,
                usuario["id"]
            )
    # BUSCAR
    def buscar_usuarios(self):
        texto = self.buscar_input.text().strip().lower()
        if not texto:
            self.mostrar_usuarios(
                self.usuarios
            )
            return
        resultados = []
        for usuario in self.usuarios:
            codigo = str(
                usuario["codigo"] or ""
            ).lower()
            nombre = str(
                usuario["nombre"] or ""
            ).lower()
            if (
                texto in codigo
                or texto in nombre
            ):
                resultados.append(
                    usuario
                )
        self.mostrar_usuarios(
            resultados
        )
    # OBTENER SELECCIONADO
    def obtener_usuario_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        item = self.tabla.item(
            fila,
            0
        )
        if item is None:
            return None

        usuario_id = item.data(
            Qt.UserRole
        )
        return usuario_id
    # NUEVO USUARIO
    def nuevo_usuario(self):
        from views.usuario_form import UsuarioForm
        formulario = UsuarioForm(
            parent=self
        )
        resultado = formulario.exec()
        if resultado == QDialog.Accepted:
            self.cargar_usuarios()

    # EDITAR USUARIO
    def editar_usuario(self):
        usuario_id = self.obtener_usuario_seleccionado()
        if usuario_id is None:
            QMessageBox.warning(
                self,
                "Selecciona un usuario",
                "Selecciona primero un usuario de la tabla."
            )
            return
        from views.usuario_form import UsuarioForm
        formulario = UsuarioForm(
            usuario_id=usuario_id,
            parent=self
        )

        resultado = formulario.exec()

        if resultado == QDialog.Accepted:

            self.cargar_usuarios()
    # DESACTIVAR USUARIO
    def desactivar_usuario(self):
        usuario_id = (
            self.obtener_usuario_seleccionado()
        )
        if usuario_id is None:
            QMessageBox.warning(
                self,
                "Selecciona un usuario",
                "Selecciona primero un usuario."
            )
            return
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Deseas desactivar este usuario?"
        )
        if respuesta != QMessageBox.Yes:
            return
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET estatus = 'Inactivo'
            WHERE id = ?
        """, (usuario_id,))
        conexion.commit()
        conexion.close()
        self.cargar_usuarios()
        QMessageBox.information(
            self,
            "Usuario actualizado",
            "El usuario fue desactivado correctamente."
        )
# PRUEBA DIRECTA
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = UsuariosWindow()
    ventana.show()
    sys.exit(
        app.exec()
    )
