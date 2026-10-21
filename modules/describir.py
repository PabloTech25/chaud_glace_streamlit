"""Pestaña 3: estadísticas descriptivas y comportamiento de recompra."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.ui import aplicar_estilo, colores, paleta


def render(df: pd.DataFrame) -> None:
    """Muestra los tres KPIs del negocio y la recompra por producto."""
    st.subheader("Describir el comportamiento", icon=":material/insights:")
    st.caption(
        "Lectura ejecutiva de la base limpia: qué tan seguido compran, cuánto "
        "gastan y cómo se comporta la recompra por categoría."
    )

    tasa_recompra = df["compro_ultima_campana"].mean() * 100
    gasto_promedio = df["gasto_promedio_mxn"].mean()
    visitas_promedio = df["frecuencia_visita_mes"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Tasa de recompra",
        f"{tasa_recompra:.1f}%",
        help="Porcentaje de clientes que compraron en la última campaña.",
        border=True,
    )
    col2.metric(
        "Gasto promedio",
        f"${gasto_promedio:,.2f} MXN",
        help="Ticket promedio por visita, después de imputar nulos.",
        border=True,
    )
    col3.metric(
        "Visitas promedio",
        f"{visitas_promedio:.1f} / mes",
        help="Frecuencia media de visita mensual.",
        border=True,
    )

    st.markdown("##### Tasa de recompra por producto favorito")
    st.caption("La línea punteada marca el promedio general del portafolio.")
    fig = px.histogram(
        df,
        x="producto_favorito",
        y="compro_ultima_campana",
        histfunc="avg",
        color="producto_favorito",
        text_auto=".0%",
        color_discrete_sequence=paleta(),
        labels={
            "producto_favorito": "Producto favorito",
            "compro_ultima_campana": "Tasa de recompra",
        },
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Tasa de recompra: %{y:.1%}<br>"
            "<extra></extra>"
        ),
    )
    fig.add_hline(
        y=df["compro_ultima_campana"].mean(),
        line_dash="dot",
        line_color=colores()["texto_suave"],
        annotation_text=f"Promedio general {tasa_recompra:.1f}%",
        annotation_position="top left",
        annotation_font_color=colores()["texto_suave"],
    )
    fig.update_layout(
        showlegend=False,
        yaxis=dict(tickformat=".0%", range=[0, 1], title="Tasa de recompra"),
        xaxis_title=None,
    )
    aplicar_estilo(fig, height=420)
    st.plotly_chart(
        fig,
        width="stretch",
        alt="Tasa de recompra por producto favorito",
    )


    tasas = (
        df.groupby("producto_favorito", observed=True)["compro_ultima_campana"]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=False)
    )
    if not tasas.empty:
        mejor = tasas.index[0]
        mejor_tasa = tasas.loc[mejor, "mean"] * 100
        menor = tasas.index[-1]
        menor_tasa = tasas.loc[menor, "mean"] * 100
        with st.container(border=True):
            st.markdown("**Lectura del gráfico**")
            st.write(
                f"**{mejor}** lidera la recompra con **{mejor_tasa:.1f}%**, "
                f"mientras que **{menor}** registra **{menor_tasa:.1f}%**. "
                "La cercanía entre categorías sugiere que el producto no es el único "
                "motor de recompra: la frecuencia y el gasto también pesan."
            )
