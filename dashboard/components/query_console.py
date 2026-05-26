import streamlit as st
import requests
import pandas as pd


API_URL = "http://127.0.0.1:8000"


def render_query_console():

    # ======================================
    # HEADER
    # ======================================

    st.markdown(
        '<div class="section-title">🔍 AI Query Workspace</div>',
        unsafe_allow_html=True
    )

    # ======================================
    # QUERY INFO PANEL
    # ======================================

    st.markdown("""
    <div class="glass-card">

    <h3 style="
        margin-top:0;
        color:white;
    ">
    💡 Supported Query Types
    </h3>

    <ul style="
        color:#CBD5E1;
        line-height:2;
    ">
        <li>Structured SQL queries</li>
        <li>Document retrieval & RAG</li>
        <li>Hybrid enterprise search</li>
        <li>Analytics & summarization</li>
        <li>Fact-checked responses</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)

    # ======================================
    # QUERY INPUT
    # ======================================

    query = st.text_input(
        "Ask the Enterprise AI Platform"
    )

    # ======================================
    # QUICK PROMPTS
    # ======================================

    st.markdown("""
    <div style="
        margin-top:15px;
        margin-bottom:20px;
    ">
    """, unsafe_allow_html=True)

    prompt_col1, prompt_col2, prompt_col3 = st.columns(3)

    with prompt_col1:

        if st.button(
            "📊 Average Salary"
        ):

            query = (
                "What is the average salary?"
            )

    with prompt_col2:

        if st.button(
            "📄 Company Policies"
        ):

            query = (
                "What are the company policies?"
            )

    with prompt_col3:

        if st.button(
            "⚙️ Agent Analytics"
        ):

            query = (
                "Show system analytics"
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # ======================================
    # PROCESS QUERY
    # ======================================

    if st.button("🚀 Run Enterprise Query"):

        if query:

            with st.spinner(
                "Multi-agent orchestration in progress..."
            ):

                try:

                    response = requests.post(

                        f"{API_URL}/query",

                        json={
                            "query": query
                        }
                    )

                    result = response.json()

                    # ==========================
                    # FINAL RESPONSE
                    # ==========================

                    st.markdown("""
                    <div class="glass-card">
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <h3 style="
                        margin-top:0;
                        color:white;
                    ">
                    📄 AI Response
                    </h3>
                    """, unsafe_allow_html=True)

                    st.write(
                        result["final_answer"]
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                    # ==========================
                    # PROCESSING PIPELINE
                    # ==========================

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown("""
                    <div class="glass-card">
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <h3 style="
                        margin-top:0;
                        color:white;
                    ">
                    ⚙️ Multi-Agent Pipeline
                    </h3>
                    """, unsafe_allow_html=True)

                    steps = result[
                        "processing_steps"
                    ]

                    pipeline_data = pd.DataFrame({

                        "Stage": [
                            "Routing",
                            "Retrieval",
                            "Analysis",
                            "Fact Check",
                            "Synthesis"
                        ],

                        "Status": [
                            "Completed",
                            "Completed",
                            "Completed",
                            "Completed",
                            "Completed"
                        ]
                    })

                    st.dataframe(
                        pipeline_data,
                        width="stretch"
                    )

                    st.json(steps)

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                    # ==========================
                    # SYSTEM METADATA
                    # ==========================

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown("""
                    <div class="glass-card">
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <h3 style="
                        margin-top:0;
                        color:white;
                    ">
                    📡 Execution Metadata
                    </h3>
                    """, unsafe_allow_html=True)

                    metadata = result["metadata"]

                    meta_col1, meta_col2 = st.columns(2)

                    with meta_col1:

                        st.metric(
                            "Processing Time",
                            f"{metadata['processing_time_seconds']:.2f}s"
                        )

                    with meta_col2:

                        st.metric(
                            "Session ID",
                            metadata["session_id"][:8]
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                except Exception as e:

                    st.error(str(e))

        else:

            st.warning(
                "Please enter a query."
            )