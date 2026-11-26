
import pandas as pd
import streamlit as st

def load_csv(uploaded_file):
    """Read an uploaded CSV file safely."""

    try:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.warning("The uploaded CSV file is empty.")
            return None

        if len(df.columns) == 0:
            st.warning("No columns found in the CSV file.")
            return None

        return df

    except Exception as error:
        st.error(f"Unable to read CSV file: {error}")
        return None