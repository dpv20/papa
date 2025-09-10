import streamlit as st
from pathlib import Path

# --- Configuración global ---
st.set_page_config(page_title="Construction Budget", layout="wide")
logo_path = Path("media/pavez_P_logo.png")
logo2_path = Path("media/pavez_logo.png")

# --- Sidebar ---
with st.sidebar:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    st.title("Menú")

    view = st.radio(
        "Ir a:",
        [
            "🏠 Home",
            "📦 Presupuesto",
            "➕ Agregar ítem",
            "✏️ Modificar/Eliminar",
            "🗂️ Agregar Categoría"
        ],
        index=0
    )
# --- Rutas / Vistas ---
def render_home():
    st.title("Bienvenido 👋")
    st.write(
        """
        Esta es tu app de **gestión de presupuesto de construcción**.
        Usa el menú lateral para navegar entre las funciones.
        """
    )
    if logo2_path.exists():
        st.image(str(logo2_path), caption="Pavez", use_container_width=False)

def render_add_item():
    st.title("➕ Agregar ítem")
    st.info("Funcionalidad en construcción.")

def render_edit_delete_item():
    st.title("✏️ Modificar / Eliminar ítem")
    st.info("Funcionalidad en construcción.")

# --- Router simple ---
if view == "🏠 Home":
    render_home()
elif view == "📦 Presupuesto":
    from funciones.presupuesto import render_presupuesto
    render_presupuesto()
elif view == "➕ Agregar ítem":
    from funciones.add_item import render_add_item
    render_add_item()
elif view == "✏️ Modificar/Eliminar":
    from funciones.modify_item import render_modify_item
    render_modify_item()
elif view == "🗂️ Agregar Categoría":
    from funciones.agregar_categoria import render_add_category
    render_add_category()