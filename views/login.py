import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

from PySide6.QtCore import Qt, Signal


# ==========================================
# RUTA PRINCIPAL DEL PROYECTO
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from database.database import conectar


# ==========================================
# VENTANA DE LOGIN
# ==========================================

class LoginWindow(QWidget):

    login_exitoso = Signal(dict)

    def __init__(self):
        super().__init__()
        self.usuario_actual = None
        self.setWindowTitle(
            "ABERCAS - Inicio de sesión"
        )
        self.setFixedSize(420, 500)
        self.crear_interfaz()

    # ======================================
    # INTERFAZ
    # ======================================

    def crear_interfaz(self):

        layout = QVBoxLayout()

        layout.setContentsMargins(
            50,
            40,
            50,
            40
        )

        layout.setSpacing(15)

        # Título

        titulo = QLabel("ABERCAS")

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setObjectName(
            "titulo"
        )

        # Subtítulo

        subtitulo = QLabel(
            "Sistema de administración"
        )

        subtitulo.setAlignment(
            Qt.AlignCenter
        )

        subtitulo.setObjectName(
            "subtitulo"
        )

        # Usuario

        etiqueta_usuario = QLabel(
            "Usuario"
        )

        self.usuario_input = QLineEdit()

        self.usuario_input.setPlaceholderText(
            "Ingresa tu usuario"
        )

        # Contraseña

        etiqueta_password = QLabel(
            "Contraseña"
        )

        self.password_input = QLineEdit()

        self.password_input.setPlaceholderText(
            "Ingresa tu contraseña"
        )

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        # Botón

        boton = QPushButton(
            "INGRESAR"
        )

        boton.setObjectName(
            "botonLogin"
        )

        boton.clicked.connect(
            self.iniciar_sesion
        )

        self.password_input.returnPressed.connect(
            self.iniciar_sesion
        )

        # Agregar elementos

        layout.addStretch()

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            subtitulo
        )

        layout.addSpacing(20)

        layout.addWidget(
            etiqueta_usuario
        )

        layout.addWidget(
            self.usuario_input
        )

        layout.addWidget(
            etiqueta_password
        )

        layout.addWidget(
            self.password_input
        )

        layout.addSpacing(15)

        layout.addWidget(
            boton
        )

        layout.addStretch()

        self.setLayout(
            layout
        )

    # ======================================
    # INICIAR SESIÓN
    # ======================================

    def iniciar_sesion(self):

        usuario = self.usuario_input.text().strip()

        password = self.password_input.text()

        # Validar campos vacíos

        if not usuario or not password:

            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Ingresa tu usuario y contraseña."
            )

            return

        # Conectar a SQLite

        conexion = conectar()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                id,
                usuario,
                password,
                nombre,
                rol,
                turno,
                alberca,
                activo
            FROM empleados
            WHERE usuario = ?
            """,
            (usuario,)
        )

        empleado = cursor.fetchone()

        conexion.close()

        # Usuario inexistente

        if empleado is None:

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "El usuario no existe."
            )

            return

        # Usuario inactivo

        if empleado["activo"] != 1:

            QMessageBox.warning(
                self,
                "Usuario inactivo",
                "Este usuario se encuentra desactivado."
            )

            return

        # Contraseña incorrecta

        if empleado["password"] != password:

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "La contraseña es incorrecta."
            )

            return

        # ==================================
        # LOGIN CORRECTO
        # ==================================

        self.usuario_actual = {

            "id": empleado["id"],

            "usuario": empleado["usuario"],

            "nombre": empleado["nombre"],

            "rol": empleado["rol"],

            "turno": empleado["turno"],

            "alberca": empleado["alberca"]

        }

        QMessageBox.information(
            self,
            "Bienvenido",
            f"Bienvenido, {empleado['nombre']}."
        )

        # Avisar a main.py que el login fue exitoso

        self.login_exitoso.emit(
            self.usuario_actual
        )

        # Cerrar ventana de login

        self.close()


# ==========================================
# PRUEBA DIRECTA
# ==========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    ventana = LoginWindow()

    ventana.show()

    sys.exit(
        app.exec()
    )