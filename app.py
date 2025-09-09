import streamlit as st
import pandas as pd

# Load data from the newly created CSV
@st.cache_data
def load_data():
    return pd.read_csv('construction_budget_data.csv')

# Initialize session state for selected Codigos
if 'selected_codigos' not in st.session_state:
    st.session_state['selected_codigos'] = set()

# Load the CSV data
df = load_data()

# Streamlit UI
st.title("📐 Construction Budget Manager")

# Filters
selected_cat = st.selectbox("Select Category", df['Categoria'].unique())
filtered_df = df[df['Categoria'] == selected_cat]

selected_subcat = st.selectbox("Select Subcategory", filtered_df['Subcategoria'].dropna().unique())
filtered_df = filtered_df[filtered_df['Subcategoria'] == selected_subcat].copy()

# Search bar with autocompletion only using 'Resumen'
search_options = filtered_df['Resumen'].tolist()
search_query = st.selectbox("🔍 Search by name:", options=[""] + sorted(set(search_options)), index=0)

if search_query:
    search_query_lower = search_query.lower()
    filtered_df = filtered_df[
        filtered_df['Resumen'].str.lower().str.contains(search_query_lower)
    ].copy()

# Pre-fill selection state from session
filtered_df['Select'] = filtered_df['Codigo'].isin(st.session_state['selected_codigos'])

st.write("### Select Items")
selection_event = st.data_editor(
    filtered_df[['Select', 'Codigo', 'Resumen', 'Ud', 'Pres', 'Fecha']],
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="editor",
    disabled=[False, True, True, True, True, True]  # Allow only 'Select' column to be edited
)

# Button to apply selection and update session state
if st.button("✅ Apply Selection"):
    selected_now = set(selection_event[selection_event['Select']]['Codigo'])
    # Only keep codes that are selected across all categories
    st.session_state['selected_codigos'].difference_update(filtered_df['Codigo'])
    st.session_state['selected_codigos'].update(selected_now)

# Show cumulative selected items
selected_df = df[df['Codigo'].isin(st.session_state['selected_codigos'])]
if not selected_df.empty:
    st.write("### Cumulative Selected Items")
    st.dataframe(selected_df[['Codigo', 'Resumen', 'Ud', 'Pres', 'Fecha']])

    st.write("### Total")
    st.write(f"${selected_df['Pres'].sum():,.2f}")
