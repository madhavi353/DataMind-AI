import streamlit as st

from modules.theme import apply_theme
from modules.analytics import clean_dataset

st.set_page_config(layout="wide")
apply_theme()

st.title("🧹 Data Cleaning")
st.caption("Handle missing values and remove duplicate records.")

df = st.session_state.get("uploaded_df")

if df is None:
    st.warning("Please upload a CSV file from the sidebar.")
    st.stop()

st.subheader("Original Dataset")
st.dataframe(df.head(100), use_container_width=True)

st.write(f"Missing values: {df.isnull().sum().sum()}")
st.write(f"Duplicate rows: {df.duplicated().sum()}")

strategy = st.selectbox(
    "Choose missing value strategy",
    ["median", "mean", "mode"]
)

if st.button("Clean Dataset"):
    try:
        cleaned_df = clean_dataset(df.copy(), strategy=strategy)

        st.session_state["cleaned_df"] = cleaned_df

        st.success("Dataset cleaned successfully!")

    except Exception as error:
        st.error(f"Cleaning failed: {error}")

cleaned_df = st.session_state.get("cleaned_df")

if cleaned_df is not None:
    st.divider()
    st.subheader("Cleaned Dataset")

    col1, col2 = st.columns(2)

    col1.metric("Original Rows", df.shape[0])
    col2.metric("Cleaned Rows", cleaned_df.shape[0])

    st.dataframe(cleaned_df, use_container_width=True)

    st.download_button(
        "Download Cleaned CSV",
        data=cleaned_df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv"
    )
