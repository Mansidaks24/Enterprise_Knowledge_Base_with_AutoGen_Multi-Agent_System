import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000"


def render_history():

    # ======================================
    # HEADER
    # ======================================

    st.markdown(
        '<div class="section-title">🧠 Query Intelligence History</div>',
        unsafe_allow_html=True
    )

    # ======================================
    # DESCRIPTION
    # ======================================

    st.markdown("""
    <div class="glass-card">

    View previously processed enterprise queries,
    orchestration metadata, confidence scores,
    and session intelligence.

    </div>
    """, unsafe_allow_html=True)

    # ======================================
    # FETCH HISTORY
    # ======================================

    try:

        response = requests.get(
            f"{API_URL}/history"
        )

        data = response.json()

        history_data = data.get(
            "history",
            []
        )

    except Exception as e:

        st.error(str(e))

        history_data = []

    # ======================================
    # EMPTY STATE
    # ======================================

    if not history_data:

        st.info(
            "No query history available."
        )

        return

    # ======================================
    # SEARCH
    # ======================================

    search_query = st.text_input(
        "🔍 Search Query History"
    )

    # ======================================
    # PROCESS HISTORY
    # ======================================

    rows = []

    for item in history_data:

        try:

            confidence = item[
                "processing_steps"
            ]["synthesis"][
                "confidence_score"
            ]

        except:

            confidence = 0

        rows.append({

            "Query":
                item["query"],

            "Timestamp":
                item["metadata"]["timestamp"],

            "Confidence":
                confidence,

            "Session ID":
                item["metadata"][
                    "session_id"
                ][:8]
        })

    df = pd.DataFrame(rows)

    # ======================================
    # FILTER
    # ======================================

    if search_query:

        df = df[
            df["Query"]
            .str.contains(
                search_query,
                case=False
            )
        ]

    # ======================================
    # STATS
    # ======================================

    stat_col1, stat_col2, stat_col3 = st.columns(3)

    with stat_col1:

        st.metric(
            "Total Queries",
            len(df)
        )

    with stat_col2:

        avg_conf = round(
            df["Confidence"].mean(),
            2
        )

        st.metric(
            "Avg Confidence",
            f"{avg_conf}%"
        )

    with stat_col3:

        unique_sessions = (
            df["Session ID"]
            .nunique()
        )

        st.metric(
            "Unique Sessions",
            unique_sessions
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================
    # HISTORY TABLE
    # ======================================

    st.markdown("""
    <div class="glass-card">
    """, unsafe_allow_html=True)

    st.markdown("""
    <h3 style="
        margin-top:0;
        color:white;
    ">
    📄 Query Records
    </h3>
    """, unsafe_allow_html=True)

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # ======================================
    # RECENT QUERIES
    # ======================================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
    """, unsafe_allow_html=True)

    st.markdown("""
    <h3 style="
        margin-top:0;
        color:white;
    ">
    ⚡ Recent Queries
    </h3>
    """, unsafe_allow_html=True)

    recent_queries = df.head(5)

    for _, row in recent_queries.iterrows():

        confidence_color = (
            "#22C55E"
            if row["Confidence"] >= 80
            else "#F59E0B"
        )

        st.markdown(f"""
        <div class="log-card">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div>

                <div style="
                    color:white;
                    font-size:15px;
                    margin-bottom:6px;
                ">
                {row['Query']}
                </div>

                <div style="
                    color:#94A3B8;
                    font-size:12px;
                ">
                {row['Timestamp']}
                </div>

            </div>

            <div style="
                color:{confidence_color};
                font-weight:600;
            ">
            {row['Confidence']}%
            </div>

        </div>

        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )