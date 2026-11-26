import streamlit as st

from modules.theme import apply_theme
from modules.pdf_report import generate_pdf_report

st.set_page_config(layout="wide")
apply_theme()

st.title("📄 Analytics Reports")
st.caption("Generate and download your dataset analytics report.")

df = st.session_state.get("uploaded_df")

if df is None:
    st.warning("Please upload a CSV file from the sidebar.")
    st.stop()

st.subheader("Report Preview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Rows", df.shape[0])
col2.metric("Total Columns", df.shape[1])
col3.metric("Missing Values", df.isnull().sum().sum())

st.write("Your PDF report will contain:")
st.markdown("""
- Dataset overview
- Column information
- Missing values
- Statistical summary
""")

if st.button("Generate PDF Report"):
    try:
        pdf_file = generate_pdf_report(df, {})

        st.download_button(
            "⬇️ Download Analytics Report",
            data=pdf_file.getvalue(),
            file_name="DataMind_AI_Analytics_Report.pdf",
            mime="application/pdf"
        )

        st.success("Your report is ready!")

    except Exception as error:
        st.error(f"Report generation failed: {error}")
