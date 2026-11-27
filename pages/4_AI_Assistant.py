import streamlit as st
import plotly.express as px

from modules.theme import apply_theme
from modules.free_assistant import analyze_question

st.set_page_config(layout="wide")
apply_theme()

st.title("🤖 DataMind AI Assistant")
st.caption("Ask questions about your uploaded dataset.")

df = st.session_state.get("uploaded_df")

if df is None:
    st.warning("Please upload a CSV file from the sidebar.")
    st.stop()

if "free_chat_history" not in st.session_state:
    st.session_state["free_chat_history"] = []

if "free_latest_result" not in st.session_state:
    st.session_state["free_latest_result"] = None

# Display conversation
for message in st.session_state["free_chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested questions
st.subheader("Try asking")

suggestions = [
    "Show a preview of the dataset",
    "How many rows and columns are in the dataset?",
    "Show column names",
    "Show missing values",
    "Show unique values"
]

numeric_columns = df.select_dtypes(include="number").columns.tolist()
categorical_columns = df.select_dtypes(
    include=["object", "category", "string"]
).columns.tolist()

if numeric_columns:
    suggestions.append(f"What is the highest {numeric_columns[0]}?")
    suggestions.append(f"What is the average {numeric_columns[0]}?")

if categorical_columns and numeric_columns:
    suggestions.append(
        f"Show {numeric_columns[0]} by {categorical_columns[0]}"
    )

cols = st.columns(2)

for i, suggestion in enumerate(suggestions):
    if cols[i % 2].button(suggestion, key=f"suggestion_{i}"):
        st.session_state["pending_question"] = suggestion
        st.rerun()

question = st.chat_input("Ask something about your dataset...")

if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state["free_chat_history"].append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Analyzing your data..."):
                response = analyze_question(df, question)

            st.markdown(response["answer"])

            result = response.get("data")

            if result is not None:
                st.dataframe(result, use_container_width=True)

                st.session_state["free_latest_result"] = result

            if response.get("chart") and result is not None:
                fig = px.bar(
                    result,
                    x=response["x"],
                    y=response["y"],
                    title=f'{response["y"]} by {response["x"]}',
                    text_auto=True
                )

                st.plotly_chart(fig, use_container_width=True)

            st.session_state["free_chat_history"].append({
                "role": "assistant",
                "content": response["answer"]
            })

        except Exception as error:
            st.error(f"Analysis error: {error}")

latest_result = st.session_state.get("free_latest_result")

if latest_result is not None:
    st.download_button(
        "Download Analysis Results",
        data=latest_result.to_csv(index=False).encode("utf-8"),
        file_name="datamind_analysis.csv",
        mime="text/csv"
    )

if st.button("Clear Conversation"):
    st.session_state["free_chat_history"] = []
    st.session_state["free_latest_result"] = None
    st.rerun()
