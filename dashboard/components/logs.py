import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"


def render_logs():

    # ======================================
    # HEADER
    # ======================================

    st.markdown(
        '<div class="section-title">🤖 Agent Orchestration Timeline</div>',
        unsafe_allow_html=True
    )

    # ======================================
    # DESCRIPTION
    # ======================================

    st.markdown("""
    <div class="glass-card">

    Monitor real-time multi-agent orchestration,
    retrieval workflows, validation pipelines,
    and synthesis execution.

    </div>
    """, unsafe_allow_html=True)

    # ======================================
    # REFRESH BUTTON
    # ======================================

    refresh_col1, refresh_col2 = st.columns([1, 5])

    with refresh_col1:

        refresh = st.button(
            "🔄 Refresh"
        )

    # ======================================
    # FETCH LOGS
    # ======================================

    try:

        response = requests.get(
            f"{API_URL}/agent-conversations"
        )

        data = response.json()

        logs = data.get(
            "conversations",
            []
        )

    except Exception as e:

        st.error(str(e))

        logs = []

    # ======================================
    # EMPTY STATE
    # ======================================

    if not logs:

        st.info(
            "No orchestration logs available."
        )

        return

    # ======================================
    # AGENT COLORS
    # ======================================

    agent_colors = {

        "Query Router": "#2563EB",

        "Retriever Agent": "#7C3AED",

        "Text2SQL Agent": "#059669",

        "Analyst Agent": "#D97706",

        "Fact Checker": "#DC2626",

        "Synthesizer Agent": "#0EA5E9"
    }

    # ======================================
    # TIMELINE VIEW
    # ======================================

    for log in reversed(logs):

        color = agent_colors.get(
            log["agent"],
            "#FFFFFF"
        )

        st.markdown(f"""
        <div style="
            display:flex;
            gap:18px;
            margin-bottom:18px;
            align-items:flex-start;
        ">

            <!-- Timeline Dot -->

            <div style="
                width:14px;
                height:14px;
                background:{color};
                border-radius:50%;
                margin-top:14px;
                flex-shrink:0;
                box-shadow:0 0 12px {color};
            ">
            </div>

            <!-- Timeline Card -->

            <div class="glass-card"
                 style="
                    width:100%;
                    margin-bottom:0;
                 ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:10px;
                ">

                    <h4 style="
                        margin:0;
                        color:{color};
                        font-size:17px;
                    ">
                    {log['agent']}
                    </h4>

                    <span style="
                        color:#94A3B8;
                        font-size:12px;
                    ">
                    {log['timestamp']}
                    </span>

                </div>

                <div style="
                    color:#E2E8F0;
                    line-height:1.7;
                    font-size:15px;
                ">
                {log['message']}
                </div>

            </div>

        </div>
        """, unsafe_allow_html=True)

    # ======================================
    # SYSTEM SUMMARY
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
    📡 Orchestration Summary
    </h3>
    """, unsafe_allow_html=True)

    st.markdown(f"""

    <div style="
        color:#CBD5E1;
        line-height:2;
        font-size:15px;
    ">

    • Total Agent Events:
    <b>{len(logs)}</b>

    <br>

    • Active Agents:
    <b>5</b>

    <br>

    • Retrieval Mode:
    <b>Hybrid Retrieval</b>

    <br>

    • Monitoring Status:
    <span style="color:#22C55E;">
    Active
    </span>

    </div>

    """, unsafe_allow_html=True)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )