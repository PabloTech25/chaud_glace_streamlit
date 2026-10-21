"""Pestaña 4: modelo de regresión logística para predecir recompra."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from modules.ui import aplicar_estilo, colores

FEATURES = [
    "frecuencia_visita_mes",
    "gasto_promedio_mxn",
    "antiguedad_meses",
]

ETIQUETAS = {
    "frecuencia_visita_mes": "Frecuencia de visita",
    "gasto_promedio_mxn": "Gasto promedio",
    "antiguedad_meses": "Antigüedad",
}


@st.cache_data(show_spinner=False)
def entrenar_modelo(df: pd.DataFrame) -> dict:
    """Entrena una regresión logística y devuelve modelo, métricas y pesos.

    La accuracy se calcula sobre una muestra de prueba (25%) estratificada.
    Después de evaluar, el modelo se reentrena con todos los datos para
    generar las probabilidades de la etapa de prescripción.
    """
    X = df[FEATURES].astype(float)
    y = df["compro_ultima_campana"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    pipeline = Pipeline(
        steps=[
            ("escalador", StandardScaler()),
            (
                "modelo",
                LogisticRegression(max_iter=1000, random_state=42),
            ),
        ]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    # Reentrenamiento con toda la base para prescribir sobre cada cliente.
    modelo_final = clone(pipeline).fit(X, y)
    coeficientes = modelo_final.named_steps["modelo"].coef_[0]

    return {
        "modelo": modelo_final,
        "accuracy": float(accuracy),
        "auc": float(auc),
        "coeficientes": dict(zip(FEATURES, coeficientes)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }


def render(df: pd.DataFrame) -> None:
    """Entrena el modelo y presenta accuracy y coeficientes."""
    st.subheader("Predecir la probabilidad de recompra", icon=":material/query_stats:")
    st.caption(
        "Regresión logística con tres variables de comportamiento. Las variables "
        "se estandarizan para que sus coeficientes sean comparables entre sí."
    )

    info = entrenar_modelo(df)
    accuracy = info["accuracy"]
    auc = info["auc"]

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Accuracy del modelo",
        f"{accuracy * 100:.1f}%",
        help="Aciertos sobre la muestra de prueba (25% de los clientes).",
        border=True,
    )
    col2.metric(
        "AUC-ROC",
        f"{auc:.2f}",
        help="Capacidad de discriminación; 0.5 equivale a azar y 1.0 es perfecta.",
        border=True,
    )
    col3.metric(
        "Clientes analizados",
        f"{len(df):,}",
        help=f"{info['n_train']} para entrenar y {info['n_test']} para evaluar.",
        border=True,
    )

    st.markdown("##### Peso de cada variable en la decisión")
    st.caption(
        "Coeficientes estandarizados: valores positivos empujan la recompra; "
        "valores negativos la reducen."
    )
    df_coef = pd.DataFrame(
        {
            "Variable": [ETIQUETAS[f] for f in FEATURES],
            "Coeficiente": [info["coeficientes"][f] for f in FEATURES],
        }
    ).sort_values("Coeficiente")
    df_coef["Efecto"] = np.where(
        df_coef["Coeficiente"] >= 0,
        "Aumenta la recompra",
        "Reduce la recompra",
    )

    c = colores()
    fig = px.bar(
        df_coef,
        x="Coeficiente",
        y="Variable",
        orientation="h",
        color="Efecto",
        text_auto=".2f",
        color_discrete_map={
            "Aumenta la recompra": c["positivo"],
            "Reduce la recompra": c["negativo"],
        },
        labels={"Coeficiente": "Peso estandarizado", "Variable": ""},
    )
    fig.add_vline(x=0, line_color=c["texto_suave"], line_width=1)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis_title="Coeficiente estandarizado",
        legend_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    aplicar_estilo(fig, height=340)
    st.plotly_chart(
        fig,
        width="stretch",
        alt="Coeficientes estandarizados del modelo de recompra",
    )


    variable_top = max(info["coeficientes"], key=info["coeficientes"].get)
    signo = "incrementa" if info["coeficientes"][variable_top] >= 0 else "reduce"
    with st.container(border=True):
        st.markdown("**Lectura del modelo**")
        st.write(
            f"La variable con mayor peso es **{ETIQUETAS[variable_top].lower()}** "
            f"({info['coeficientes'][variable_top]:+.2f}) y {signo} la probabilidad "
            f"de recompra. Con una accuracy de **{accuracy * 100:.1f}%**, el modelo "
            "supera claramente a una asignación al azar y es útil para priorizar "
            "esfuerzos comerciales, no para tomar decisiones irreversibles."
        )
    st.caption(
        "Lectura del coeficiente: al aumentar una desviación estándar de la "
        "variable, cambian las *odds* de recompra manteniendo el resto constante."
    )
