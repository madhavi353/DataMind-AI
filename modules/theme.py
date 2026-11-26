import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #08111F 0%, #0B1F33 100%);
            color: #E5F3FF;
        }

        .block-container {
            padding-top: 2rem;
            max-width: 1100px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #091526 0%, #102A43 100%);
            border-right: 1px solid rgba(56, 189, 248, 0.15);
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(120deg, #102A50, #123B65, #075985);
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 35px rgba(0,0,0,0.3);
            padding: 18px 18px 8px 18px;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p {
            color: #38BDF8;
            text-align: center;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #102A50, #0B3A5B);
            padding: 18px;
            border-radius: 14px;
            border: 1px solid rgba(56, 189, 248, 0.38);
            box-shadow: 0 8px 24px rgba(2, 132, 199, 0.12);
        }

        [data-testid="stMetricLabel"] {
            color: #BAE6FD;
        }

        [data-testid="stMetricValue"] {
            color: #38BDF8;
        }

        h1, h2, h3, h4, p, label, span {
            color: #E5F3FF;
        }

        .stTextInput input, .stTextArea textarea,
        [data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input {
            background-color: #0F2740 !important;
            color: #E5F3FF !important;
            border-color: rgba(56, 189, 248, 0.28) !important;
        }

        .stButton > button,
        [data-testid="stDownloadButton"] > button {
            background: linear-gradient(135deg, #0EA5E9, #2563EB);
            color: white;
            border: 0;
            border-radius: 10px;
            font-weight: 600;
        }

        .stButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover {
            background: linear-gradient(135deg, #38BDF8, #3B82F6);
            color: white;
        }

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            border: 1px solid rgba(56, 189, 248, 0.18);
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
