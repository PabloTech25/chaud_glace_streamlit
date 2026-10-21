"""Genera el dataset sintético de clientes de Chaud & Glace.

El archivo se guarda en ``data/clientes_chaud_glace.csv`` e incluye,
de forma intencional, valores faltantes y filas duplicadas para que las
etapas de limpieza de la aplicación tengan algo que resolver.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RUTA_SALIDA = Path(__file__).resolve().parent / "data" / "clientes_chaud_glace.csv"

PRODUCTOS = ["Helados/Paletas", "Café y Frappes", "Postres", "Salados"]
PROBABILIDAD_PRODUCTO = [0.34, 0.28, 0.26, 0.12]

# Gasto base por tipo de producto (MXN)
GASTO_BASE = {
    "Helados/Paletas": 95,
    "Café y Frappes": 120,
    "Postres": 150,
    "Salados": 110,
}

# Pequeño efecto de producto en la probabilidad de recompra
EFECTO_PRODUCTO = {
    "Helados/Paletas": -0.10,
    "Café y Frappes": 0.10,
    "Postres": 0.25,
    "Salados": -0.05,
}


def _estandarizar(valores: np.ndarray) -> np.ndarray:
    """Devuelve los valores estandarizados (media 0, desviación 1)."""
    desviacion = valores.std(ddof=0)
    if desviacion == 0:
        return np.zeros_like(valores, dtype=float)
    return (valores - valores.mean()) / desviacion


def generar_datos(n_clientes: int = 260, seed: int = 42) -> pd.DataFrame:
    """Construye el DataFrame de clientes con 8 variables.

    Se generan 260 clientes únicos, se agregan 2 filas duplicadas y se
    dejan 5 nulos en ``gasto_promedio_mxn``.
    """
    rng = np.random.default_rng(seed)

    ids = [f"CG-{i:04d}" for i in range(1, n_clientes + 1)]

    # Frecuencia mensual: distribución asimétrica, de 1 a 20 visitas.
    frecuencia = np.clip(
        np.rint(rng.gamma(shape=2.4, scale=2.0, size=n_clientes) + 1), 1, 20
    ).astype(int)

    producto = rng.choice(PRODUCTOS, size=n_clientes, p=PROBABILIDAD_PRODUCTO)

    # Antigüedad: clientes nuevos y veteranos, hasta 72 meses.
    antiguedad = np.clip(
        np.rint(rng.gamma(shape=2.2, scale=11.0, size=n_clientes) + 1), 1, 72
    ).astype(int)

    # La visita de fin de semana es más probable en clientes frecuentes.
    prob_fin_semana = np.clip(0.22 + 0.025 * frecuencia, 0.20, 0.80)
    visita_fin_semana = rng.binomial(1, prob_fin_semana, size=n_clientes)

    gasto_base = np.array([GASTO_BASE[p] for p in producto])
    gasto_promedio = (
        gasto_base
        + 5.8 * frecuencia
        + 0.75 * antiguedad
        + 14 * visita_fin_semana
        + rng.normal(0, 22, size=n_clientes)
    )
    gasto_promedio = np.clip(np.rint(gasto_promedio), 45, 650).astype(float)

    edad = np.clip(
        np.rint(rng.normal(loc=32, scale=11, size=n_clientes)), 18, 74
    ).astype(int)

    # Probabilidad latente de compra en la última campaña.
    efecto_producto = np.array([EFECTO_PRODUCTO[p] for p in producto])
    logit = (
        -0.10
        + 1.55 * _estandarizar(frecuencia.astype(float))
        + 0.75 * _estandarizar(gasto_promedio)
        + 0.30 * _estandarizar(antiguedad.astype(float))
        + 0.45 * visita_fin_semana
        + efecto_producto
        + rng.normal(0, 0.12, size=n_clientes)
    )
    probabilidad = 1 / (1 + np.exp(-logit))
    compro_ultima_campana = rng.binomial(1, probabilidad, size=n_clientes)

    df = pd.DataFrame(
        {
            "id_cliente": ids,
            "frecuencia_visita_mes": frecuencia,
            "gasto_promedio_mxn": gasto_promedio,
            "producto_favorito": producto,
            "antiguedad_meses": antiguedad,
            "visita_fin_semana": visita_fin_semana,
            "compro_ultima_campana": compro_ultima_campana,
            "edad": edad,
        }
    )

    # 5 valores faltantes intencionales en el gasto promedio.
    indices_nulos = rng.choice(df.index, size=5, replace=False)
    df.loc[indices_nulos, "gasto_promedio_mxn"] = np.nan

    # 2 filas duplicadas exactas (se eligen filas sin nulos para que el
    # duplicado sea detectable con drop_duplicates).
    candidatos = df[df["gasto_promedio_mxn"].notna()].index
    indices_duplicados = rng.choice(candidatos, size=2, replace=False)
    df = pd.concat([df, df.loc[indices_duplicados]], ignore_index=True)

    # Mezcla el orden para que los duplicados no queden al final.
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    return df


def guardar_datos(df: pd.DataFrame, ruta: Path = RUTA_SALIDA) -> Path:
    """Guarda el DataFrame en CSV (UTF-8 con BOM para Excel)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    return ruta


def main() -> None:
    df = generar_datos()
    ruta = guardar_datos(df)

    print(f"Dataset generado: {ruta}")
    print(f"Registros: {len(df)} | Variables: {df.shape[1]}")
    print(f"Nulos en gasto_promedio_mxn: {df['gasto_promedio_mxn'].isna().sum()}")
    print(f"Filas duplicadas: {df.duplicated().sum()}")
    print(f"Tasa de recompra: {df['compro_ultima_campana'].mean():.1%}")


if __name__ == "__main__":
    main()
