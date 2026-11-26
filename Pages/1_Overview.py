import streamlit as st
import pandas as pd

from modules.theme import apply_theme
from modules.analytics import generate_data_insights
from modules.visualizations import recommend_charts, create_chart

st.set_page_config(layout="wide")
apply_theme()

st.title("📊 Dataset Overview")
st.caption("Explore your dataset and discover useful insights.")

df = st.session_state.get("uploaded_df")

if df is None:
    st.warning("Please upload a CSV file from the sidebar.")
    st.stop()

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rows", f"{df.shape[0]:,}")
col2.metric("Total Columns", f"{df.shape[1]:,}")
col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")
col4.metric("Duplicate Rows", f"{df.duplicated().sum():,}")

# Dataset preview
st.divider()
st.header("Dataset Preview")
st.dataframe(df.head(100), use_container_width=True)

# Column information
st.header("Column Information")

info_df = pd.DataFrame({
    "Column": df.columns,
    "Data Type": df.dtypes.astype(str).values,
    "Missing Values": df.isnull().sum().values,
    "Unique Values": df.nunique().values
})

st.dataframe(info_df, use_container_width=True, hide_index=True)

# Statistical summary
st.divider()
st.header("Statistical Analysis")

numeric_df = df.select_dtypes(include="number")

if not numeric_df.empty:
    st.dataframe(
        numeric_df.describe().round(2),
        use_container_width=True
    )
else:
    st.info("No numerical columns found.")

# Automatic insights
st.divider()
st.header("🤖 Automatic Data Insights")

for insight in generate_data_insights(df):
    st.info(insight)

# Automatic charts
st.divider()
st.header("📈 Smart Data Visualization")

recommendations = recommend_charts(df)

if recommendations:
    for i in range(0, len(recommendations), 2):
        cols = st.columns(2)

        for j, recommendation in enumerate(recommendations[i:i + 2]):
            with cols[j]:
                st.subheader(recommendation["title"])

                try:
                    fig = create_chart(df, recommendation)

                    if fig is not None:
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"overview_chart_{i}_{j}"
                        )

                except Exception as error:
                    st.warning(f"Chart error: {error}")
else:
    st.info("Not enough suitable columns for automatic charts.")
