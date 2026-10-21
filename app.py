"""Chaud & Glace · Motor de recompra de clientes.

Aplicación Streamlit que recorre el flujo completo de analítica:
entender → limpiar → describir → predecir → prescribir → decidir.

Ejecutar con:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from modules import decidir, describir, entender, limpiar, predecir, prescribir

RUTA_DATOS = Path(__file__).resolve().parent / "data" / "clientes_chaud_glace.csv"

st.set_page_config(
    page_title="Chaud & Glace | Motor de recompra",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Solo se personaliza la identidad visual (hero y navegación). Los colores de
# cards, tablas, widgets y sidebar vienen del tema nativo de Streamlit, por lo
# que se adaptan automáticamente a los modos claro y oscuro.
st.markdown(
    """
    <style>
        .cg-hero {
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at 88% 12%, rgba(255, 196, 168, 0.28), transparent 34%),
                linear-gradient(125deg, #241715 0%, #43241F 48%, #9C3550 100%);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 22px;
            padding: 1.65rem 1.9rem 1.55rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 16px 40px rgba(24, 14, 12, 0.16);
        }
        .cg-hero::after {
            content: "";
            position: absolute;
            right: -55px;
            bottom: -85px;
            width: 260px;
            height: 260px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 50%;
            box-shadow: 0 0 0 28px rgba(255, 255, 255, 0.035),
                        0 0 0 56px rgba(255, 255, 255, 0.025);
        }
        .cg-hero__top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .cg-brand {
            display: inline-flex;
            align-items: center;
            gap: 0.65rem;
            color: #FFF8F2;
            font-weight: 700;
            letter-spacing: 0.01em;
        }
        .cg-brand__mark {
            display: inline-grid;
            place-items: center;
            width: 34px;
            height: 34px;
            border-radius: 10px;
            background: rgba(255, 248, 242, 0.12);
            border: 1px solid rgba(255, 248, 242, 0.24);
            font-family: Georgia, serif;
            font-size: 0.92rem;
        }
        .cg-eyebrow {
            color: #EBC9BB;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }
        .cg-hero h1 {
            color: #FFF9F4;
            font-family: var(--st-heading-font, Georgia, serif);
            font-size: clamp(1.95rem, 3.4vw, 2.75rem);
            font-weight: 700;
            line-height: 1.08;
            margin: 0 0 0.55rem 0;
            max-width: 920px;
        }
        .cg-hero p {
            color: #F2DDD4;
            font-size: 1rem;
            line-height: 1.6;
            margin: 0;
            max-width: 820px;
        }
        .cg-hero__chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1.1rem;
        }
        .cg-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: rgba(255, 248, 242, 0.10);
            border: 1px solid rgba(255, 248, 242, 0.20);
            border-radius: 999px;
            color: #FFF8F2;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.28rem 0.72rem;
        }
        .cg-chip__dot {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #F2B36A;
        }
        .cg-section-title {
            margin: 0.25rem 0 -0.35rem 0;
        }
        @media (max-width: 640px) {
            .cg-hero {padding: 1.25rem 1.15rem; border-radius: 16px;}
            .cg-hero__top {align-items: flex-start; flex-direction: column; gap: 0.45rem;}
            .cg-hero p {font-size: 0.93rem;}
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cargar_datos(ruta: str) -> pd.DataFrame:
    """Carga el CSV de clientes una sola vez por sesión."""
    return pd.read_csv(ruta, encoding="utf-8-sig")


def _hero(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> None:
    """Cabecera de marca con el contexto del análisis."""
    recompra = df_clean["compro_ultima_campana"].mean()
    st.markdown(
        f"""
        <div class="cg-hero">
            <div class="cg-hero__top">
                <div class="cg-brand">
                    <span class="cg-brand__mark">C&amp;G</span>
                    <span>Chaud &amp; Glace</span>
                </div>
                <span class="cg-eyebrow">Customer analytics</span>
            </div>
            <h1>Motor de recompra de clientes</h1>
            <p>
                ¿Qué clientes tienen mayor probabilidad de volver a comprar y qué
                promoción o estrategia comercial deberíamos darles? Un recorrido
                de seis etapas, desde los datos crudos hasta la decisión.
            </p>
            <div class="cg-hero__chips">
                <span class="cg-chip"><span class="cg-chip__dot"></span>{len(df_clean):,} clientes</span>
                <span class="cg-chip"><span class="cg-chip__dot"></span>{df_clean.shape[1]} variables</span>
                <span class="cg-chip"><span class="cg-chip__dot"></span>{recompra:.1%} recompra histórica</span>
                <span class="cg-chip"><span class="cg-chip__dot"></span>6 etapas</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sidebar(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> None:
    """Panel lateral con contexto, calidad de datos y ruta analítica."""
    with st.sidebar:
        st.markdown("#### Chaud & Glace")
        st.caption("Customer analytics · Cafetería y heladería")
        st.badge(
            "Base preparada",
            icon=":material/check_circle:",
            color="green",
        )

        with st.container(border=True):
            st.markdown("**Resumen de la base**")
            st.markdown(
                f"""
                **{len(df_clean):,}** clientes analizados  
                **{df_raw.shape[1]}** variables de negocio  
                **{len(df_raw) - len(df_clean):,}** duplicados depurados  
                **{df_clean['compro_ultima_campana'].mean():.1%}** recompra histórica
                """
            )

        st.markdown("##### Ruta analítica")
        st.markdown(
            """
            :material/table_view: Entender  
            :material/cleaning_services: Limpiar  
            :material/insights: Describir  
            :material/query_stats: Predecir  
            :material/route: Prescribir  
            :material/task_alt: Decidir
            """
        )

        st.caption(
            "Segmentos de recompra: **Alta** ≥ 60% · **Moderada** 35–59% · "
            "**Baja** < 35%."
        )
        st.caption("Datos sintéticos con fines demostrativos.")


def main() -> None:
    if not RUTA_DATOS.exists():
        st.error(
            "No se encontró `data/clientes_chaud_glace.csv`. "
            "Genera la base ejecutando: `python generar_datos_heladeria.py`."
        )
        st.stop()

    with st.spinner("Cargando y preparando los datos…"):
        df_raw = cargar_datos(str(RUTA_DATOS))
        df_clean = limpiar.limpiar_datos(df_raw)

    _hero(df_raw, df_clean)
    _sidebar(df_raw, df_clean)

    st.markdown("#### Recorrido analítico")
    st.caption(
        "Avanza por las pestañas para pasar del diagnóstico a una acción "
        "comercial concreta por segmento."
    )

    tab_entender, tab_limpiar, tab_describir, tab_predecir, tab_prescribir, tab_decidir = st.tabs(
        [
            "1 · Entender",
            "2 · Limpiar",
            "3 · Describir",
            "4 · Predecir",
            "5 · Prescribir",
            "6 · Decidir",
        ]
    )

    with tab_entender:
        entender.render(df_raw)

    with tab_limpiar:
        limpiar.render(df_raw, df_clean)

    with tab_describir:
        describir.render(df_clean)

    with tab_predecir:
        predecir.render(df_clean)

    with tab_prescribir:
        prescribir.render(df_clean)

    with tab_decidir:
        decidir.render(df_clean)

    st.space("large")
    st.caption(
        "Chaud & Glace · Ciencia de datos aplicada. Las probabilidades apoyan "
        "la decisión comercial y no la sustituyen."
    )


if __name__ == "__main__":
    main()
