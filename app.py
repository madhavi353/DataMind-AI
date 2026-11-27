
import streamlit as st

from modules.data_loader import load_csv
from modules.theme import apply_theme

# Page configuration
st.set_page_config(
    page_title="DataMind AI | Smart Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Register application pages
pg = st.navigation(
    [
        st.Page(
            "pages/1_Overview.py",
            title="Overview",
            icon="📊",
            default=True
        ),
        st.Page(
            "pages/2_Data_Cleaning.py",
            title="Data Cleaning",
            icon="🧹"
        ),
        st.Page(
            "pages/3_SQL_Explorer.py",
            title="SQL Explorer",
            icon="🗄️"
        ),
        st.Page(
            "pages/4_AI_Assistant.py",
            title="AI Assistant",
            icon="🤖"
        ),
        st.Page(
            "pages/5_Reports.py",
            title="Reports",
            icon="📄"
        )
    ],
    position="sidebar",
    expanded=True
)

# Apply blue-black theme
apply_theme()

# Application branding
with st.container(border=True):
    st.markdown("### 🧠 DataMind AI")
    st.markdown("**Your Intelligent Data Analytics Platform**")
    st.write(
        "Transform raw data into meaningful insights. "
        "Clean, analyze, visualize and explore your data "
        "with one intelligent platform."
    )

# Shared CSV uploader
with st.sidebar:
    st.markdown(
        "<div style='text-align:center; font-size:42px;'>🧠</div>",
        unsafe_allow_html=True
    )
    st.markdown("## DataMind AI")
    st.caption("INTELLIGENT ANALYTICS")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your CSV dataset",
        type=["csv"],
        key="main_csv_uploader"
    )

    st.divider()
    st.caption("⚡ Powered by Python & DuckDB")
    st.caption("Version 1.0")

# Share dataset across all pages
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

if st.session_state.get("uploaded_df") is None:
    st.info("Upload a CSV file using the sidebar to get started.")

# Run the selected page
pg.run()
