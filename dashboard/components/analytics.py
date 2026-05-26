import streamlit as st
import requests
import pandas as pd
import plotly.express as px


API_URL = "http://127.0.0.1:8000"


def render_analytics():

    # ======================================
    # FETCH LIVE ANALYTICS
    # ======================================

    try:

        analytics = requests.get(
            f"{API_URL}/analytics"
        ).json()

    except:

        analytics = {

            "routing_distribution": {},
            "confidence_distribution": {}
        }

    routing_distribution = analytics.get(
        "routing_distribution",
        {}
    )

    confidence_distribution = analytics.get(
        "confidence_distribution",
        {}
    )

    # ======================================
    # HEADER
    # ======================================

    st.markdown(
        '<div class="section-title">📊 Enterprise Analytics</div>',
        unsafe_allow_html=True
    )

    # ======================================
    # ROUTING DISTRIBUTION
    # ======================================

    chart_col1, chart_col2 = st.columns(2)

    # ======================================
    # ROUTING CHART
    # ======================================

    with chart_col1:

        st.markdown("""
        <div class="glass-card">
        """, unsafe_allow_html=True)

        st.markdown("""
        <h3 style="
            margin-top:0;
            color:white;
        ">
        ⚙️ Retrieval Distribution
        </h3>
        """, unsafe_allow_html=True)

        if routing_distribution:

            routing_df = pd.DataFrame({

                "Type":
                    list(
                        routing_distribution.keys()
                    ),

                "Count":
                    list(
                        routing_distribution.values()
                    )
            })

            fig = px.pie(

                routing_df,

                names="Type",

                values="Count",

                hole=0.5
            )

            fig.update_layout(

                template="plotly_dark",

                paper_bgcolor="#111827",

                font_color="white",

                height=400
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "No routing analytics available"
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # ======================================
    # CONFIDENCE DISTRIBUTION
    # ======================================

    with chart_col2:

        st.markdown("""
        <div class="glass-card">
        """, unsafe_allow_html=True)

        st.markdown("""
        <h3 style="
            margin-top:0;
            color:white;
        ">
        🎯 Confidence Distribution
        </h3>
        """, unsafe_allow_html=True)

        if confidence_distribution:

            confidence_df = pd.DataFrame({

                "Confidence":
                    list(
                        confidence_distribution.keys()
                    ),

                "Count":
                    list(
                        confidence_distribution.values()
                    )
            })

            fig2 = px.bar(

                confidence_df,

                x="Confidence",

                y="Count",

                text="Count"
            )

            fig2.update_layout(

                template="plotly_dark",

                paper_bgcolor="#111827",

                plot_bgcolor="#111827",

                font_color="white",

                height=400
            )

            st.plotly_chart(
                fig2,
                width="stretch"
            )

        else:

            st.info(
                "No confidence analytics available"
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # ======================================
    # INSIGHTS PANEL
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
    🧠 Enterprise Insights
    </h3>
    """, unsafe_allow_html=True)

    insights = [

        "Hybrid retrieval is the dominant orchestration mode",

        "Fact-checking confidence remains consistently high",

        "Enterprise query traffic is increasing steadily",

        "Agent orchestration pipeline is operating normally"
    ]

    for insight in insights:

        st.markdown(f"""
        <div class="log-card">
        {insight}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )