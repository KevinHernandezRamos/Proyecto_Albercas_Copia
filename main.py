import sys
from pathlib import Path
from views.usuarios import UsuariosWindow

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame
)
from PySide6.QtCore import Qt, QTimer

from views.login import LoginWindow
from database.database import conectar
BASE_DIR = Path(__file__).resolve().parent
class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("ABERCAS - Sistema de Administración")
        self.setMinimumSize(1100, 700)
        self.crear_interfaz()
        #temporizador para actualizar el dashboard
        self.timer_dashboard = QTimer(self)
        self.timer_dashboard.timeout.connect(self.actualizar_dashboard)
        self.timer_dashboard.start(30000)


    def obtener_datos_dashboard(self):
        conexion = conectar()
        cursor = conexion.cursor()

        # Ventas realizadas hoy
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM ventas
            WHERE fecha = date('now', 'localtime')
        """)
        ventas_hoy = cursor.fetchone()[0]

        # Total de usuarios
        cursor.execute("""
            SELECT COUNT(*)
            FROM usuarios
        """)
        usuarios = cursor.fetchone()[0]

        #   Asistencias registradas hoy
        cursor.execute("""
            SELECT COUNT(*)
            FROM asistencias
            WHERE fecha = date('now', 'localtime')
        """)
        asistencias = cursor.fetchone()[0]


        # Salidas registradas hoy
        cursor.execute("""
            SELECT COUNT(*)
            FROM asistencias
            WHERE fecha = date('now', 'localtime')
            AND hora_salida IS NOT NULL
            """)
        salidas_hoy = cursor.fetchone()[0]


        # Personas que actualmente están dentro
        cursor.execute("""
            SELECT COUNT(*)
            FROM asistencias
            WHERE fecha = date('now', 'localtime')
            AND hora_salida IS NULL
        """)
        personas_dentro = cursor.fetchone()[0]

        # Total de productos
        cursor.execute("""
            SELECT COUNT(*)
            FROM productos
            WHERE activo = 1
        """)
        productos = cursor.fetchone()[0]
        # Usuarios que tienen instructor
        cursor.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE instructor IS NOT NULL
            AND instructor != ''
        """)
        personas_con_instructor = cursor.fetchone()[0]
        

        cursor.execute("""
                    SELECT nivel_nado, COUNT(*)
                    FROM usuarios
                    WHERE nivel_nado IS NOT NULL
                    AND nivel_nado != ''
                    GROUP BY nivel_nado
                    ORDER BY nivel_nado
                    """)
        niveles = cursor.fetchall()



        #entradas agrupadas por hora
        cursor.execute("""
            SELECT
                substr(hora_entrada, 1,2) AS hora,
                COUNT(*)
            FROM asistencias
            WHERE  fecha = date('now', 'localtime')
            AND hora_entrada IS NOT NULL
            GROUP BY hora
            ORDER BY hora
            """)
        entradas_por_hora = cursor.fetchall()


        #Recibos generados hoy
        cursor.execute("""
            SELECT COUNT(*)
            FROM ventas
            WHERE fecha = date('now', 'localtime')
            AND estatus = 'Completada'
            """)
        recibos_hoy = cursor.fetchone()[0]



        conexion.close()
        return(
            ventas_hoy,
            usuarios,
            asistencias,
            salidas_hoy,
            productos,
            personas_dentro,
            personas_con_instructor,
            niveles,
            entradas_por_hora,
            recibos_hoy
        )
    
        



    def crear_interfaz(self):
        contenedor = QWidget()
        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)



        # ==========================================
        # BARRA LATERAL
        # ==========================================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(8)


        # Logo / nombre
        logo = QLabel("ABERCAS")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)

        subtitulo = QLabel("Sistema de administración")
        subtitulo.setObjectName("sidebarSubtitle")
        subtitulo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(subtitulo)
        sidebar_layout.addSpacing(20)

        # ==========================================
        # BOTONES DEL MENÚ
        # ==========================================

        botones = [
            "Inicio",
            "Usuarios",
            "Punto de venta",
            "Historial",
            "Asistencia",
            "Corte de caja",
            "Dashboard",
            "Configuración"
]

        for nombre in botones:
            boton = QPushButton(nombre)
            boton.setObjectName("menuButton")
            boton.setMinimumHeight(42)
            if nombre == "Usuarios":
                boton.clicked.connect(self.abrir_usuarios)
            elif nombre == "Punto de venta":
                boton.clicked.connect(self.abrir_punto_venta)
            elif nombre == "Historial":
                boton.clicked.connect(self.abrir_historial)
            elif nombre == "Asistencia":
                boton.clicked.connect(self.abrir_asistencia)
            elif nombre == "Corte de caja":
                boton.clicked.connect(self.abrir_corte_caja)
            sidebar_layout.addWidget(boton)
        # Usuario actual
        usuario_label = QLabel(
            f"{self.usuario['nombre']}\n"
            f"Rol: {self.usuario['rol']}"
        )
        usuario_label.setObjectName("usuarioActual")
        usuario_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(usuario_label)
        boton_cerrar = QPushButton("Cerrar sesión")
        boton_cerrar.setObjectName("logoutButton")
        boton_cerrar.clicked.connect(self.cerrar_sesion)
        sidebar_layout.addWidget(boton_cerrar)
        # ==========================================
        # CONTENIDO PRINCIPAL
        # ==========================================
        contenido = QWidget()
        contenido_layout = QVBoxLayout(contenido)
        contenido_layout.setContentsMargins(30, 30, 30, 30)
        contenido_layout.setSpacing(20)
        # Encabezado
        encabezado = QLabel(
            f"Bienvenido, {self.usuario['nombre']}"
        )
        encabezado.setObjectName("tituloPrincipal")
        contenido_layout.addWidget(encabezado)
        subtitulo_contenido = QLabel(
            f"Rol: {self.usuario['rol']}   |   "
            f"Turno: {self.usuario['turno'] or 'No especificado'}"
        )
        subtitulo_contenido.setObjectName("subtituloPrincipal")
        contenido_layout.addWidget(subtitulo_contenido)



        boton_actualizar = QPushButton("Actualizar")
        boton_actualizar.setObjectName("menuButton")
        boton_actualizar.clicked.connect(self.actualizar_dashboard)

        contenido_layout.addWidget(boton_actualizar)







        # ==========================================
        # TARJETAS
        # ==========================================
        self.tarjetas_layout = QGridLayout()
        self.tarjetas_layout.setHorizontalSpacing(15)
        self.tarjetas_layout.setVerticalSpacing(15)
        (
            ventas_hoy,
            usuarios,
            asistencias,
            salidas_hoy,
            productos,
            personas_dentro,
            personas_con_instructor,
            niveles,
            entradas_por_hora,
            recibos_hoy
        ) = self.obtener_datos_dashboard()



        tarjetas = [
            ("Ventas del día", f"${ventas_hoy:.2f}"),
            ("Usuarios", str(usuarios)),
            ("Asistencias", str(asistencias)),
            ("Personas dentro", str(personas_dentro)),
            ("Con instructor", str(personas_con_instructor)),
            ("Productos", str(productos)),
            ("Recibos de hoy", str(recibos_hoy))
        ]

        for i, (titulo, valor) in enumerate(tarjetas):

            tarjeta = QFrame()
            tarjeta.setObjectName("card")

            tarjeta_layout = QVBoxLayout(tarjeta)

            titulo_label = QLabel(titulo)
            titulo_label.setObjectName("cardTitle")
            titulo_label.setAlignment(Qt.AlignCenter)

            valor_label = QLabel(valor)
            valor_label.setObjectName("cardValue")
            valor_label.setAlignment(Qt.AlignCenter)

            tarjeta_layout.addWidget(titulo_label)
            tarjeta_layout.addWidget(valor_label)

            fila = i // 4
            columna = i % 4

            self.tarjetas_layout.addWidget(
                tarjeta,
                fila,
                columna
            )
        contenido_layout.addLayout(self.tarjetas_layout)


        # ==========================================
        # RESUMEN DE ASISTENCIA
        # ==========================================

        asistencia_card = QFrame()
        asistencia_card.setObjectName("card")

        asistencia_layout = QVBoxLayout(asistencia_card)

        asistencia_titulo = QLabel("Resumen de asistencia")
        asistencia_titulo.setObjectName("cardTitle")
        asistencia_layout.addWidget(asistencia_titulo)

        resumen_layout = QHBoxLayout()

        self.entrada_label = QLabel(
            f"Entradas hoy \n {asistencias}"
        )
        self.entrada_label.setAlignment(Qt.AlignCenter)



        self.salida_label = QLabel(
            f"Salidas hoy \n {salidas_hoy}"
        )
        self.salida_label.setAlignment(Qt.AlignCenter)



        self.dentro_label = QLabel(
            f"Personas dentro \n {personas_dentro}"
        )
        self.dentro_label.setAlignment(Qt.AlignCenter)

        resumen_layout.addWidget(self.entrada_label)
        resumen_layout.addWidget(self.salida_label)
        resumen_layout.addWidget(self.dentro_label)

        asistencia_layout.addLayout(resumen_layout)

        contenido_layout.addWidget(asistencia_card)




        # ==========================================
        # NIVELES DE NATACION
        # ==========================================

        niveles_card = QFrame()
        niveles_card.setObjectName("card")

        niveles_card_layout = QVBoxLayout(niveles_card)

        niveles_titulo = QLabel("Usuarios por nivel de natación")
        niveles_titulo.setObjectName("cardTitle")
        niveles_card_layout.addWidget(niveles_titulo)
        self.niveles_layout = QVBoxLayout()
        niveles_card_layout.addLayout(self.niveles_layout)
        contenido_layout.addWidget(niveles_card)
        self.mostrar_niveles(niveles)


        # ========================================
        # ENTRADAS POR HORA
        # ========================================

        horas_card = QFrame()
        horas_card.setObjectName("card")

        horas_card_layout = QVBoxLayout(horas_card)
        horas_titulo = QLabel("Entradas de hoy por hora")
        horas_titulo.setObjectName("cardTitle")

        horas_card_layout.addWidget(horas_titulo)

        self.horas_layout = QVBoxLayout()
        horas_card_layout.addLayout(self.horas_layout)

        contenido_layout.addWidget(horas_card)

        self.mostrar_entradas_por_hora(entradas_por_hora)


        # ==========================================
        # MENSAJE DE BIENVENIDA
        # ==========================================

        bienvenida = QFrame()
        bienvenida.setObjectName("welcomeCard")
        bienvenida_layout = QVBoxLayout(bienvenida)
        titulo_bienvenida = QLabel(
            "Sistema ABERCAS"
        )
        titulo_bienvenida.setObjectName("welcomeTitle")
        texto_bienvenida = QLabel(
            "El sistema está conectado correctamente "
            "con la base de datos."
        )
        texto_bienvenida.setObjectName("welcomeText")
        bienvenida_layout.addWidget(titulo_bienvenida)
        bienvenida_layout.addWidget(texto_bienvenida)
        contenido_layout.addWidget(bienvenida)
        contenido_layout.addStretch()
        # ==========================================
        # AGREGAR TODOS
        # ==========================================
        layout_principal.addWidget(sidebar)
        layout_principal.addWidget(contenido)

        self.setCentralWidget(contenedor)
    def actualizar_dashboard(self):
        #obtener todos los datos de la bd
        (
            ventas_hoy,
            usuarios,
            asistencias,
            salidas_hoy,
            productos,
            personas_dentro,
            personas_con_instructor,
            niveles,
            entradas_por_hora,
            recibos_hoy
        ) = self.obtener_datos_dashboard()


        self.entrada_label.setText(
            f"Entradas hoy \n {asistencias}"
        )
        self.salida_label.setText(
            f"Salidas hoy \n {salidas_hoy}"
        )
        self.dentro_label.setText(
            f"Personas dentro \n {personas_dentro}"
        )

        self.mostrar_niveles(niveles)
        self.mostrar_entradas_por_hora(entradas_por_hora)

        #eliminamos todas las tarjetas anteriores
        while self.tarjetas_layout.count():
            elemento = self.tarjetas_layout.takeAt(0)

            if elemento.widget():
                elemento.widget().deleteLater()

        #creamos las tarjetas ya actualizadas hasta el momento

        tarjetas = [
            ("Ventas del dia", f"${ventas_hoy:.2f}"),
            ("Usuarios", str(usuarios)),
            ("Asistencias", str(asistencias)),
            ("Personas dentro", str(personas_dentro)),
            ("Personas con instructor", str(personas_con_instructor)),
            ("Productos", str(productos)),
            ("Recibos de hoy", str(recibos_hoy))
        ]




        for titulo, valor in tarjetas:
            tarjeta = QFrame()
            tarjeta.setObjectName("card")

            tarjeta_layout = QVBoxLayout(tarjeta)

            titulo_label = QLabel(titulo)
            titulo_label.setObjectName("cardTitle")
            titulo_label.setAlignment(Qt.AlignCenter)

            valor_label = QLabel(valor)
            valor_label.setObjectName("cardValue")
            valor_label.setAlignment(Qt.AlignCenter)

            tarjeta_layout.addWidget(titulo_label)
            tarjeta_layout.addWidget(valor_label)

            i = self.tarjetas_layout.count()
            fila = i // 4
            columna = i % 4

            self.tarjetas_layout.addWidget(
                tarjeta,
                fila,
                columna
            )


        
    def mostrar_niveles(self,niveles):
        #eliminar los datos anteriores 
        while self.niveles_layout.count():
            elemento = self.niveles_layout.takeAt(0)

            if elemento.widget():
                elemento.widget().deleteLater()

        for nivel in niveles:
            nombre_nivel = nivel[0]
            cantidad = nivel[1]

            etiqueta = QLabel(
                f"{nombre_nivel}: {cantidad}"
            )

            self.niveles_layout.addWidget(etiqueta)

    def mostrar_entradas_por_hora(self, entradas_por_hora):
        #eliminar datos anteriores 
        while self.horas_layout.count():
            elemento = self.horas_layout.takeAt(0)

            if elemento.widget():
                elemento.widget().deleteLater()

        #mostrar las entradas que existen
        for registro in entradas_por_hora:
            hora = registro[0]
            cantidad = registro[1]

            etiqueta = QLabel(
                f"{hora}:00 - {cantidad} personas"
            )

            self.horas_layout.addWidget(etiqueta)


    def abrir_usuarios(self):
        self.ventana_usuarios = UsuariosWindow()
        self.ventana_usuarios.show()


    def abrir_punto_venta(self):
        from views.punto_venta import PuntoVentaWindow
        self.ventana_punto_venta = PuntoVentaWindow(
            self.usuario
        )
        self.ventana_punto_venta.show()


    def abrir_historial(self):
            from views.historial_ventas import HistorialVentasWindow
            self.ventana_historial = HistorialVentasWindow()
            self.ventana_historial.show()

    def abrir_asistencia(self):
        from views.asistencia import AsistenciaWindow
        self.ventana_asistencia = AsistenciaWindow()
        self.ventana_asistencia.show()

    def abrir_corte_caja(self):
        from views.corte_caja import CorteCajaWindow
        self.ventana_corte = CorteCajaWindow(self.usuario)
        self.ventana_corte.show()
    

    def cerrar_sesion(self):
        self.close()
        self.login = LoginWindow()
        self.login.login_exitoso.connect(
            iniciar_aplicacion
        )

        self.login.show()


def iniciar_aplicacion(usuario):
    ventana = MainWindow(usuario)
    ventana.show()
    ventanas.append(ventana)


ventanas = []


def main():

    app = QApplication(sys.argv)

    # Cargar estilos
    archivo_estilos = BASE_DIR / "assets" / "style.qss"

    if archivo_estilos.exists():

        with open(
            archivo_estilos,
            "r",
            encoding="utf-8"
        ) as archivo:

            app.setStyleSheet(
                archivo.read()
            )

    login = LoginWindow()
    login.login_exitoso.connect(
        iniciar_aplicacion
    )

    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()