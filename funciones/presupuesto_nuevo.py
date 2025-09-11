import streamlit as st
import pandas as pd
from .presupuesto_utils import (
    load_catalogo, save_presupuesto, empty_datos_df, empty_detalle_df,
    catalog_selector_with_qty, today_str
)

DEFAULT_ITEM = "01.01"
QTY_KEY = "nuevo_qty_map"            # {Codigo(str): cantidad(float)}
PREVIEW_KEY = "nuevo_preview_full"   # DataFrame con columnas visibles

def _build_preview(catalogo: pd.DataFrame, qty_map: dict):
    """
    Construye la vista previa (Codigo, Resumen, Ud, Precio, Fecha, cantidad)
    a partir del qty_map (solo códigos con cantidad > 0).
    """
    if not qty_map:
        return pd.DataFrame(columns=["Codigo","Resumen","Ud","Precio","Fecha","cantidad"])

    # Mantener solo códigos con cantidad > 0
    positive_codes = [c for c, q in qty_map.items() if q and float(q) > 0]
    if not positive_codes:
        return pd.DataFrame(columns=["Codigo","Resumen","Ud","Precio","Fecha","cantidad"])

    base = catalogo.loc[catalogo["Codigo"].astype(str).isin(positive_codes),
                        ["Codigo","Resumen","Ud","Pres","Fecha"]].copy()
    base["Precio"] = base["Pres"].apply(lambda x: f"${int(round(float(x))):,}".replace(",", ".") if pd.notnull(x) else x)
    base["Codigo"] = base["Codigo"].astype(str)
    base["cantidad"] = base["Codigo"].map(lambda c: float(qty_map.get(c, 0)))

    return base[["Codigo","Resumen","Ud","Precio","Fecha","cantidad"]].sort_values("Codigo").reset_index(drop=True)

