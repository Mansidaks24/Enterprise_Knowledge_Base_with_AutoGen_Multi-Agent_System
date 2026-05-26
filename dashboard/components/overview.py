import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


API_URL = "http://127.0.0.1:8000"


def render_overview():

    # ======================================
    # FETCH LIVE METRICS
    # ======================================

    try:

        metrics = requests.get(
            f"{API_URL}/metrics"
        ).json()

    except:

        metrics = {

            "total_queries": 0,
            "avg_confidence": 0,
            "active_sessions": 0,
            "agents_running": 0
        }

    # ======================================
    # PAGE TITLE
    # ======================================

    st.markdown(
        '<div class="section-title">📊 System Overview</div>',
        unsafe_allow_html=True
    )

    # ======================================
    # KPI METRICS
    # ======================================

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:

        st.metric(
            "Total Queries",
            metrics["total_queries"]
        )

    with metric_col2:

        st.metric(
            "Avg Confidence",
            f"{metrics['avg_confidence']}%"
        )

    with metric_col3:

        st.metric(
            "Active Sessions",
            metrics["active_sessions"]
        )

    with metric_col4:

        st.metric(
            "Agents Running",
            metrics["agents_running"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================
    # TOP GRID
    # ======================================

    left_col, right_col = st.columns([1, 1])

    # ======================================
    # SYSTEM STATUS
    # ======================================

    with left_col:

        st.markdown("""
        <div class="glass-card">
        """, unsafe_allow_html=True)

        st.markdown("""
        <h3 style="
            margin-top:0;
            color:white;
        ">
        📡 System Health
        </h3>
        """, unsafe_allow_html=True)

        try:

            health = requests.get(
                f"{API_URL}/"
            ).json()

            st.markdown(f"""
            <div style="
                margin-top:20px;
                line-height:2;
            ">

            <span style="
                color:#22C55E;
                font-size:16px;
                font-weight:600;
            ">
            ● Backend Online
            </span>

            <br>

            <span style="
                color:#CBD5E1;
            ">
            FastAPI services operational
            </span>

            <br><br>

            <span style="
                color:#94A3B8;
                font-size:14px;
            ">
            Last Sync:
            {health['timestamp']}
            </span>

            </div>
            """, unsafe_allow_html=True)

        except Exception as e:

            st.markdown(f"""
            <div style="
                margin-top:20px;
                line-height:2;
            ">

            <span style="
                color:#EF4444;
                font-size:16px;
                font-weight:600;
            ">
            ● Backend Offline
            </span>

            <br>

            <span style="
                color:#CBD5E1;
            ">
            {str(e)}
            </span>

            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # ======================================
    # RETRIEVER CONFIDENCE
    # ======================================

    with right_col:

        st.markdown("""
        <div class="glass-card">
        """, unsafe_allow_html=True)

        st.markdown("""
        <h3 style="
            margin-top:0;
            color:white;
        ">
        🧠 Retriever Confidence
        </h3>
        """, unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(

            mode="gauge+number",

            value=metrics["avg_confidence"],

            gauge={
                'axis': {
                    'range': [0, 100]
                },

                'bar': {
                    'color': "#7C3AED"
                }
            }
        ))

        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="#111827",

            font_color="white",

            height=250,

            margin=dict(
                l=20,
                r=20,
                t=40,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # ======================================
    # AGENT PERFORMANCE
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
    🤖 Agent Performance
    </h3>
    """, unsafe_allow_html=True)

    agent_df = pd.DataFrame({

        "Agent": [
            "Retriever",
            "Analyst",
            "Fact Checker",
            "Synthesizer",
            "Router"
        ],

        "Activity": [
            95,
            88,
            82,
            91,
            86
        ]
    })

    fig3 = px.bar(

        agent_df,

        x="Agent",

        y="Activity",

        text="Activity"
    )

    fig3.update_layout(

        template="plotly_dark",

        paper_bgcolor="#111827",

        plot_bgcolor="#111827",

        font_color="white",

        height=400,

        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig3,
        width="stretch"
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )