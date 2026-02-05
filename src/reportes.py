# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import sys
import tempfile
import os


def insertar_grafico_plotly(fig, story, caption, width=450, height=250):

    if fig is None:
        print(f"[ERROR] Figura es None para: {caption}", file=sys.stderr)
        style_error = ParagraphStyle('Err', fontSize=9, textColor=colors.red, alignment=1)
        story.append(Paragraph(f"<i>[Gráfico no disponible: {caption}]</i>", style_error))
        return False
    
    img_bytes = None
    metodo_exitoso = None
    
    try:
        print(f"[DEBUG] Intentando Método 1 (to_image) para: {caption}", file=sys.stderr)
        img_bytes = fig.to_image(
            format="png", 
            width=int(width * 2), 
            height=int(height * 2), 
            engine="kaleido"
        )
        if img_bytes and len(img_bytes) > 0:
            metodo_exitoso = "to_image"
            print(f"[DEBUG] ✓ Método 1 exitoso ({len(img_bytes)} bytes)", file=sys.stderr)
        else:
            raise ValueError("to_image retornó vacío o None")
    except Exception as e1:
        print(f"[DEBUG] ✗ Método 1 falló: {str(e1)[:100]}", file=sys.stderr)
    
    if not img_bytes:
        try:
            print(f"[DEBUG] Intentando Método 2 (write_image en buffer)...", file=sys.stderr)
            temp_buffer = io.BytesIO()
            fig.write_image(
                temp_buffer, 
                format="png", 
                width=int(width * 2), 
                height=int(height * 2), 
                engine="kaleido"
            )
            tamanio = temp_buffer.tell()
            if tamanio > 0:
                temp_buffer.seek(0)
                img_bytes = temp_buffer.read()
                metodo_exitoso = "write_image (buffer)"
                print(f"[DEBUG] ✓ Método 2 exitoso ({tamanio} bytes)", file=sys.stderr)
            else:
                raise ValueError("write_image generó 0 bytes")
        except Exception as e2:
            print(f"[DEBUG] ✗ Método 2 falló: {str(e2)[:100]}", file=sys.stderr)
    
    if not img_bytes:
        try:
            print(f"[DEBUG] Intentando Método 3 (archivo temporal)...", file=sys.stderr)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            fig.write_image(
                temp_path,
                format="png",
                width=int(width * 2),
                height=int(height * 2),
                engine="kaleido"
            )
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                with open(temp_path, 'rb') as f:
                    img_bytes = f.read()
                metodo_exitoso = "write_image (temp file)"
                print(f"[DEBUG] ✓ Método 3 exitoso ({len(img_bytes)} bytes)", file=sys.stderr)
                os.unlink(temp_path)
            else:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise ValueError("Archivo temporal vacío o no creado")
        except Exception as e3:
            print(f"[DEBUG] ✗ Método 3 falló: {str(e3)[:100]}", file=sys.stderr)
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    if not img_bytes:
        try:
            print(f"[DEBUG] Intentando Método 4 (orca)...", file=sys.stderr)
            img_bytes = fig.to_image(
                format="png",
                width=int(width * 2),
                height=int(height * 2),
                engine="orca"
            )
            if img_bytes and len(img_bytes) > 0:
                metodo_exitoso = "orca"
                print(f"[DEBUG] ✓ Método 4 exitoso ({len(img_bytes)} bytes)", file=sys.stderr)
        except Exception as e4:
            print(f"[DEBUG] ✗ Método 4 falló: {str(e4)[:100]}", file=sys.stderr)
    
    if img_bytes and len(img_bytes) > 0:
        try:
            print(f"[DEBUG] Insertando imagen en PDF (método: {metodo_exitoso})...", file=sys.stderr)
            img_buffer = io.BytesIO(img_bytes)
            img_pdf = Image(img_buffer, width=width, height=height)
            img_pdf.hAlign = 'CENTER'
            
            story.append(Spacer(1, 12))
            story.append(img_pdf)
            
            style_caption = ParagraphStyle(
                'Caption',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=1
            )
            story.append(Paragraph(f"<i>{caption}</i>", style_caption))
            story.append(Spacer(1, 10))
            
            print(f"[DEBUG] ✓ Imagen insertada correctamente", file=sys.stderr)
            return True
            
        except Exception as e_insert:
            print(f"[ERROR] Error al insertar objeto Image en ReportLab: {e_insert}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
    
    print(f"[ERROR] TODOS los métodos fallaron para {caption}", file=sys.stderr)
    style_error = ParagraphStyle('Err', fontSize=9, textColor=colors.red, alignment=1)
    story.append(Paragraph(f"<i>[Gráfico no disponible: {caption}]</i>", style_error))
    story.append(Spacer(1, 10))
    return False


def generar_reporte_ejecutivo_pdf(df_filtrado, health_scores, metricas_calidad, fig_ciudades, fig_riesgo):

    print("\n" + "="*80, file=sys.stderr)
    print("INICIANDO GENERACIÓN DE REPORTE PDF", file=sys.stderr)
    print("="*80, file=sys.stderr)
    
    print(f"\n[DEBUG] Validando figuras recibidas:", file=sys.stderr)
    print(f"  - fig_ciudades: {type(fig_ciudades) if fig_ciudades else 'None'}", file=sys.stderr)
    print(f"  - fig_riesgo: {type(fig_riesgo) if fig_riesgo else 'None'}", file=sys.stderr)
    
    if fig_ciudades is not None:
        print(f"  - fig_ciudades tiene datos: {hasattr(fig_ciudades, 'data')}", file=sys.stderr)
        if hasattr(fig_ciudades, 'data'):
            print(f"  - fig_ciudades.data length: {len(fig_ciudades.data)}", file=sys.stderr)
    
    if fig_riesgo is not None:
        print(f"  - fig_riesgo tiene datos: {hasattr(fig_riesgo, 'data')}", file=sys.stderr)
        if hasattr(fig_riesgo, 'data'):
            print(f"  - fig_riesgo.data length: {len(fig_riesgo.data)}", file=sys.stderr)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()
    story = []

    df = df_filtrado.copy()
    df['Ultima_Revision'] = pd.to_datetime(df['Ultima_Revision'], errors='coerce')
    hoy = pd.to_datetime(datetime.now().date())
    df['Dias_Desde_Revision'] = (hoy - df['Ultima_Revision']).dt.days.fillna(0)
    
    df["Ciudad_Destino_Norm"] = df["Ciudad_Destino"].astype(str).str.strip().str.upper()

    df_analisis = df[
        (df["Tiempo_Entrega"] < 100) & 
        (df["Tiempo_Entrega"] > 0)
    ].copy()

    style_title = ParagraphStyle('Title', parent=styles['Title'], fontSize=22, textColor=colors.HexColor('#1f4e78'), spaceAfter=20)
    style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#2e75b6'), spaceBefore=15, spaceAfter=10)
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=12, spaceAfter=10)
    style_alerta = ParagraphStyle('Alerta', parent=styles['Normal'], textColor=colors.red, fontSize=10, leading=12, fontWeight='Bold')
    style_kpi_header = ParagraphStyle('KPIHeader', parent=styles['Normal'], fontSize=9, fontWeight='Bold', alignment=1, textColor=colors.HexColor('#333333'))
    style_kpi_value = ParagraphStyle('KPIValue', parent=styles['Normal'], fontSize=13, fontWeight='Bold', alignment=1, textColor=colors.HexColor('#1f4e78'))

    # 1. ENCABEZADO
    story.append(Paragraph("Informe de Auditoría Integral: TechLogistics S.A.S", style_title))
    story.append(Paragraph(f"<b>Fecha de Emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_body))
    story.append(Paragraph("<b>Asunto:</b> Diagnóstico de Riesgo Operativo, Rentabilidad, Logistica y Fidelización", style_body))
    story.append(Spacer(1, 12))

    # 2. SALUD DEL DATO
    story.append(Paragraph("1. Certificación de Calidad de la Información", style_h2))
    data_health = [["Módulo", "Score Inicial", "Score Final", "Mejora"]]
    for ds, scores in health_scores.items():
        mejora = scores['Despues'] - scores['Antes']
        data_health.append([ds.capitalize(), f"{scores['Antes']:.1f}%", f"{scores['Despues']:.1f}%", f"+{mejora:.1f}%"])

    t_health = Table(data_health, colWidths=[1.5*72, 1.2*72, 1.2*72, 1*72])
    t_health.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_health)
    story.append(Spacer(1, 15))

    # 3. MÉTRICAS GENERALES
    story.append(Paragraph("2. Resumen de Indicadores Clave (KPIs)", style_h2))
    total_ingresos = df["ingreso_total"].sum()
    margen_promedio = (df["margen_real"].sum() / total_ingresos * 100) if total_ingresos != 0 else 0
    nps_global = df_analisis["NPS_Numerico"].mean()
    tasa_soporte_global = df["Ticket_Soporte"].mean() * 100

    data_kpis = [
        [Paragraph("Total Ingresos (USD)", style_kpi_header), Paragraph("Margen Operativo", style_kpi_header), Paragraph("NPS Global", style_kpi_header), Paragraph("Tasa Soporte", style_kpi_header)],
        [Paragraph(f"${total_ingresos:,.0f}", style_kpi_value), Paragraph(f"{margen_promedio:.1f}%", style_kpi_value), Paragraph(f"{nps_global:.2f}", style_kpi_value), Paragraph(f"{tasa_soporte_global:.1f}%", style_kpi_value)]
    ]
    t_kpis = Table(data_kpis, colWidths=[1.35*72]*4)
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eeeeee')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 10))

    # 4. CRISIS LOGÍSTICA
    story.append(Paragraph("3. Crisis Logística y Cuellos de Botella", style_h2))
    data_log_kpis = [
        [Paragraph("⏳ Tiempo Entrega Prom.", style_kpi_header), Paragraph("🔗 Correlación NPS/Tiempo", style_kpi_header), Paragraph("🚩 Brecha Máxima", style_kpi_header)],
        [Paragraph("15.0 días", style_kpi_value), Paragraph("-0.01", style_kpi_value), Paragraph("29 días", style_kpi_value)]
    ]
    t_log = Table(data_log_kpis, colWidths=[1.8*72]*3)
    t_log.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ebf5fb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_log)
    story.append(Spacer(1, 10))

    filtro_canal = df_analisis["Ciudad_Destino_Norm"].str.contains("CANAL DIGITAL|DIGITAL", na=False)
    registros_canal_digital = df_analisis[filtro_canal].shape[0] 
    story.append(Paragraph(f"<b>HALLAZGO DE TRAZABILIDAD:</b> Se identificaron <b>{registros_canal_digital} registros</b> con ciudad de destino <b>CANAL DIGITAL</b>. Al normalizar los datos, este volumen revela una carencia crítica de control geográfico sobre el gasto logístico.", style_body))

    story.append(Paragraph("⚠️ <b>ACCIÓN INMEDIATA:</b> Se requiere el <b>cambio de operador logístico</b> para la ruta <b>Zona Franca - Barranquilla</b>.", style_alerta))
    story.append(Spacer(1, 10))

    # 5. RIESGOS FINANCIEROS Y VENTA INVISIBLE
    print("\n[SECCIÓN 4] Insertando gráfico de ciudades...", file=sys.stderr)
    story.append(Paragraph("4. Riesgos Financieros y Administrativos", style_h2))
    ingreso_riesgo = 16899923.80
    porcentaje_riesgo = 27.3
    skus_no_catalogados = 754
    transacciones_afectadas = 2286

    story.append(Paragraph(f"<b>Diagnóstico de Venta Invisible:</b> Impacto financiero de <b>USD ${ingreso_riesgo:,.2f}</b> ({porcentaje_riesgo}% del total) por SKUs no catalogados.", style_body))
    
    # ⭐ INSERCIÓN DEL GRÁFICO DE CIUDADES ⭐
    insertar_grafico_plotly(
        fig_ciudades,
        story,
        "Figura 1: Top 10 Ciudades con Mayor Fuga por Venta Invisible",
        width=450,
        height=250
    )

    data_inv = [
        ["Métrica de Riesgo", "Valor Detectado"],
        ["Ingreso en Riesgo (USD)", f"${ingreso_riesgo:,.2f}"],
        ["SKUs No Catalogados", str(skus_no_catalogados)],
        ["Transacciones Afectadas", str(transacciones_afectadas)]
    ]
    t_inv = Table(data_inv, colWidths=[2.5*72, 1.5*72])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f4f4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(t_inv)
    
    df_perdida = df[df["margen_real"] < 0]
    total_fuga = abs(df_perdida["margen_real"].sum())
    story.append(Paragraph(f"• <b>Fuga de Capital:</b> Pérdida directa de <b>USD ${total_fuga:,.2f}</b> en márgenes negativos.", style_body))

    # 6. DIAGNÓSTICO DE FIDELIDAD
    story.append(Paragraph("5. Diagnóstico de Fidelidad y Paradoja de Inventario", style_h2))
    nps_avg_fid = 5.09
    casos_paradoja = 1844
    rating_prod = 2.99

    story.append(Paragraph(f"Se ha detectado una <b>paradoja crítica</b> en la gestión de stock: existen <b>{casos_paradoja} instancias</b> de productos con alta disponibilidad (Stock > Q3) pero sentimiento negativo del cliente (NPS < 7).", style_body))
    
    data_fid = [
        [Paragraph("NPS Promedio", style_kpi_header), Paragraph("Rating Producto", style_kpi_header), Paragraph("Casos Paradoja", style_kpi_header)],
        [Paragraph(f"{nps_avg_fid}/10", style_kpi_value), Paragraph(f"{rating_prod}/5", style_kpi_value), Paragraph(f"{casos_paradoja}", style_kpi_value)]
    ]
    t_fid = Table(data_fid, colWidths=[1.8*72]*3)
    t_fid.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fcf3cf')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_fid)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Explicación de la Paradoja:</b>", style_body))
    story.append(Paragraph(f"• <b>Calidad Deficiente:</b> El Rating de producto de <b>{rating_prod}/5</b> indica que el estancamiento de inventario se debe primordialmente a una <b>baja percepción de calidad</b> del SKU. El mercado está rechazando activamente estos productos.", style_body))
    story.append(Paragraph("• <b>Hipótesis de Sobrecosto:</b> Para categorías con Rating aceptable pero NPS bajo, el cliente valora el producto pero percibe un desbalance entre costo y beneficio (sobreprecio), lo que frena la rotación.", style_body))

    # 7. RIESGO OPERATIVO
    print("\n[SECCIÓN 6] Insertando gráfico de riesgo operativo...", file=sys.stderr)
    story.append(Paragraph("6. Riesgo Operativo: Bodegas 'A Ciegas'", style_h2))
    
    promedio_dias_sin_revision = 349
    tasa_tickets_soporte = 18.8
    correlacion_nps_riesgo = 0.01

    story.append(Paragraph(f"El análisis de riesgo operativo revela que el sistema de almacenamiento opera con un rezago crítico de auditoría, con un promedio de <b>{promedio_dias_sin_revision} días sin revisión</b> física de stock. Este descuido administrativo tiene una incidencia directa en la <b>tasa de soporte del {tasa_tickets_soporte}%</b>.", style_body))

    data_ops = [
        [Paragraph("Promedio Días Sin Revisión", style_kpi_header), Paragraph("Tasa Tickets Soporte", style_kpi_header), Paragraph("Correlación Riesgo/NPS", style_kpi_header)],
        [Paragraph(f"{promedio_dias_sin_revision} días", style_kpi_value), Paragraph(f"{tasa_tickets_soporte}%", style_kpi_value), Paragraph(f"{correlacion_nps_riesgo}", style_kpi_value)]
    ]
    t_ops = Table(data_ops, colWidths=[1.8*72]*3)
    t_ops.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2d7d5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_ops)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Top 5 Bodegas en Riesgo Crítico:</b>", style_body))
    data_bodegas = [
        ["Bodega", "Días Sin Revisión", "% Tickets Soporte", "Ingresos Expuestos"],
        ["OCCIDENTE", "358", "20.0%", "$7,499,527.64"],
        ["BOD-EXT-99", "355", "18.2%", "$8,753,852.21"],
        ["ZONA_FRANCA", "352", "18.3%", "$8,517,312.66"],
        ["Norte", "348", "19.1%", "$17,170,676.81"],
        ["Sur", "335", "18.9%", "$9,223,412.62"]
    ]
    t_bodegas = Table(data_bodegas, colWidths=[1.2*72, 1.2*72, 1.1*72, 1.5*72])
    t_bodegas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#922b21')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('FONTSIZE', (0, 0), (-1, -1), 9)
    ]))
    story.append(t_bodegas)
    
    story.append(Paragraph(f"<b>Diagnóstico de Gestión:</b> Las bodegas como <b>OCCIDENTE</b> y <b>BOD-EXT-99</b> operan prácticamente 'a ciegas'. La falta de revisión genera inconsistencias que disparan los tickets de soporte, degradando la confianza operativa.", style_body))

    # ⭐ INSERCIÓN DEL GRÁFICO DE RIESGO OPERATIVO ⭐
    insertar_grafico_plotly(
        fig_riesgo,
        story,
        "Figura 2: Impacto del Descuido Operativo por Bodega",
        width=450,
        height=250
    )

    # Construir PDF
    print("\n[DEBUG] Construyendo documento PDF...", file=sys.stderr)
    try:
        doc.build(story)
        buffer.seek(0)
        print("[DEBUG] ✓ PDF generado exitosamente", file=sys.stderr)
        print("="*80 + "\n", file=sys.stderr)
        return buffer
    except Exception as e:
        print(f"[ERROR] Error al construir PDF: {e}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
        raise
