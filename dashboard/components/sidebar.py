import streamlit as st
from streamlit_option_menu import option_menu


def render_sidebar():

    with st.sidebar:

        st.markdown("""
        <div style="
            padding-top:10px;
            padding-bottom:25px;
        ">

        <h1 style="
            color:white;
            font-size:28px;
            font-weight:700;
            margin-bottom:0;
        ">
        🤖 Enterprise AI
        </h1>

        <p style="
            color:#94A3B8;
            font-size:14px;
            margin-top:6px;
        ">
        Multi-Agent Intelligence Platform
        </p>

        </div>
        """, unsafe_allow_html=True)

        selected = option_menu(

            menu_title=None,

            options=[
                "Overview",
                "Query Console",
                "Analytics",
                "Live Logs",
                "History"
            ],

            icons=[
                "grid-fill",
                "chat-dots-fill",
                "bar-chart-fill",
                "terminal-fill",
                "clock-history"
            ],

            default_index=0,

            styles={

                "container": {
                    "padding": "0!important",
                    "background-color": "#111827"
                },

                "icon": {
                    "color": "#A78BFA",
                    "font-size": "18px"
                },

                "nav-link": {

                    "font-size": "15px",

                    "text-align": "left",

                    "margin": "4px 0px",

                    "padding": "12px",

                    "border-radius": "12px",

                    "color": "white",

                    "--hover-color": "#1F2937",
                },

                "nav-link-selected": {

                    "background":
                    "linear-gradient(90deg,#2563EB,#7C3AED)",

                    "font-weight": "600",
                },
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # =====================================
        # SYSTEM STATUS PANEL
        # =====================================

        st.markdown("""
        <div class="glass-card">

        <h4 style="
            margin-top:0;
            color:white;
        ">
        📡 System Status
        </h4>

        <div style="
            color:#22C55E;
            font-size:14px;
            margin-top:10px;
        ">
        ● All Systems Operational
        </div>

        <div style="
            color:#94A3B8;
            font-size:13px;
            margin-top:10px;
        ">
        Agents Active: 5
        </div>

        <div style="
            color:#94A3B8;
            font-size:13px;
            margin-top:6px;
        ">
        Retrieval Mode: Hybrid
        </div>

        </div>
        """, unsafe_allow_html=True)

        return selected