from PySide6.QtCore import Qt, QDate
from datetime import datetime
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
    QDateEdit
)

from database.database import conectar


class AsistenciaWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asistencia")
        self.resize(1000, 650)

        self.crear_interfaz()
        self.cargar_asistencias()

    def crear_interfaz(self):

        layout_principal = QVBoxLayout(self)

        # ==============================
        # TÍTULO
        # ==============================

        titulo = QLabel("Control de Asistencia")
        titulo.setObjectName("title")

        subtitulo = QLabel(
            "Registro de entradas y salidas de usuarios"
        )
        subtitulo.setObjectName("subtitle")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)

        # ==============================
        # BÚSQUEDA
        # ==============================

        fila_busqueda = QHBoxLayout()

        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText(
            "Buscar por código o nombre..."
        )

        boton_buscar = QPushButton("Buscar")
        boton_buscar.clicked.connect(
            self.buscar_usuario
        )

        fila_busqueda.addWidget(self.busqueda)
        fila_busqueda.addWidget(boton_buscar)

        layout_principal.addLayout(fila_busqueda)

        # ==============================
        # DATOS DEL USUARIO
        # ==============================

        self.usuario_label = QLabel(
            "Usuario seleccionado: ninguno"
        )

        layout_principal.addWidget(
            self.usuario_label
        )

        self.personas_dentro_label = QLabel(
            "Personas dentro ahora: 0"
        )
        layout_principal.addWidget(
            self.personas_dentro_label
        )

        self.entradas_hoy_label = QLabel(
            "Entradas hoy: 0"
        )

        self.salidas_hoy_label = QLabel(
            "Salidas hoy: 0"
        )

        self.permisos_hoy_label = QLabel(
            "Permisos especiales hoy: 0"
        )

        layout_principal.addWidget(
            self.entradas_hoy_label
        )

        layout_principal.addWidget(
            self.salidas_hoy_label
        )

        layout_principal.addWidget(
            self.permisos_hoy_label
        )


        self.permiso = QLineEdit()
        self.permiso.setPlaceholderText(
            "Permiso especial (OPCIONAL)..."
        )
        layout_principal.addWidget(
            self.permiso
        )

        # ==============================
        # BOTONES
        # ==============================

        fila_botones = QHBoxLayout()

        self.boton_entrada = QPushButton(
            "Registrar entrada"
        )

        self.boton_salida = QPushButton(
            "Registrar salida"
        )

        self.boton_entrada.clicked.connect(
            self.registrar_entrada
        )

        self.boton_salida.clicked.connect(
            self.registrar_salida
        )

        fila_botones.addWidget(
            self.boton_entrada
        )

        fila_botones.addWidget(
            self.boton_salida
        )

        layout_principal.addLayout(
            fila_botones
        )
        # ==============================
        # FILTROS DEL HISTORIAL
        # ==============================

        fila_filtros = QHBoxLayout()

        self.filtro_historial = QLineEdit()

        self.filtro_historial.setPlaceholderText(
        "Filtrar por código o nombre..."
        )

        self.filtro_fecha = QDateEdit()

        self.filtro_fecha.setCalendarPopup(True)

        self.filtro_fecha.setDate(
            QDate.currentDate()
        )

        self.filtro_fecha.setDisplayFormat(
            "yyyy-MM-dd"
        )

        boton_filtrar = QPushButton("Filtrar")

        boton_filtrar.clicked.connect(
            self.filtrar_asistencias
        )

        boton_mostrar_todo = QPushButton("Mostrar todo")
        boton_dia = QPushButton("Consultar día")
        boton_dia.clicked.connect(
            self.consultar_dia
        )




        boton_mostrar_todo.clicked.connect(
            self.mostrar_todo
        )
        fila_filtros.addWidget(
            self.filtro_historial
        )
        fila_filtros.addWidget(
            self.filtro_fecha
        )
        fila_filtros.addWidget(
            boton_filtrar
        )
        fila_filtros.addWidget(
            boton_mostrar_todo
        )
        fila_filtros.addWidget(
            boton_dia
        )


        layout_principal.addLayout(
    fila_filtros
)

        # ==============================
        # TABLA
        # ==============================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(6)

        self.tabla.setHorizontalHeaderLabels([
            "Código",
            "Nombre",
            "Fecha",
            "Entrada",
            "Salida",
            "Permiso"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout_principal.addWidget(
            self.tabla
        )
        titulo_dentro = QLabel(
        "Personas dentro actualmente"
        )

        layout_principal.addWidget(
            titulo_dentro
        )

        self.tabla_dentro = QTableWidget()

        self.tabla_dentro.setColumnCount(3)

        self.tabla_dentro.setHorizontalHeaderLabels([
            "Código",
            "Nombre",
            "Hora de entrada"
        ])

        self.tabla_dentro.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout_principal.addWidget(
            self.tabla_dentro
        )
    def cargar_personas_dentro(self):

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                u.codigo,
                u.nombre,
                a.hora_entrada
            FROM asistencias a
            INNER JOIN usuarios u
                ON a.usuario_id = u.id
            WHERE a.hora_salida IS NULL
            ORDER BY a.hora_entrada
        """)

        personas = cursor.fetchall()

        conexion.close()

        self.tabla_dentro.setRowCount(0)

        for persona in personas:

            fila = self.tabla_dentro.rowCount()

            self.tabla_dentro.insertRow(fila)

            self.tabla_dentro.setItem(
                fila,
                0,
                QTableWidgetItem(
                    persona["codigo"]
                )
        )   

            self.tabla_dentro.setItem(
                fila,
                1,
                QTableWidgetItem(
                persona["nombre"]
            )
        )

        self.tabla_dentro.setItem(
            fila,
            2,
            QTableWidgetItem(
                persona["hora_entrada"]
            )
        )

    # ==========================================
    # CARGAR ASISTENCIAS
    # ==========================================

    def cargar_asistencias(self):

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                a.id,
                u.codigo,
                u.nombre,
                a.fecha,
                a.hora_entrada,
                a.hora_salida,
                a.permiso_especial
            FROM asistencias a
            INNER JOIN usuarios u
                ON a.usuario_id = u.id
            ORDER BY a.id DESC
        """)

        registros = cursor.fetchall()

        conexion.close()

        self.tabla.setRowCount(0)

        for registro in registros:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    registro["codigo"]
                )
            )
            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    registro["nombre"]
                )
            )

            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    registro["fecha"]
                )
            )

            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    registro["hora_entrada"] or ""
                )
            )

            self.tabla.setItem(
                fila,
                4,
                QTableWidgetItem(
                    registro["hora_salida"] or ""
                )
            )

            self.tabla.setItem(
                fila,
                5,
                QTableWidgetItem(
                    registro["permiso_especial"] or ""
                )
            )
        self.actualizar_personas_dentro()

    # ==========================================
    # BUSCAR USUARIO
    # ==========================================

    def buscar_usuario(self):

        texto = self.busqueda.text().strip()

        if not texto:
            QMessageBox.warning(
                self,
                "Búsqueda",
                "Escribe un código o nombre."
            )
            return

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT *
            FROM usuarios
            WHERE codigo = ?
               OR nombre LIKE ?
            LIMIT 1
        """, (
            texto,
            f"%{texto}%"
        ))

        usuario = cursor.fetchone()

        conexion.close()

        if not usuario:

            self.usuario_label.setText(
                "Usuario seleccionado: ninguno"
            )

            QMessageBox.warning(
                self,
                "Usuario no encontrado",
                "No se encontró ningún usuario."
            )

            return

        self.usuario_seleccionado = usuario

        self.usuario_label.setText(
            f"Usuario seleccionado: "
            f"{usuario['codigo']} - "
            f"{usuario['nombre']}"
        )

    # ==========================================
    # REGISTRAR ENTRADA
    # ==========================================

    def registrar_entrada(self):
        if not hasattr(self, "usuario_seleccionado"):
            QMessageBox.warning(
            self,
            "Entrada",
            "Primero debes buscar y seleccionar un usuario."
            )
            return

        usuario_id = self.usuario_seleccionado["id"]
        permiso = self.permiso.text().strip()
        ahora = datetime.now()

        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")

        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si ya tiene una entrada sin salida
        cursor.execute("""
            SELECT id
            FROM asistencias
            WHERE usuario_id = ?
            AND fecha = ?
            AND hora_salida IS NULL
            ORDER BY id DESC
            LIMIT 1
        """, (
            usuario_id,
            fecha
        ))

        asistencia_abierta = cursor.fetchone()

        if asistencia_abierta:

            conexion.close()

            QMessageBox.warning(
                self,
                "Entrada no permitida",
                "Este usuario ya tiene una entrada registrada "
                "y todavía no registra su salida."
            )   

            return

        # Registrar nueva entrada
        cursor.execute("""
            INSERT INTO asistencias (
                usuario_id,
                fecha,
                hora_entrada,
                hora_salida,
                permiso_especial
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            usuario_id,
            fecha,
            hora,
            None,
            permiso
        ))

        conexion.commit()
        conexion.close()

        QMessageBox.information(
            self,
            "Entrada registrada",
            f"Entrada registrada correctamente.\n\n"
            f"Usuario: {self.usuario_seleccionado['nombre']}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}"
        )

        self.cargar_asistencias()
        self.permiso.clear()
    # ==========================================
    # REGISTRAR SALIDA
    # ==========================================

    def registrar_salida(self):

        if not hasattr(self, "usuario_seleccionado"):
            QMessageBox.warning(
                self,
                "Salida",
                "Primero debes buscar y seleccionar un usuario."
            )
            return

        usuario_id = self.usuario_seleccionado["id"]

        ahora = datetime.now()

        fecha = ahora.strftime("%Y-%m-%d")
        hora = ahora.strftime("%H:%M:%S")

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id
            FROM asistencias
            WHERE usuario_id = ?
            AND fecha = ?
            AND hora_salida IS NULL
            ORDER BY id DESC
            LIMIT 1
        """, (
            usuario_id,
            fecha
        ))

        asistencia = cursor.fetchone()

        if not asistencia:

            conexion.close()

            QMessageBox.warning(
                self,
                "Salida no permitida",
                "Este usuario no tiene una entrada pendiente "
                "para registrar su salida."
            )

            return

        cursor.execute("""
            UPDATE asistencias
            SET hora_salida = ?
            WHERE id = ?
        """, (
            hora,
            asistencia["id"]
        ))

        conexion.commit()
        conexion.close()

        QMessageBox.information(
            self,
            "Salida registrada",
            f"Salida registrada correctamente.\n\n"
            f"Usuario: {self.usuario_seleccionado['nombre']}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}"
        )

        self.cargar_asistencias()

    def actualizar_personas_dentro(self):
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM asistencias
            WHERE hora_salida IS NULL
        """)
        resultado = cursor.fetchone()
        conexion.close()
        total = resultado["total"]


        self.personas_dentro_label.setText(
            f"Personas dentro ahora: {total}"
        )
        self.cargar_personas_dentro()
        self.actualizar_resumen_hoy()



    def filtrar_asistencias(self):
        texto = self.filtro_historial.text().strip()
        fecha = self.filtro_fecha.text().strip()
        conexion = conectar()
        cursor = conexion.cursor()
        consulta = """
            SELECT
                a.id,
                u.codigo,
                u.nombre,
                a.fecha,
                a.hora_entrada,
                a.hora_salida,
                a.permiso_especial
            FROM asistencias a
            INNER JOIN usuarios u
                ON a.usuario_id = u.id
            WHERE 1 = 1
        """

        parametros = []

        # Filtrar por código o nombre
        if texto:

            consulta += """
                AND (
                    u.codigo LIKE ?
                    OR u.nombre LIKE ?
                )
            """

            parametros.append(f"%{texto}%")
            parametros.append(f"%{texto}%")

        # Filtrar por fecha
        if fecha:

            consulta += """
                AND a.fecha = ?
            """

            parametros.append(fecha)

        consulta += """
            ORDER BY a.id DESC
        """

        cursor.execute(
            consulta,
            parametros
        )

        registros = cursor.fetchall()

        conexion.close()

        self.tabla.setRowCount(0)

        for registro in registros:

            fila = self.tabla.rowCount()

            self.tabla.insertRow(fila)

            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    registro["codigo"]
                )
            )

            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    registro["nombre"]
                )
            )

            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    registro["fecha"]
                )
            )

            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    registro["hora_entrada"] or ""
                )
            )

            self.tabla.setItem(
                fila,
                4,
                QTableWidgetItem(
                    registro["hora_salida"] or ""
                )
            )

            self.tabla.setItem(
                fila,
                5,
                QTableWidgetItem(
                    registro["permiso_especial"] or ""
                )
            )
    def mostrar_todo(self):
        self.filtro_historial.clear()
        self.filtro_fecha.clear()
        self.cargar_asistencias()


    def actualizar_resumen_hoy(self):
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d")
        conexion = conectar()
        cursor = conexion.cursor()
        # Total de entradas de hoy
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND hora_entrada IS NOT NULL
        """, (fecha,))
        entradas = cursor.fetchone()["total"]
        # Total de salidas de hoy
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND hora_salida IS NOT NULL
        """, (fecha,))
        salidas = cursor.fetchone()["total"]
        # Total de permisos especiales de hoy
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND permiso_especial IS NOT NULL
            AND permiso_especial != ''
        """, (fecha,))
        permisos = cursor.fetchone()["total"]
        conexion.close()
        self.entradas_hoy_label.setText(
            f"Entradas hoy: {entradas}"
        )
        self.salidas_hoy_label.setText(
            f"Salidas hoy: {salidas}"
        )
        self.permisos_hoy_label.setText(
            f"Permisos especiales hoy: {permisos}"
        )




    def consultar_dia(self):
        fecha = self.filtro_fecha.date().toString(
            "yyyy-MM-dd"
        )
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND hora_entrada IS NOT NULL
        """, (fecha,))
        entradas = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND hora_salida IS NOT NULL
        """, (fecha,))
        salidas = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND permiso_especial IS NOT NULL
            AND permiso_especial != ''
        """, (fecha,))
        permisos = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM asistencias
            WHERE fecha = ?
            AND hora_salida IS NULL
        """, (fecha,))
        dentro = cursor.fetchone()["total"]
        conexion.close()
        QMessageBox.information(
            self,
            "Asistencia del día",
            f"Fecha: {fecha}\n\n"
            f"Entradas: {entradas}\n"
            f"Salidas: {salidas}\n"
            f"Personas dentro: {dentro}\n"
            f"Permisos especiales: {permisos}"
        )
        self.filtro_fecha.setDate(
            QDate.fromString(
            fecha,
            "yyyy-MM-dd"
        )
    )
        self.filtrar_por_fecha(fecha)


    def filtrar_por_fecha(self, fecha):
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
        SELECT
            a.id,
            u.codigo,
            u.nombre,
            a.fecha,
            a.hora_entrada,
            a.hora_salida,
            a.permiso_especial
        FROM asistencias a
        INNER JOIN usuarios u
            ON a.usuario_id = u.id
        WHERE a.fecha = ?
        ORDER BY a.id DESC
        """, (fecha,))

        registros = cursor.fetchall()
        conexion.close()

        self.tabla.setRowCount(0)

        for registro in registros:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    registro["codigo"]
                )
            )
            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    registro["nombre"]
                )
            )
            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    registro["fecha"]
                )
            )
            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    registro["hora_entrada"] or  ""
                )
            )
            self.tabla.setItem(
                fila,
                4,
                QTableWidgetItem(
                    registro["hora_salida"] or ""
                )
            )
            self.tabla.setItem(
                fila,
                5,
                QTableWidgetItem(
                    registro["permiso_especial"] or ""
                )
            )