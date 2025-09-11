import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    # CSV principal
    return pd.read_csv('construction_budget_data.csv')

# Formateador visual CLP (solo para mostrar)
def clp(x):
    try:
        return "$" + f"{int(round(float(x))):,}".replace(",", ".")
    except Exception:
        return x

def render_presupuesto():
    # Estado para selección acumulada
    if 'selected_codigos' not in st.session_state:
        st.session_state['selected_codigos'] = set()

    df = load_data()

    st.title("📐 Construction Budget Manager")

    # ---- Filtros
    selected_cat = st.selectbox("Select Category", df['Categoria'].unique())
    filtered_df = df[df['Categoria'] == selected_cat]

    selected_subcat = st.selectbox(
        "Select Subcategory",
        filtered_df['Subcategoria'].dropna().unique()
    )
    filtered_df = filtered_df[filtered_df['Subcategoria'] == selected_subcat].copy()

    # ---- Búsqueda por Resumen
    search_options = filtered_df['Resumen'].tolist()
    search_query = st.selectbox("🔍 Search by name:", options=[""] + sorted(set(search_options)), index=0)

    if search_query:
        q = search_query.lower()
        filtered_df = filtered_df[filtered_df['Resumen'].str.lower().str.contains(q)].copy()

    # Prellenar selección (no tocamos el dataset original)
    filtered_df['Select'] = filtered_df['Codigo'].isin(st.session_state['selected_codigos'])

    # Vista del editor con precio SOLO visual
    editor_view = filtered_df[['Select', 'Codigo', 'Resumen', 'Ud', 'Pres', 'Fecha']].copy()
    editor_view['Precio'] = editor_view['Pres'].apply(clp)

    st.write("### Select Items")
    selection_event = st.data_editor(
        editor_view[['Select', 'Codigo', 'Resumen', 'Ud', 'Precio', 'Fecha']],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="editor",
        disabled=[False, True, True, True, True, True]
    )

    # Aplicar selección
    if st.button("✅ Apply Selection"):
        selected_now = set(selection_event[selection_event['Select']]['Codigo'])
        st.session_state['selected_codigos'].difference_update(filtered_df['Codigo'])
        st.session_state['selected_codigos'].update(selected_now)

    # Seleccionados acumulados
    selected_df = df[df['Codigo'].isin(st.session_state['selected_codigos'])].copy()
    if not selected_df.empty:
        selected_view = selected_df[['Codigo', 'Resumen', 'Ud', 'Pres', 'Fecha']].copy()
        selected_view['Precio'] = selected_view['Pres'].apply(clp)

        st.write("### Cumulative Selected Items")
        st.dataframe(selected_view[['Codigo', 'Resumen', 'Ud', 'Precio', 'Fecha']], use_container_width=True)

        st.write("### Total")
        total_num = selected_df['Pres'].fillna(0).sum()
        st.write(clp(total_num))
