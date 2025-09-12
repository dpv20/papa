import streamlit as st
from pathlib import Path
from funciones.Trans_excel import render as render_crear_excel  # 👈 usa la vista con 3 botones
from funciones.crear_pdf import render_crear_pdf

# --- Configuración global ---
st.set_page_config(page_title="Construction Budget", layout="wide")
logo_path = Path("media/pavez_P_logo.png")
logo2_path = Path("media/pavez_logo.png")

# --- Sidebar ---
with st.sidebar:
    if logo_path.exists():
        st.image(str(logo_path))
    st.title("Menú")

    view = st.radio(
        "Ir a:",
        [
            "🏠 Home",
            "📦 Nuevo Presupuesto",
            "📝 Modificar Presupuesto",
            "➕ Agregar ítem",
            "🛠️ Modificar ítem",         
            "🗂️ Categorías",
            "📊 Crear Excel",
            "🧾 Crear PDF",
        ],
        index=0
    )

# --- Vistas locales ---
def render_home():
    st.title("Bienvenido 👋")
    st.write(
        """
        Esta es tu app de **gestión de presupuesto de construcción**.
        Usa el menú lateral para navegar entre las funciones.
        """
    )
    if logo2_path.exists():
        st.image(str(logo2_path), caption="Pavez")

def render_excel():
    # Delegamos toda la UI de Crear/Mostrar/Descargar al módulo Trans_excel
    render_crear_excel()

# --- Router simple ---
if view == "🏠 Home":
    render_home()

elif view == "📦 Nuevo Presupuesto":
    try:
        from funciones.presupuesto_nuevo import render_presupuesto_nuevo
        render_presupuesto_nuevo()
    except Exception as e:
        st.error(f"No se pudo cargar **Nuevo Presupuesto**: {e}")

elif view == "📝 Modificar Presupuesto":
    try:
        from funciones.modificar_presupuesto import render_modificar_presupuesto
        render_modificar_presupuesto()
    except Exception as e:
        st.error(f"No se pudo cargar **Modificar Presupuesto**: {e}")

elif view == "🛠️ Modificar ítem":  
    try:
        from funciones.modify_item import render_modify_item
        render_modify_item()
    except Exception as e:
        st.error(f"No se pudo cargar **Modificar ítem**: {e}")

elif view == "➕ Agregar ítem":
    try:
        from funciones.add_item import render_add_item
        render_add_item()
    except Exception as e:
        st.error(f"No se pudo cargar **Agregar ítem**: {e}")

elif view == "🗂️ Categorías":
    try:
        from funciones.agregar_categoria import render_add_category
        render_add_category()
    except Exception as e:
        st.error(f"No se pudo cargar **Categorías**: {e}")

elif view == "📊 Crear Excel":
    render_excel()

elif view == "🧾 Crear PDF":
    try:
        render_crear_pdf()
    except Exception as e:
        st.error(f"No se pudo cargar **Crear PDF**: {e}")
