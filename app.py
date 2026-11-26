import streamlit as st

from modules.data_loader import load_csv
from modules.theme import apply_theme

st.set_page_config(
    page_title="DataMind AI | Smart Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# Application branding
welcome = st.container(border=True)

with welcome:
    st.markdown("### 🧠 DataMind AI")
    st.markdown("**Your Intelligent Data Analytics Platform**")
    st.write(
        "Transform raw data into meaningful insights. "
        "Clean, analyze, visualize and explore your data "
        "with one intelligent platform."
    )

# Shared dataset uploader
with st.sidebar:
    st.markdown("<div style='text-align:center; font-size:42px;'>🧠</div>", unsafe_allow_html=True)
    st.markdown("## DataMind AI")
    st.caption("INTELLIGENT ANALYTICS")

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your CSV dataset",
        type=["csv"]
    )

    st.divider()

    st.caption("⚡ Powered by Python & DuckDB")
    st.caption("Version 1.0")

# Store uploaded dataset for all pages
if uploaded_file is not None:
    try:
        df = load_csv(uploaded_file)

        if df is not None:
            st.session_state["uploaded_df"] = df
            st.success("Dataset uploaded successfully!")
        else:
            st.session_state["uploaded_df"] = None

    except Exception as error:
        st.session_state["uploaded_df"] = None
        st.error(f"Unable to load dataset: {error}")
else:
    st.session_state["uploaded_df"] = None

st.divider()

if st.session_state.get("uploaded_df") is None:
    st.info("Upload a CSV file using the sidebar to get started.")
