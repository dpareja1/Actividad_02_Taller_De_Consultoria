# -*- coding: utf-8 -*-

import streamlit as st
from datetime import datetime
import sys
import plotly.graph_objects as go

from src.data_loader import cargar_datos
from src.filtros import crear_sidebar_filtros

from src.paginas.resumen_ejecutivo import mostrar_resumen_ejecutivo
from src.paginas.fuga_capital import mostrar_fuga_capital
from src.paginas.crisis_logistica import mostrar_crisis_logistica
from src.paginas.venta_invisible import (
    mostrar_venta_invisible,
    construir_fig_venta_invisible
)
from src.paginas.diagnostico_fidelidad import mostrar_diagnostico_fidelidad
from src.paginas.riesgo_operativo import (
    mostrar_riesgo_operativo,
    construir_fig_riesgo_operativo
)
from src.paginas.salud_dato import mostrar_salud_datos

from src.reportes import generar_reporte_ejecutivo_pdf


# =============================================================================
# 1. Configuración de la página
# =============================================================================
st.set_page_config(
    page_title="TechLogistics DSS - Dashboard Ejecutivo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# 2. Carga de datos centralizada
# =============================================================================
try:
    df_dss, health_scores, metricas_calidad = cargar_datos()
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
    st.stop()


# =============================================================================
# 3. Sidebar – Filtros globales y exportación
# =============================================================================
df_filtrado = crear_sidebar_filtros(df_dss)

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar Datos Consolidados")


@st.cache_data(show_spinner=False)
def convertir_df_a_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")


csv_master = convertir_df_a_csv(df_filtrado)

st.sidebar.download_button(
    label="💾 Descargar Tabla Maestra (CSV)",
    data=csv_master,
    file_name=f"techlogistics_consolidado_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)


# =============================================================================
# 4. Encabezado principal
# =============================================================================
st.title("📊 TechLogistics S.A.S")
st.markdown("### Sistema de Soporte a Decisiones (DSS) – Auditoría de Consultoría")
st.info(
    f"💡 **Base de Datos Actualizada:** "
    f"Analizando {len(df_filtrado):,} transacciones filtradas."
)


# =============================================================================
# 5. Navegación por pestañas
# =============================================================================
tabs = st.tabs([
    "📈 Resumen Ejecutivo",
    "💰 Fuga de Capital",
    "🚚 Crisis Logística",
    "👻 Venta Invisible",
    "⭐ Diagnóstico Fidelidad",
    "⚠️ Riesgo Operativo",
    "📊 Salud de los Datos"
])

with tabs[0]:
    mostrar_resumen_ejecutivo(df_filtrado, health_scores, metricas_calidad)

with tabs[1]:
    mostrar_fuga_capital(df_filtrado)

with tabs[2]:
    mostrar_crisis_logistica(df_filtrado)

with tabs[3]:
    mostrar_venta_invisible(df_filtrado, renderizar=True)

with tabs[4]:
    mostrar_diagnostico_fidelidad(df_filtrado)

with tabs[5]:
    mostrar_riesgo_operativo(df_filtrado, renderizar=True)

with tabs[6]:
    mostrar_salud_datos(df_filtrado, metricas_calidad)


# =============================================================================
# 6. Generación de Reporte PDF (FIX DEFINITIVO STREAMLIT STATE)
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📄 Reporte Ejecutivo PDF")

# ---- Estado persistente (CLAVE DEL ARREGLO) ----
if "pdf_reporte" not in st.session_state:
    st.session_state.pdf_reporte = None

if "fig_ciudades" not in st.session_state:
    st.session_state.fig_ciudades = None

if "fig_riesgo" not in st.session_state:
    st.session_state.fig_riesgo = None


def validar_figura(fig, nombre):
    if fig is None:
        raise ValueError(f"La figura '{nombre}' es None")
    if not isinstance(fig, go.Figure):
        raise TypeError(
            f"La figura '{nombre}' no es un objeto Plotly Figure. "
            f"Tipo recibido: {type(fig)}"
        )


if st.sidebar.button("🛠️ Preparar Reporte"):
    try:
        with st.spinner("🔄 Generando reporte ejecutivo..."):

            # -------------------------------------------------------------
            # 1. CONSTRUIR FIGURAS (FUNCIONES PURAS)
            # -------------------------------------------------------------
            st.session_state.fig_ciudades = construir_fig_venta_invisible(df_filtrado)
            st.session_state.fig_riesgo = construir_fig_riesgo_operativo(df_filtrado)

            print("[DEBUG APP] Figuras en session_state:")
            print("fig_ciudades =", type(st.session_state.fig_ciudades))
            print("fig_riesgo   =", type(st.session_state.fig_riesgo))

            # -------------------------------------------------------------
            # 2. VALIDACIÓN DEFENSIVA
            # -------------------------------------------------------------
            validar_figura(st.session_state.fig_ciudades, "Venta Invisible")
            validar_figura(st.session_state.fig_riesgo, "Riesgo Operativo")

            # -------------------------------------------------------------
            # 3. GENERACIÓN DEL PDF
            # -------------------------------------------------------------
            st.session_state.pdf_reporte = generar_reporte_ejecutivo_pdf(
                df_filtrado=df_filtrado,
                health_scores=health_scores,
                metricas_calidad=metricas_calidad,
                fig_ciudades=st.session_state.fig_ciudades,
                fig_riesgo=st.session_state.fig_riesgo
            )

        st.sidebar.success("✅ Reporte listo para descargar")

    except Exception as e:
        st.sidebar.error("❌ Error al generar el reporte PDF")
        import traceback
        print(traceback.format_exc(), file=sys.stderr)


# =============================================================================
# 7. Descarga del PDF
# =============================================================================
if st.session_state.pdf_reporte is not None:
    st.sidebar.download_button(
        label="⬇️ Descargar Reporte PDF",
        data=st.session_state.pdf_reporte,
        file_name=f"Reporte_Ejecutivo_TechLogistics_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )


# =============================================================================
# Footer
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 TechLogistics S.A.S – Dashboard de Auditoría Técnica")
