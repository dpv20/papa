# funciones/agregar_categoria.py
import streamlit as st
import pandas as pd
from pathlib import Path

CATEGORIES_PATH = Path("categorias.csv")

def load_categories():
    if CATEGORIES_PATH.exists():
        return pd.read_csv(CATEGORIES_PATH)
    return pd.DataFrame(columns=["Categoria", "Subcategoria", "Prefijo", "MaxNumero", "Count", "NextCodigo"])

def save_categories(df):
    df.to_csv(CATEGORIES_PATH, index=False)

def render_add_category():
    st.title("🗂️ Agregar Categoría / Subcategoría")

    df = load_categories()

    # --- Formulario arriba ---
    st.subheader("Nueva Categoría/Subcategoría")
    with st.form("add_category_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            categoria = st.text_input("Categoría*", placeholder="Ej: Hormigones y morteros").strip()
        with col2:
            subcategoria = st.text_input("Subcategoría*", placeholder="Ej: Hormigones").strip()
        with col3:
            prefijo = st.text_input("Prefijo*", placeholder="Ej: MAA").strip().upper()

        submitted = st.form_submit_button("Guardar")
        if submitted:
            if not categoria or not subcategoria or not prefijo:
                st.error("Todos los campos son obligatorios.")
            else:
                # Verificar duplicado
                if not df.empty and not df[
                    (df["Categoria"].astype(str).str.strip() == categoria) &
                    (df["Subcategoria"].astype(str).str.strip() == subcategoria)
                ].empty:
                    st.error("Esta combinación Categoría/Subcategoría ya existe.")
                else:
                    # Siempre empezamos en 1
                    numero_inicial = 1
                    ancho = 4
                    next_code = f"{prefijo}{str(numero_inicial).zfill(ancho)}"
                    nuevo = {
                        "Categoria": categoria,
                        "Subcategoria": subcategoria,
                        "Prefijo": prefijo,
                        "MaxNumero": numero_inicial - 1,
                        "Count": 0,
                        "NextCodigo": next_code
                    }
                    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
                    save_categories(df)
                    st.success(f"✅ Agregado: {prefijo} → {categoria} / {subcategoria}")

    # --- Listado abajo ---
    st.subheader("Listado de Categorías/Subcategorías")
    if not df.empty:
        show = (
            df[["Prefijo", "Categoria", "Subcategoria", "Count", "NextCodigo"]]
            .sort_values("Prefijo")
            .reset_index(drop=True)
        )
        st.dataframe(show, use_container_width=True)
    else:
        st.info("Aún no hay categorías registradas.")
