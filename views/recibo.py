from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import(
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generar_recibo(venta, detalles, ruta_archivo):
    documento = SimpleDocTemplate(
        ruta_archivo,
        pagesize = letter,
        rightMargin = 15 * mm,
        leftMargin = 15 * mm,
        topMargin = 15 * mm,
        bottomMargin = 15 * mm
    )

    estilos = getSampleStyleSheet()
    elementos = []

    #
    #       ENCABEZADO DEL REPORTE
    #
    titulo = Paragraph(
    "<b>ALBERCA OLÍMPICA 450</b>",
    estilos["Title"]
)

    elementos.append(titulo)

    elementos.append(
    Paragraph(
        "RECIBO PROFESIONAL DE INGRESOS",
        estilos["Heading2"]
    )
)
    elementos.append(Spacer(1, 8))

    #
    #      DATOS DE LA VENTA *AL MOMENTO, FALTA COMPLETARLA*
    #


    datos_venta = [
        ["Folio:", venta["folio"]],
        ["Fecha:", venta["fecha"]],
        ["Hora:", venta["hora"]],
        ["Cajero:", venta["cajero"]],
        ["Metodo de pago:", venta["metodo_pago"]],
        ["Estatus:", venta["estatus"]],
    ]

    tabla_datos = Table(
        datos_venta,
        colWidths=[40 * mm, 110 * mm]
    )

    tabla_datos.setStyle(
        TableStyle([
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME", (1,0), (1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])
    )

    elementos.append(tabla_datos)
    elementos.append(Spacer(1,10))

    #
    #   PRODUCTOS ACTUALES 
    #

    elementos.append(
        Paragraph(
            "<b>DETALLE DE LA VENTA</b>",
            estilos["Heading3"]
        )
    )

    elementos.append(Spacer(1,5))

    datos_productos = [
        [
            "Codigo",
            "Productos",
            "Cantidad",
            "Precio",
            "Subtotal"
        ]
    ]


    for detalle in detalles:
        datos_productos.append([
            detalle["codigo"],
            detalle["nombre"],
            str(detalle["cantidad"]),
            f"${detalle['precio_unitario']:.2f}",
            f"${detalle['subtotal']:.2f}"
        ])

    tabla_productos = Table(
        datos_productos,
        colWidths=[
            25 * mm,
            65 * mm,
            20 * mm,
            25 * mm,
            25 * mm
        ]   
    )

    tabla_productos.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0,0),
                (-1,0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0,1),
                (-1,-1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0,0),
                (-1,-1),
                8
            ),
            (
                "GRID",
                (0,0),
                (-1,-1),
                0.5,
                colors.grey
            ),
            (
                "ALIGN",
                (2,1),
                (-1,-1),
                "RIGHT"
            ),
            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE"
            ),
            (
                "BOTTOMPADDING",
                (0,0),
                (-1,-1),
                5
            ),
            (
                "TOPPADDING",
                (0,0),
                (-1,-1),
                5
            ),
        ])
    )

    elementos.append(tabla_productos)
    elementos.append(Spacer(1,12))



    #
    #   TOTALES DE PAGO Y COSTO
    #

    datos_totales = [
        ["Subtotal:", f"${venta['subtotal']:.2f}"],
        ["Descuento:", f"${venta['descuento']:.2f}"],
        ["Total", f"${venta['total']:.2f}"],
    ]


    tabla_totales = Table(
        datos_totales,
        colWidths=[120 * mm, 40 * mm],
        hAlign="RIGHT"
    )

    tabla_totales.setStyle(
        TableStyle([
            (
                "FONTNAME",
                (0,0),
                (-1,1),
                "Helvetica"
            ),
            (
                "FONTNAME",
                (0,2),
                (-1,2),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0,0),
                (-1,-1),
                10
            ),
            (
                "ALIGN",
                (1,0),
                (1,-1),
                "RIGHT"
            ),
            (
                "LINEABOVE",
                (0,2),
                (-1,2),
                1,
                colors.black
            ),
            (
                "TOPPADDING",
                (0,0),
                (-1,-1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0,0),
                (-1,-1),
                5
            ),
        ])
    )

    elementos.append(tabla_totales)
    elementos.append(Spacer(1,20))

    elementos.append(
        Paragraph(
            "Este documento es un comprobante generado por el sistema.",
            estilos["Normal"]
        )
    )
    documento.build(elementos)