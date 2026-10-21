"""Pestaña 5: segmentación por probabilidad y matriz de prescripción."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from modules.predecir import FEATURES, entrenar_modelo

SEGMENTOS = ["Alta", "Moderada", "Baja"]
RANGOS = {
    "Alta": "≥ 60%",
    "Moderada": "35% – 59%",
    "Baja": "< 35%",
}

# Configuración comercial reutilizada por la pestaña Decidir.
MATRIZ_COMERCIAL = {
    "Alta": {
        "emoji": "🥇",
        "prioridad": "Retener y rentabilizar",
        "accion": (
            "Activar el programa de recompra VIP con acceso anticipado a nuevos "
            "sabores y doble punto de lealtad."
        ),
        "oferta": "2x1 en {producto} o 20% en la siguiente visita (válido 14 días).",
        "canal": "WhatsApp personalizado y correo; contacto en las próximas 48 horas.",
        "mensaje": (
            "¡{producto} te está esperando! Como parte de nuestros clientes más "
            "fieles, tienes acceso anticipado a los nuevos sabores y un 2x1 "
            "exclusivo esta semana en Chaud & Glace. 🍦☕"
        ),
        "objetivo": "Elevar la frecuencia y el ticket sin regalar margen.",
    },
    "Moderada": {
        "emoji": "🔄",
        "prioridad": "Reactivar el hábito",
        "accion": (
            "Campaña de reactivación con incentivo de ticket y recordatorio del "
            "producto favorito para recuperar la visita quincenal."
        ),
        "oferta": "10% de descuento + postre de cortesía en compra mínima de $150.",
        "canal": "Instagram/Facebook Ads y SMS; activar jueves a domingo.",
        "mensaje": (
            "Tu {producto} favorito sabe mejor en buena compañía. Vuelve este fin "
            "de semana y llévate un postre de cortesía en tu compra. Te guardamos "
            "lugar en Chaud & Glace. 🍰"
        ),
        "objetivo": "Mover al cliente a una segunda compra y consolidar el hábito.",
    },
    "Baja": {
        "emoji": "🌱",
        "prioridad": "Recuperar sin sacrificar margen",
        "accion": (
            "Campaña masiva de bajo costo con cupón de bienvenida y contenido del "
            "producto favorito; evitar contacto uno a uno."
        ),
        "oferta": "Cupón de $25 MXN en consumo mínimo de $100.",
        "canal": "Correo masivo y anuncio geolocalizado; sin seguimiento individual.",
        "mensaje": (
            "¿Un antojo? Regresa a Chaud & Glace con $25 de descuento en tu "
            "próxima visita. Hay un {producto} esperando por ti. ✨"
        ),
        "objetivo": "Recuperar atención con inversión mínima y medir respuesta.",
    },
}


@st.cache_data(show_spinner=False)
def evaluar_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """Añade probabilidad de compra y segmento comercial a cada cliente."""
    modelo = entrenar_modelo(df)["modelo"]

    evaluados = df.copy()
    evaluados["probabilidad_compra"] = modelo.predict_proba(
        evaluados[FEATURES].astype(float)
    )[:, 1]

    evaluados["segmento"] = np.select(
        [
            evaluados["probabilidad_compra"] >= 0.60,
            evaluados["probabilidad_compra"] >= 0.35,
        ],
        ["Alta", "Moderada"],
        default="Baja",
    )
    evaluados["probabilidad_pct"] = evaluados["probabilidad_compra"] * 100

    return evaluados


def _producto_estrella(subconjunto: pd.DataFrame) -> str:
    if subconjunto.empty:
        return "—"
    return str(subconjunto["producto_favorito"].mode().iloc[0])


def render(df: pd.DataFrame) -> None:
    """Calcula probabilidades, segmenta y muestra la matriz de acción."""
    st.subheader("Prescribir: a quién priorizar y con qué", icon=":material/route:")
    st.caption(
        "La probabilidad del modelo se traduce en tres segmentos accionables. "
        "La matriz conecta cada segmento con una oferta, un canal y un objetivo."
    )

    evaluados = evaluar_clientes(df)
    total = len(evaluados)
    alta = int((evaluados["segmento"] == "Alta").sum())
    moderada = int((evaluados["segmento"] == "Moderada").sum())
    baja = int((evaluados["segmento"] == "Baja").sum())
    prob_media = evaluados["probabilidad_compra"].mean() * 100
    valor_esperado = float(
        (evaluados["probabilidad_compra"] * evaluados["gasto_promedio_mxn"]).sum()
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Alta prioridad",
        f"{alta:,}",
        help=f"{alta / total:.1%} de la cartera.",
        border=True,
    )
    col2.metric(
        "Prioridad moderada",
        f"{moderada:,}",
        help=f"{moderada / total:.1%} de la cartera.",
        border=True,
    )
    col3.metric(
        "Probabilidad media",
        f"{prob_media:.1f}%",
        help="Promedio de todo el portafolio.",
        border=True,
    )
    col4.metric(
        "Valor esperado de recompra",
        f"${valor_esperado:,.0f}",
        help="Suma de gasto promedio × probabilidad de compra.",
        border=True,
    )

    st.markdown("##### Matriz de prescripción comercial")
    st.caption(
        "Cada fila resume el tamaño del segmento, su ticket y la jugada comercial "
        "recomendada."
    )

    filas = []
    for segmento in SEGMENTOS:
        subconjunto = evaluados[evaluados["segmento"] == segmento]
        config = MATRIZ_COMERCIAL[segmento]
        producto = _producto_estrella(subconjunto)
        filas.append(
            {
                "Segmento": f"{config['emoji']} {segmento}",
                "Probabilidad": RANGOS[segmento],
                "Clientes": len(subconjunto),
                "% cartera": len(subconjunto) / total * 100,
                "Ticket prom.": subconjunto["gasto_promedio_mxn"].mean(),
                "Producto estrella": producto,
                "Acción comercial": config["accion"],
                "Oferta sugerida": config["oferta"].format(producto=producto.lower()),
                "Canal y momento": config["canal"],
            }
        )
    matriz = pd.DataFrame(filas)

    st.dataframe(
        matriz,
        width="stretch",
        hide_index=True,
        column_config={
            "Clientes": st.column_config.NumberColumn(format="%d"),
            "% cartera": st.column_config.NumberColumn(format="%.1f%%"),
            "Ticket prom.": st.column_config.NumberColumn(format="$%.0f"),
            "Probabilidad": st.column_config.TextColumn(width="small"),
            "Segmento": st.column_config.TextColumn(width="small"),
            "Producto estrella": st.column_config.TextColumn(width="small"),
            "Acción comercial": st.column_config.TextColumn(width="large"),
            "Oferta sugerida": st.column_config.TextColumn(width="medium"),
            "Canal y momento": st.column_config.TextColumn(width="medium"),
        },
    )

    st.markdown("##### Clientes evaluados")
    st.caption(
        "Ordenados por probabilidad estimada. La barra de progreso facilita "
        "detectar a quién contactar primero."
    )

    tabla_clientes = (
        evaluados[
            [
                "id_cliente",
                "producto_favorito",
                "frecuencia_visita_mes",
                "gasto_promedio_mxn",
                "antiguedad_meses",
                "visita_fin_semana",
                "probabilidad_pct",
                "segmento",
            ]
        ]
        .sort_values("probabilidad_pct", ascending=False)
        .rename(
            columns={
                "id_cliente": "Cliente",
                "producto_favorito": "Producto favorito",
                "frecuencia_visita_mes": "Visitas/mes",
                "gasto_promedio_mxn": "Gasto prom.",
                "antiguedad_meses": "Antigüedad (meses)",
                "visita_fin_semana": "Fin de semana",
                "probabilidad_pct": "Prob. recompra",
                "segmento": "Segmento",
            }
        )
    )
    tabla_clientes["Fin de semana"] = tabla_clientes["Fin de semana"].map(
        {1: "Sí", 0: "No"}
    )

    st.dataframe(
        tabla_clientes,
        width="stretch",
        hide_index=True,
        height=420,
        column_config={
            "Gasto prom.": st.column_config.NumberColumn(format="$%.2f"),
            "Prob. recompra": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
            "Visitas/mes": st.column_config.NumberColumn(format="%d"),
            "Antigüedad (meses)": st.column_config.NumberColumn(format="%d"),
            "Cliente": st.column_config.TextColumn(width="small"),
        },
    )

    csv = evaluados.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar clientes evaluados (CSV)",
        data=csv,
        file_name="clientes_evaluados_chaud_glace.csv",
        mime="text/csv",
        width="content",
    )

    st.caption(
        "Regla de segmentación: **Alta** ≥ 60%, **Moderada** 35%–59%, "
        "**Baja** < 35% de probabilidad estimada de compra."
    )
