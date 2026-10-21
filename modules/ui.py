"""Utilidades visuales compartidas: paleta y estilo de gráficos.

Los colores se adaptan al modo claro/oscuro activo para evitar fondos
blancos y textos invisibles cuando el usuario cambia la apariencia.
"""

from __future__ import annotations

import streamlit as st

PALETA_CLARA = ["#C43D5B", "#D9884B", "#3E8E68", "#8C6A5D", "#B58B5A", "#7A6FA8"]
PALETA_OSCURA = ["#F08CA0", "#F2B36A", "#6FC79A", "#C9A28E", "#D9B36A", "#A99BE0"]


def es_modo_oscuro() -> bool:
    """Indica si la apariencia activa es oscura (con fallback seguro)."""
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def paleta() -> list[str]:
    """Devuelve la paleta categórica adecuada al modo activo."""
    return PALETA_OSCURA if es_modo_oscuro() else PALETA_CLARA


def colores() -> dict[str, str]:
    """Tokens de color para gráficos Plotly."""
    if es_modo_oscuro():
        return {
            "texto": "#F5EDE6",
            "texto_suave": "#C7B8AE",
            "grid": "rgba(245, 237, 230, 0.10)",
            "positivo": "#6FC79A",
            "negativo": "#F08CA0",
            "acento": "#F08CA0",
            "hover": "#2A211D",
        }
    return {
        "texto": "#2D211C",
        "texto_suave": "#7A665B",
        "grid": "rgba(45, 33, 28, 0.10)",
        "positivo": "#3E8E68",
        "negativo": "#C43D5B",
        "acento": "#C43D5B",
        "hover": "#FFFFFF",
    }


def aplicar_estilo(fig, *, height: int = 420):
    """Aplica fondo transparente y tipografía legible al gráfico Plotly."""
    c = colores()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", color=c["texto"], size=13),
        height=height,
        margin=dict(l=16, r=24, t=24, b=16),
        hoverlabel=dict(
            bgcolor=c["hover"],
            bordercolor=c["grid"],
            font=dict(color=c["texto"], family="Manrope, sans-serif"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(color=c["texto_suave"]),
        ),
    )
    fig.update_xaxes(
        gridcolor=c["grid"],
        zerolinecolor=c["grid"],
        linecolor=c["grid"],
        tickfont=dict(color=c["texto_suave"]),
        title_font=dict(color=c["texto_suave"]),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor=c["grid"],
        zerolinecolor=c["grid"],
        linecolor=c["grid"],
        tickfont=dict(color=c["texto_suave"]),
        title_font=dict(color=c["texto_suave"]),
        automargin=True,
    )
    return fig
