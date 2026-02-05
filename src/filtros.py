# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def crear_sidebar_filtros(df_dss):

    st.sidebar.title("🎛️ Panel de Control")
    st.sidebar.markdown("---")
    
    # Filtros principales
    st.sidebar.subheader("🔍 Filtros de Negocio")
    
    df_filtrado = df_dss.copy()
    
    # 1. Filtro por Categoría (Incluye 'no Catalogado' de la Venta Invisible)
    if "Categoria" in df_dss.columns:
        # Obtenemos todas las categorías únicas
        categorias = sorted(df_dss["Categoria"].unique().tolist())
        cat_sel = st.sidebar.multiselect(
            "Categoría de Producto",
            options=categorias,
            default=categorias
        )
        if cat_sel:
            df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(cat_sel)]
    
    # 2. Filtro por Ciudad Destino
    if "Ciudad_Destino" in df_dss.columns:
        ciudades = sorted(df_dss["Ciudad_Destino"].dropna().unique().tolist())
        city_sel = st.sidebar.multiselect(
            "Ciudad Destino",
            options=ciudades,
            default=ciudades 
        )
        if city_sel:
            df_filtrado = df_filtrado[df_filtrado["Ciudad_Destino"].isin(city_sel)]

    # 3. Filtro por Estado de Envío
    if "Estado_Envio" in df_dss.columns:
        estados = sorted(df_dss["Estado_Envio"].dropna().unique().tolist())
        estado_sel = st.sidebar.multiselect(
            "Estado de Envío",
            options=estados,
            default=estados
        )
        if estado_sel:
            df_filtrado = df_filtrado[df_filtrado["Estado_Envio"].isin(estado_sel)]
    
    # 4. Filtro por Rango de Fechas
    if "Fecha_Venta" in df_dss.columns:
        st.sidebar.subheader("📅 Período de Análisis")
        df_dss["Fecha_Venta"] = pd.to_datetime(df_dss["Fecha_Venta"])
        fecha_min = df_dss["Fecha_Venta"].min().date()
        fecha_max = df_dss["Fecha_Venta"].max().date()
        
        rango_fechas = st.sidebar.date_input(
            "Seleccione el rango",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
            df_filtrado = df_filtrado[
                (df_filtrado["Fecha_Venta"].dt.date >= rango_fechas[0]) &
                (df_filtrado["Fecha_Venta"].dt.date <= rango_fechas[1])
            ]
    
    # 5. Segmentación por Rentabilidad
    st.sidebar.markdown("---")
    st.sidebar.subheader("💸 Filtros de Margen")
    solo_negativos = st.sidebar.checkbox("Mostrar solo Margen Negativo")
    if solo_negativos:
        df_filtrado = df_filtrado[df_filtrado["margen_real"] < 0]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Visualizando {len(df_filtrado):,} de {len(df_dss):,} registros")
    
    return df_filtrado