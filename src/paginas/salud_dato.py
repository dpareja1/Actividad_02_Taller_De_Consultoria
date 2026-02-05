# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar_salud_datos(df, metricas_calidad):
    st.header("🔍 Salud del Dato - Auditoría de Calidad")
    st.markdown("---")
    
    # 1. Preparación de datos para los gráficos
    hs_data = []
    for modulo, met in metricas_calidad.items():
        hs_data.append({
            "Módulo": modulo.capitalize(),
            "Antes": met.get("health_score_antes", 0),
            "Despues": met.get("health_score_despues", 0)
        })
    df_hs = pd.DataFrame(hs_data)

    # 2. Resumen Ejecutivo
    avg_antes = df_hs["Antes"].mean()
    avg_despues = df_hs["Despues"].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⭐ Health Score Inicial", f"{avg_antes:.1f}%")
    with col2:
        st.metric("✅ Health Score Final", f"{avg_despues:.1f}%", delta=f"{avg_despues - avg_antes:.1f}%")
    with col3:
        nulos = df.isna().sum().sum()
        st.metric("🕳️ Celdas Vacías", f"{nulos:,}")

    # 3. Gráfico Comparativo
    fig = px.bar(df_hs, x="Módulo", y=["Antes", "Despues"], barmode="group",
                 title="Mejora de Calidad por Módulo",
                 color_discrete_map={"Antes": "#FF6B6B", "Despues": "#4ECDC4"})
    st.plotly_chart(fig, use_container_width=True)

    # 4. Detalle por Módulo (Tabs)
    t1, t2, t3 = st.tabs(["Feedback", "Inventario", "Transacciones"])
    
    with t1:
        m = metricas_calidad.get("feedback", {})
        c1, c2 = st.columns(2)
        c1.metric("👤 Edades Corregidas", m.get("edades_corregidas", 0))
        c2.metric("⭐ Ratings Ajustados", m.get("ratings_corregidos", 0))
        st.info("Estrategia: Normalización de NPS a base 10 e imputación de edades por mediana.")

    with t2:
        m = metricas_calidad.get("inventario", {})
        c1, c2 = st.columns(2)
        c1.metric("💰 Costos Atípicos", m.get("costos_outliers", 0))
        c2.metric("📦 Stocks Negativos", m.get("stock_negativos", 0))
        st.info("Estrategia: Limpieza de costos mediante mediana por categoría.")

    with t3:
        m = metricas_calidad.get("transacciones", {})
        c1, c2 = st.columns(2)
        c1.metric("🚚 Tiempos 'Outliers'", m.get("tiempos_outliers", 0))
        c2.metric("❌ SKUs No Catalogados", m.get("skus_sin_inventario", 0))
        st.info("Estrategia: Corrección de tiempos de entrega de 999 días.")