"""Pestaña 1: entendimiento inicial de los datos."""

from __future__ import annotations

import pandas as pd
import streamlit as st

DESCRIPCIONES = {
    "id_cliente": "Identificador único del cliente.",
    "frecuencia_visita_mes": "Visitas promedio al mes.",
    "gasto_promedio_mxn": "Ticket promedio por visita (MXN).",
    "producto_favorito": "Categoría de producto que más consume.",
    "antiguedad_meses": "Meses desde la primera compra.",
    "visita_fin_semana": "1 si suele visitar sábado/domingo; 0 en otro caso.",
    "compro_ultima_campana": "1 si compró en la última campaña; 0 si no.",
    "edad": "Edad declarada del cliente (años).",
}


def _ejemplo(serie: pd.Series) -> str:
    """Devuelve un valor representativo y legible de una columna."""
    valores = serie.dropna()
    if valores.empty:
        return "—"
    valor = valores.iloc[0]
    if pd.api.types.is_float_dtype(serie):
        return f"{valor:,.2f}"
    if pd.api.types.is_integer_dtype(serie):
        return f"{int(valor):,}"
    return str(valor)


def render(df: pd.DataFrame) -> None:
    """Muestra dimensión, vista previa y diccionario de variables."""
    st.subheader("Entender los datos", icon=":material/table_view:")
    st.caption(
        "Unidad de análisis: **cliente**. Cada fila representa a una persona "
        "del programa de lealtad de Chaud & Glace."
    )

    filas, columnas = df.shape
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Total de filas",
        f"{filas:,}",
        help="Registros en el archivo original.",
        border=True,
    )
    col2.metric(
        "Total de columnas",
        f"{columnas}",
        help="Variables disponibles.",
        border=True,
    )
    col3.metric(
        "Valores nulos",
        f"{int(df.isna().sum().sum()):,}",
        help="Conteo global de celdas vacías.",
        border=True,
    )
    col4.metric(
        "Filas duplicadas",
        f"{int(df.duplicated().sum()):,}",
        help="Duplicados exactos detectados antes de limpiar.",
        border=True,
    )

    st.markdown("##### Vista previa · 10 registros")
    st.caption("Primer vistazo a la estructura y al contenido de la base original.")
    st.dataframe(
        df.head(10),
        width="stretch",
        hide_index=True,
        height=360,
    )

    st.markdown("##### Diccionario y calidad de variables")
    st.caption("Tipo, completitud, cardinalidad y descripción de cada campo.")

    resumen = pd.DataFrame(
        {
            "Variable": df.columns,
            "Tipo": [str(dtype) for dtype in df.dtypes],
            "No nulos": df.notna().sum().to_numpy(),
            "Nulos": df.isna().sum().to_numpy(),
            "% Nulos": (df.isna().mean() * 100).round(1).to_numpy(),
            "Valores únicos": df.nunique(dropna=True).to_numpy(),
            "Ejemplo": [_ejemplo(df[col]) for col in df.columns],
            "Descripción": [DESCRIPCIONES.get(col, "—") for col in df.columns],
        }
    )

    st.dataframe(
        resumen,
        width="stretch",
        hide_index=True,
        column_config={
            "% Nulos": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    with st.container(border=True):
        st.markdown("**Nota metodológica**")
        st.write(
            "El dataset mezcla variables de comportamiento (**frecuencia**, "
            "**gasto**, **antigüedad**) con contexto comercial (**producto "
            "favorito**, **visita de fin de semana**). La variable objetivo es "
            "`compro_ultima_campana`."
        )
