"""Pestaña 2: diagnóstico y limpieza de datos."""

from __future__ import annotations

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina duplicados e imputa el gasto con la mediana.

    Parameters
    ----------
    df:
        Datos crudos cargados desde el CSV.

    Returns
    -------
    pandas.DataFrame
        Copia limpia, con índice reiniciado y sin nulos en gasto.
    """
    df_clean = df.drop_duplicates().copy()

    mediana_gasto = df_clean["gasto_promedio_mxn"].median()
    df_clean["gasto_promedio_mxn"] = df_clean["gasto_promedio_mxn"].fillna(
        mediana_gasto
    )

    return df_clean.reset_index(drop=True)


def render(df: pd.DataFrame, df_clean: pd.DataFrame | None = None) -> pd.DataFrame:
    """Documenta la limpieza aplicada y devuelve el DataFrame limpio."""
    if df_clean is None:
        df_clean = limpiar_datos(df)

    st.subheader("Limpiar y preparar", icon=":material/cleaning_services:")
    st.caption(
        "Se eliminan registros duplicados y se imputa el gasto faltante con la "
        "mediana para no distorsionar la distribución con valores extremos."
    )

    nulos_gasto = int(df["gasto_promedio_mxn"].isna().sum())
    duplicados = int(df.duplicated().sum())
    eliminados = len(df) - len(df_clean)
    mediana = float(df_clean["gasto_promedio_mxn"].median())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros originales", f"{len(df):,}", border=True)
    col2.metric(
        "Duplicados eliminados",
        f"{duplicados:,}",
        delta=f"-{eliminados} filas",
        delta_color="inverse",
        border=True,
    )
    col3.metric(
        "Nulos imputados",
        f"{nulos_gasto}",
        help="Solo en gasto_promedio_mxn.",
        border=True,
    )
    col4.metric(
        "Registros finales",
        f"{len(df_clean):,}",
        delta=f"{len(df_clean) - len(df):,}",
        border=True,
    )

    st.markdown("##### Diagnóstico de valores faltantes")

    tabla_nulos = pd.DataFrame(
        {
            "Variable": df.columns,
            "Nulos": df.isna().sum().to_numpy(),
            "% del total": (df.isna().mean() * 100).round(1).to_numpy(),
        }
    )
    tabla_nulos = tabla_nulos[tabla_nulos["Nulos"] > 0]
    if tabla_nulos.empty:
        st.success("No se encontraron valores nulos.")
    else:
        st.dataframe(
            tabla_nulos,
            width="stretch",
            hide_index=True,
            column_config={
                "% del total": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )

    st.markdown("##### Registros duplicados detectados")
    duplicados_df = df[df.duplicated(keep=False)].sort_values("id_cliente")
    if duplicados_df.empty:
        st.success("No se encontraron filas duplicadas.")
    else:
        st.warning(
            f"Se detectaron **{duplicados}** filas duplicadas "
            f"(**{len(duplicados_df)}** registros involucrados contando originales)."
        )
        with st.expander("Ver filas duplicadas", expanded=False):
            st.dataframe(duplicados_df, width="stretch", hide_index=True)

    st.markdown("##### Transformaciones aplicadas")
    st.markdown(
        f"""
        1. **Duplicados:** `drop_duplicates()` eliminó **{eliminados}** filas exactas.
        2. **Gasto faltante:** se imputaron **{nulos_gasto}** nulos con la mediana
           de **${mediana:,.2f} MXN**.
        3. **Índice:** se reinició para dejar una base consecutiva de
           **{len(df_clean):,}** clientes.
        """
    )

    st.success(
        f"Base limpia lista: **{len(df_clean):,} filas** × "
        f"**{df_clean.shape[1]} columnas**, sin duplicados y sin nulos en gasto."
    )

    return df_clean
