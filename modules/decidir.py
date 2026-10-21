"""Pestaña 6: decisión comercial dinámica por segmento."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.prescribir import MATRIZ_COMERCIAL, RANGOS, SEGMENTOS, evaluar_clientes

# Segmento de probabilidad media: es el que se atiende con reactivación y el
# que requiere demostrar rentabilidad antes de escalar.
SEGMENTO_REACTIVACION = "Moderada"

# Supuestos económicos de la promoción de reactivación. Se dejan explícitos
# para que el equipo comercial pueda auditarlos y actualizarlos sin tocar la
# lógica de cálculo.
SUPUESTO_DESCUENTO = 0.10  # 10% de descuento sobre el ticket promedio.
SUPUESTO_MARGEN_BIENES = 0.70  # Margen bruto: alimentos ≈ 30% del precio.
PRECIO_POSTRE = 45.0  # Precio de referencia del postre de cortesía.
COSTO_POSTRE = PRECIO_POSTRE * (1 - SUPUESTO_MARGEN_BIENES)
COSTO_CONTACTO = 2.0  # Pauta SMS/Meta por cliente contactado.
PCT_CONTROL = 0.20  # Proporción del segmento que queda sin incentivo.
META_UPLIFT_PP = 20.0  # Meta del KPI de la campaña (puntos porcentuales).


def _proyeccion_reactivacion(subconjunto: pd.DataFrame) -> dict[str, float]:
    """Proyecta costo, margen y punto de equilibrio del piloto de reactivación.

    El segmento de probabilidad media se atiende con un 10% de descuento más
    un postre de cortesía. Sólo el 80% del segmento recibe la oferta; el resto
    queda como grupo de control para medir la recompra incremental real.

    Returns
    -------
    dict
        Grupos del experimento, costo de la promoción, margen esperado de
        ganancia, ROMI y uplift mínimo necesario para cubrir la inversión.
    """
    n = len(subconjunto)
    ticket = float(subconjunto["gasto_promedio_mxn"].mean())
    probabilidad = float(subconjunto["probabilidad_compra"].mean())

    n_control = int(round(n * PCT_CONTROL))
    n_tratamiento = n - n_control

    # Lo que deja cada compra atendida con la oferta, ya descontado el incentivo.
    descuento_unitario = ticket * SUPUESTO_DESCUENTO
    margen_unitario = (
        ticket
        - descuento_unitario
        - ticket * (1 - SUPUESTO_MARGEN_BIENES)
        - COSTO_POSTRE
    )
    redenciones = n_tratamiento * probabilidad

    costo_incentivo = redenciones * (descuento_unitario + COSTO_POSTRE)
    costo_pauta = n_tratamiento * COSTO_CONTACTO
    costo_campana = costo_incentivo + costo_pauta

    margen_bruto = redenciones * ticket * SUPUESTO_MARGEN_BIENES
    margen_esperado = margen_bruto - costo_campana
    romi = margen_esperado / costo_campana if costo_campana else 0.0

    # Recompra incremental que debe generar la oferta para no perder margen.
    uplift_minimo = (
        costo_campana / (n_tratamiento * margen_unitario)
        if n_tratamiento > 0 and margen_unitario > 0
        else 0.0
    )

    return {
        "n": n,
        "n_tratamiento": n_tratamiento,
        "n_control": n_control,
        "ticket": ticket,
        "probabilidad": probabilidad,
        "redenciones": redenciones,
        "costo_incentivo": costo_incentivo,
        "costo_pauta": costo_pauta,
        "costo_campana": costo_campana,
        "margen_unitario": margen_unitario,
        "margen_bruto": margen_bruto,
        "margen_esperado": margen_esperado,
        "romi": romi,
        "uplift_minimo": uplift_minimo,
    }


def _render_economia_reactivacion(subconjunto: pd.DataFrame) -> None:
    """Muestra costo, margen, KPI y grupo de control de la reactivación."""
    proy = _proyeccion_reactivacion(subconjunto)
    n = proy["n"]
    ticket = proy["ticket"]
    probabilidad = proy["probabilidad"]
    n_tratamiento = proy["n_tratamiento"]
    n_control = proy["n_control"]
    redenciones = proy["redenciones"]
    costo_incentivo = proy["costo_incentivo"]
    costo_pauta = proy["costo_pauta"]
    costo_campana = proy["costo_campana"]
    margen_unitario = proy["margen_unitario"]
    margen_bruto = proy["margen_bruto"]
    margen_esperado = proy["margen_esperado"]
    romi = proy["romi"]
    uplift_minimo = proy["uplift_minimo"]

    st.divider()
    st.markdown("#### 💰 Economía de la promoción: costo, margen y KPI")
    st.caption(
        "Proyección de la oferta «10% + postre de cortesía» sobre el segmento "
        "de probabilidad media. Las cifras dimensionan la campaña y justifican "
        "una prueba piloto, pero no prueban por sí solas que sea rentable: "
        "esa rentabilidad se mide con el grupo de control."
    )

    col_costo, col_margen, col_kpi = st.columns(3)
    col_costo.metric(
        "Costo estimado de la promoción",
        f"${costo_campana:,.0f} MXN",
        help=(
            f"**Incentivo:** ${costo_incentivo:,.0f} en {redenciones:.1f} "
            f"redenciones esperadas (${ticket * SUPUESTO_DESCUENTO:,.1f} de "
            f"descuento + ${COSTO_POSTRE:,.1f} de postre por compra).  \n"
            f"**Pauta:** ${costo_pauta:,.0f} para {n_tratamiento} contactos "
            f"(${COSTO_CONTACTO:,.2f} c/u). El {PCT_CONTROL:.0%} del segmento "
            "no recibe incentivo, así que el costo ya viene ajustado."
        ),
        border=True,
    )
    col_margen.metric(
        "Margen esperado de ganancia",
        f"${margen_esperado:,.0f} MXN",
        help=(
            f"Margen bruto de las ventas del grupo tratado (${margen_bruto:,.0f}, "
            f"{SUPUESTO_MARGEN_BIENES:.0%} del ticket) menos la inversión de "
            f"${costo_campana:,.0f}.  \n"
            f"Margen por compra con incentivo: ${margen_unitario:,.1f} "
            f"({margen_unitario / ticket:.0%} del ticket de ${ticket:,.0f}).  \n"
            f"ROMI bruto: {romi:.0%} = margen esperado ÷ inversión."
        ),
        border=True,
    )
    col_kpi.metric(
        "KPI de éxito · uplift mínimo",
        f"+{uplift_minimo * 100:.1f} p.p.",
        help=(
            "Indicador con el que se juzga la campaña: la recompra "
            "incremental que debe generar la oferta para cubrir exactamente "
            f"la inversión de ${costo_campana:,.0f}.  \n"
            f"Meta de la campaña: ≥ +{META_UPLIFT_PP:.0f} p.p. de recompra a "
            "30 días, medida contra el grupo de control."
        ),
        border=True,
    )

    col_kpi_detalle, col_control = st.columns(2)
    with col_kpi_detalle:
        with st.container(border=True):
            st.markdown("**📊 KPI para medir el éxito de la campaña**")
            st.markdown(
                "\n".join(
                    [
                        (
                            "- **Principal:** uplift de recompra a 30 días = "
                            "tasa de recompra del grupo con incentivo − tasa del "
                            "grupo de control, en puntos porcentuales (p.p.)."
                        ),
                        (
                            f"- **Meta:** ≥ **+{META_UPLIFT_PP:.0f} p.p.**, por "
                            "encima del break-even de "
                            f"+{uplift_minimo * 100:.1f} p.p."
                        ),
                        (
                            "- **Secundario:** costo por recompra incremental = "
                            f"${costo_campana:,.0f} ÷ recompras incrementales, "
                            "que debe quedar por debajo de "
                            f"${margen_unitario:,.1f} (margen por compra)."
                        ),
                        (
                            "- **Lectura:** se calcula a los 30 días del envío "
                            "y se reporta por grupo, no sobre el segmento "
                            "completo."
                        ),
                    ]
                )
            )
    with col_control:
        with st.container(border=True):
            st.markdown("**🧪 Grupo de control (experimento piloto)**")
            st.markdown(
                "\n".join(
                    [
                        (
                            f"- **Tratamiento:** {n_tratamiento} clientes "
                            f"({n_tratamiento / n:.0%}) con la oferta de "
                            "reactivación."
                        ),
                        (
                            f"- **Control:** {n_control} clientes "
                            f"({PCT_CONTROL:.0%}) que **no reciben el "
                            "incentivo**: sólo comunicación de marca."
                        ),
                        (
                            "- **Asignación:** aleatoria y reproducible dentro "
                            "del mismo segmento, para que ambos grupos arranquen "
                            "con la misma probabilidad de compra."
                        ),
                        (
                            "- **Comparación:** a los 30 días se contrasta la "
                            "recompra de un grupo contra la del otro; esa "
                            "diferencia es la evidencia de rentabilidad."
                        ),
                        (
                            "- **Regla de decisión:** escalar al 100% del "
                            "segmento sólo si se cumple la meta del KPI; si no, "
                            "se ajusta la oferta o se descarta."
                        ),
                    ]
                )
            )

    st.markdown("#### ⚖️ Comparación del piloto: con incentivo vs. sin incentivo")
    comparacion = pd.DataFrame(
        [
            {
                "Grupo": "Tratamiento · con incentivo (10% + postre)",
                "Clientes": n_tratamiento,
                "Tasa de partida": probabilidad * 100,
                "Margen por compra": margen_unitario,
            },
            {
                "Grupo": "Control · sin incentivo",
                "Clientes": n_control,
                "Tasa de partida": probabilidad * 100,
                "Margen por compra": ticket * SUPUESTO_MARGEN_BIENES,
            },
        ]
    )
    st.dataframe(
        comparacion,
        width="stretch",
        hide_index=True,
        alt="Comparación del piloto entre el grupo tratado y el grupo de control",
        column_config={
            "Grupo": st.column_config.TextColumn(width="large"),
            "Clientes": st.column_config.NumberColumn(format="%d"),
            "Tasa de partida": st.column_config.NumberColumn(format="%.1f%%"),
            "Margen por compra": st.column_config.NumberColumn(format="$%.2f"),
        },
    )
    st.caption(
        f"Ambos grupos parten de la misma tasa de recompra "
        f"({probabilidad:.1%}) porque la asignación es aleatoria: la diferencia "
        f"que se mida a 30 días es el uplift (KPI). La rentabilidad real se "
        f"calcula como (tasa_incentivo − tasa_control) × {n_tratamiento} × "
        f"${margen_unitario:,.1f} − ${costo_campana:,.0f}; sólo el grupo sin "
        "incentivo permite saber cuánta de esa recompra generó la promoción."
    )

    st.success(
        f"La promoción queda dimensionada: requiere ${costo_campana:,.0f} de "
        f"inversión y proyecta ${margen_esperado:,.0f} de margen neto si se "
        f"sostiene la recompra actual ({probabilidad:.1%}), con "
        f"${margen_unitario:,.1f} de margen por compra (ROMI {romi:.0%}). "
        "Con estas cifras sale a prueba piloto.",
        title="Costo y margen esperado cuantificados",
    )
    st.warning(
        "El margen proyectado es un escenario, todavía no una demostración de "
        f"rentabilidad: asume margen de bienes del {SUPUESTO_MARGEN_BIENES:.0%}, "
        f"un postre de cortesía a ${COSTO_POSTRE:,.1f} de costo (precio "
        f"${PRECIO_POSTRE:.0f}) y pauta de ${COSTO_CONTACTO:,.2f} por contacto, "
        "sin distinguir la recompra incremental de la que ya ocurría. Si el "
        f"descuento llega a clientes que iban a comprar igual, el efecto "
        f"incremental es de −${costo_campana:,.0f}. Por eso la evidencia "
        f"justifica el piloto, no el escalado: con {n} clientes la potencia "
        "estadística es limitada.",
        title="La evidencia aún no demuestra que la promoción sea rentable",
    )
    st.error(
        "No se puede declarar rentable la promoción sin grupo de control: sólo "
        f"el {PCT_CONTROL:.0%} ({n_control} clientes) que no recibe el "
        "incentivo permite comparar contra clientes sin incentivo y separar la "
        "recompra incremental de la que ya ocurriría. Criterio de corte: si a "
        "30 días el uplift queda por debajo "
        f"de +{uplift_minimo * 100:.1f} p.p. (meta +{META_UPLIFT_PP:.0f} p.p.), "
        f"la campaña destruye hasta ${costo_campana:,.0f} de margen y no debe "
        "escalar al 100% del segmento.",
        title="Decisión bloqueada hasta comparar con el grupo de control",
    )


def render(df: pd.DataFrame) -> None:
    """Permite elegir un segmento y muestra la acción comercial recomendada."""
    st.subheader("Decidir: plan de acción por segmento", icon=":material/task_alt:")
    st.caption(
        "Selecciona un segmento para convertir la probabilidad en una acción "
        "concreta, un mensaje listo para enviar y su justificación con datos."
    )

    evaluados = evaluar_clientes(df)
    total = len(evaluados)
    tasa_global = df["compro_ultima_campana"].mean() * 100
    ticket_global = df["gasto_promedio_mxn"].mean()
    frecuencia_global = df["frecuencia_visita_mes"].mean()

    etiquetas = {
        "Alta": f"🥇 Alta prioridad ({RANGOS['Alta']})",
        "Moderada": f"🔄 Prioridad moderada ({RANGOS['Moderada']})",
        "Baja": f"🌱 Prioridad baja ({RANGOS['Baja']})",
    }
    seleccion = st.selectbox(
        "Segmento a atender",
        options=SEGMENTOS,
        format_func=lambda segmento: etiquetas[segmento],
        index=0,
    )

    subconjunto = evaluados[evaluados["segmento"] == seleccion]
    config = MATRIZ_COMERCIAL[seleccion]

    if subconjunto.empty:
        st.warning("Este segmento no tiene clientes en la base actual.")
        return

    n = len(subconjunto)
    share = n / total * 100
    prob_media = subconjunto["probabilidad_compra"].mean() * 100
    ticket = subconjunto["gasto_promedio_mxn"].mean()
    frecuencia = subconjunto["frecuencia_visita_mes"].mean()
    tasa_segmento = subconjunto["compro_ultima_campana"].mean() * 100
    producto = str(subconjunto["producto_favorito"].mode().iloc[0])
    top_share = (
        (subconjunto["producto_favorito"] == producto).mean() * 100
    )
    fin_semana = subconjunto["visita_fin_semana"].mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes en el segmento", f"{n:,}", help=f"{share:.1f}% de la cartera.", border=True)
    col2.metric(
        "Probabilidad media",
        f"{prob_media:.1f}%",
        help="Probabilidad estimada por el modelo.",
        border=True,
    )
    col3.metric(
        "Ticket promedio",
        f"${ticket:,.0f}",
        help="Gasto promedio por visita.",
        border=True,
    )
    col4.metric(
        "Visitas promedio",
        f"{frecuencia:.1f} / mes",
        border=True,
    )


    st.divider()
    st.markdown(f"### {config['emoji']} {config['prioridad']}")

    col_accion, col_logistica = st.columns([1.4, 1])
    with col_accion:
        with st.container(border=True):
            st.markdown("**🎯 Acción concreta**")
            st.write(config["accion"])
            st.markdown("**🎁 Oferta sugerida**")
            st.write(config["oferta"].format(producto=producto.lower()))
            st.markdown("**📣 Canal y momento**")
            st.write(config["canal"])
            st.markdown("**🚩 Objetivo comercial**")
            st.write(config["objetivo"])
    with col_logistica:
        with st.container(border=True):
            st.markdown("**📌 Ficha del segmento**")
            st.write(f"**Rango de probabilidad:** {RANGOS[seleccion]}")
            st.write(f"**Tamaño:** {n:,} clientes ({share:.1f}% de la base)")
            st.write(f"**Producto dominante:** {producto} ({top_share:.0f}% del segmento)")
            st.write(f"**Visitan en fin de semana:** {fin_semana:.0f}%")
            st.write(f"**Recompra histórica del segmento:** {tasa_segmento:.1f}%")

    st.markdown("#### ✉️ Mensaje comercial sugerido")
    st.success(
        config["mensaje"].format(producto=producto.lower()),
        icon="💬",
    )
    st.caption(
        "Sugerencia: personaliza el nombre del cliente y el producto exacto "
        "(por ejemplo, «pay de limón» o «frappé de moka») al momento del envío."
    )

    st.markdown("#### 🔍 Justificación basada en datos")
    delta_prob = prob_media - tasa_global
    delta_ticket = (ticket / ticket_global - 1) * 100
    delta_freq = frecuencia - frecuencia_global
    st.info(
        f"El segmento **{seleccion.lower()}** reúne **{n:,} clientes** "
        f"(**{share:.1f}%** de la cartera) con una probabilidad media de recompra "
        f"de **{prob_media:.1f}%**, es decir, **{delta_prob:+.1f} p.p.** frente al "
        f"promedio general ({tasa_global:.1f}%). Su ticket promedio es "
        f"**${ticket:,.0f}** ({delta_ticket:+.1f}% vs. ${ticket_global:,.0f}) y "
        f"visitan **{frecuencia:.1f} veces al mes** ({delta_freq:+.1f} vs. el "
        f"promedio). El **{top_share:.0f}%** prefiere **{producto.lower()}**, "
        "por eso la oferta se ancla a esa categoría en lugar de descontar todo "
        "el menú."
    )
    st.caption(
        "La tasa de recompra histórica del segmento corresponde a la campaña "
        "anterior; úsala como referencia y no como garantía de la próxima."
    )

    st.markdown("#### 👥 Clientes prioritarios del segmento")
    muestra = (
        subconjunto[
            [
                "id_cliente",
                "producto_favorito",
                "gasto_promedio_mxn",
                "frecuencia_visita_mes",
                "probabilidad_pct",
            ]
        ]
        .sort_values("probabilidad_pct", ascending=False)
        .head(10)
        .rename(
            columns={
                "id_cliente": "Cliente",
                "producto_favorito": "Producto favorito",
                "gasto_promedio_mxn": "Gasto prom.",
                "frecuencia_visita_mes": "Visitas/mes",
                "probabilidad_pct": "Prob. recompra",
            }
        )
    )
    st.dataframe(
        muestra,
        width="stretch",
        hide_index=True,
        column_config={
            "Gasto prom.": st.column_config.NumberColumn(format="$%.0f"),
            "Visitas/mes": st.column_config.NumberColumn(format="%d"),
            "Prob. recompra": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
        },
    )

    valor_esperado = float(
        (subconjunto["probabilidad_compra"] * subconjunto["gasto_promedio_mxn"]).sum()
    )
    st.metric(
        "Valor esperado de recompra del segmento",
        f"${valor_esperado:,.0f} MXN",
        help="Suma de gasto promedio × probabilidad de compra para este segmento.",
        border=True,
    )

    # El segmento de probabilidad media exige demostrar rentabilidad antes de
    # escalar: costo, margen, KPI y grupo de control del piloto.
    if seleccion == SEGMENTO_REACTIVACION:
        _render_economia_reactivacion(subconjunto)