def render_presupuesto_nuevo():
    st.title("📦 Nuevo Presupuesto")

    # 1) Nombre del presupuesto
    nombre = st.text_input("Nombre del presupuesto (carpeta en 'presupuestos')", placeholder="Ej: Casa_Los_Alerces")
    if not nombre.strip():
        st.info("Ingresa un nombre para continuar.")
        return
    nombre = nombre.strip()

    # Reinicio de estado si cambia el nombre
    if "nuevo_nombre" not in st.session_state or st.session_state["nuevo_nombre"] != nombre:
        st.session_state["nuevo_nombre"] = nombre
        st.session_state[QTY_KEY] = {}
        st.session_state[PREVIEW_KEY] = pd.DataFrame(columns=["Codigo","Resumen","Ud","Precio","Fecha","cantidad"])
        # limpiar selects/editores previos del catálogo
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and k.startswith("nuevo_min_"):
                del st.session_state[k]

    # 2) Datos del PRIMER ÍTEM (Item fijo = 01.01)
    st.subheader("Datos del primer ítem (Item = 01.01)")
    col1, col2 = st.columns([2,1])
    with col1:
        partida = st.text_input("Partida (descripción)", value=st.session_state.get("np_partida", ""))
    with col2:
        fecha_str = st.text_input("Fecha (DD/MM/YYYY)", value=st.session_state.get("np_fecha", today_str()))
    st.session_state["np_partida"] = partida
    st.session_state["np_fecha"] = fecha_str

    catalogo = load_catalogo()
    uds_unique = [""] + sorted(catalogo["Ud"].dropna().unique().tolist())
    col3, col4, col5 = st.columns([1,1,1])
    with col3:
        cant_tipo = st.selectbox("Cantidad tipo (unidad)", options=uds_unique, index=0, key="np_cant_tipo")
    with col4:
        cant_num = st.number_input("Cantidad número", min_value=0.0, value=float(st.session_state.get("np_cant_num", 1.0)), step=1.0, key="np_cant_num_in")
    with col5:
        moneda = st.number_input("Moneda", min_value=0.0, value=float(st.session_state.get("np_moneda", 1.0)), step=1.0, key="np_moneda_in")
    st.session_state["np_cant_num"] = cant_num
    st.session_state["np_moneda"] = moneda

    # Mantener datos_df (fila única 01.01)
    datos_df = empty_datos_df()
    datos_df.loc[len(datos_df)] = {
        "Item": DEFAULT_ITEM,
        "Partida": partida.strip(),
        "Fecha": str(fecha_str).strip(),
        "cantidad tipo": cant_tipo,
        "cantidad numero": float(cant_num),
        "moneda": float(moneda),
    }
    st.session_state["nuevo_datos_df"] = datos_df

    # 3) Catálogo con cantidad (0 default). 'Aplicar selección' acumula al qty_map global
    st.subheader("Selecciona materiales desde el catálogo (ajusta 'cantidad')")
    edited, current_codes, qty_key = catalog_selector_with_qty(catalogo, state_key_prefix="nuevo_min", qty_key=QTY_KEY)

    # Botón: Aplicar selección (acumula cantidades de la vista actual)
    if st.button("✅ Aplicar selección"):
        qty_map = st.session_state[qty_key]
        # tomar cantidades de la vista actual y guardarlas en el mapa global
        temp = edited[["Codigo","cantidad"]].copy()
        temp["Codigo"] = temp["Codigo"].astype(str)
        temp["cantidad"] = pd.to_numeric(temp["cantidad"], errors="coerce").fillna(0)

        for _, r in temp.iterrows():
            code = r["Codigo"]
            qty = float(r["cantidad"])
            # Actualiza valor del código (no borres otros códigos de otras categorías)
            qty_map[code] = qty

        st.session_state[qty_key] = qty_map
        # Reconstruir preview desde el mapa global
        st.session_state[PREVIEW_KEY] = _build_preview(catalogo, qty_map)
        st.success("Selección aplicada (acumulada).")

    # 4) Vista previa (editable en 'cantidad'); cambios se sincronizan al mapa global
    st.markdown("### Detalle actual (vista previa)")
    preview_full = st.session_state.get(PREVIEW_KEY, pd.DataFrame(columns=["Codigo","Resumen","Ud","Precio","Fecha","cantidad"]))
    if preview_full is not None and not preview_full.empty:
        edited_preview = st.data_editor(
            preview_full,
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={
                "Codigo": st.column_config.TextColumn("Codigo", disabled=True),
                "Resumen": st.column_config.TextColumn("Resumen", disabled=True),
                "Ud": st.column_config.TextColumn("Ud", disabled=True),
                "Precio": st.column_config.TextColumn("Precio", disabled=True),
                "Fecha": st.column_config.TextColumn("Fecha", disabled=True),
                "cantidad": st.column_config.NumberColumn("cantidad", step=1.0, min_value=0.0),
            },
            key="nuevo_preview_editor",
        )
        # Sincroniza cambios de cantidad desde la vista previa al mapa global
        sync_temp = edited_preview[["Codigo","cantidad"]].copy()
        sync_temp["Codigo"] = sync_temp["Codigo"].astype(str)
        sync_temp["cantidad"] = pd.to_numeric(sync_temp["cantidad"], errors="coerce").fillna(0)
        qty_map = st.session_state[QTY_KEY]
        for _, r in sync_temp.iterrows():
            qty_map[r["Codigo"]] = float(r["cantidad"])
        st.session_state[QTY_KEY] = qty_map
        st.session_state[PREVIEW_KEY] = edited_preview

        # 5) Guardar presupuesto (debajo de la vista previa)
        if st.button("💾 Guardar presupuesto"):
            if not partida.strip():
                st.error("Debes ingresar la Partida del ítem 01.01.")
                return
            if not str(fecha_str).strip():
                st.error("Debes ingresar la Fecha en formato DD/MM/YYYY.")
                return

            datos_to_save = st.session_state["nuevo_datos_df"].copy()

            # Construir detalle.csv desde qty_map (solo > 0)
            qty_map = st.session_state[QTY_KEY]
            positive = [(c, q) for c, q in qty_map.items() if q and float(q) > 0]
            if positive:
                detalle_to_save = pd.DataFrame(positive, columns=["Codigo","cantidad"])
                detalle_to_save["item"] = DEFAULT_ITEM
                detalle_to_save = detalle_to_save[["item","Codigo","cantidad"]]
            else:
                detalle_to_save = empty_detalle_df()

            # Tipos seguros
            if "Fecha" in datos_to_save.columns:
                datos_to_save["Fecha"] = datos_to_save["Fecha"].astype(str)
            for c in ["cantidad numero","moneda"]:
                if c in datos_to_save.columns:
                    datos_to_save[c] = pd.to_numeric(datos_to_save[c], errors="coerce").fillna(0)
            if not detalle_to_save.empty and "cantidad" in detalle_to_save.columns:
                detalle_to_save["cantidad"] = pd.to_numeric(detalle_to_save["cantidad"], errors="coerce").fillna(0)

            save_presupuesto(nombre, datos_to_save, detalle_to_save)
            st.success(f"Presupuesto **{nombre}** creado y guardado.")
    else:
        st.caption("Ajusta cantidades (> 0) y presiona **✅ Aplicar selección** para verlas aquí.")
