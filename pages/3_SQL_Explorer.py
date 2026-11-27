import streamlit as st

from modules.theme import apply_theme
from modules.sql_engine import execute_query

st.set_page_config(layout="wide")
apply_theme()

st.title("🗄️ SQL Explorer")
st.caption("Query your uploaded CSV using SQL.")

df = st.session_state.get("uploaded_df")

if df is None:
    st.warning("Please upload a CSV file from the sidebar.")
    st.stop()

st.info("Your dataset is available as uploaded_data.")

query = st.text_area(
    "Write your SQL query",
    value="SELECT * FROM uploaded_data LIMIT 10;",
    height=180
)

if st.button("▶ Execute SQL Query"):
    try:
        result = execute_query(df, query)

        st.session_state["sql_result"] = result

        st.success(f"Query completed: {len(result)} rows returned.")

    except Exception as error:
        st.error(f"SQL Error: {error}")

result = st.session_state.get("sql_result")

if result is not None:
    st.subheader("Query Results")

    st.dataframe(result, use_container_width=True)

    st.download_button(
        "Download SQL Results",
        data=result.to_csv(index=False).encode("utf-8"),
        file_name="sql_results.csv",
        mime="text/csv"
    )
