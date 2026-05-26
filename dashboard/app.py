import streamlit as st

from styles import load_css

from components.sidebar import render_sidebar
from components.overview import render_overview
from components.query_console import render_query_console
from components.analytics import render_analytics
from components.logs import render_logs
from components.history import render_history

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(

    page_title="Enterprise AI Platform",

    page_icon="🚀",

    layout="wide",

    initial_sidebar_state="expanded"
)

# ==========================================
# LOAD GLOBAL CSS
# ==========================================

st.markdown(

    load_css(),

    unsafe_allow_html=True
)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

selected = render_sidebar()

# ==========================================
# MAIN HEADER
# ==========================================

st.markdown("""
<div style="
padding-bottom:20px;
">

<h1 class="main-title">
🚀 Enterprise Knowledge Base
</h1>

<p class="sub-title">
Multi-Agent AI Platform with Hybrid Retrieval,
Text2SQL, Memory, Analytics & Agent Orchestration
</p>

</div>
""", unsafe_allow_html=True)

# ==========================================
# PAGE ROUTING
# ==========================================

if selected == "Overview":

    render_overview()

# ==========================================

elif selected == "Query Console":

    render_query_console()

# ==========================================

elif selected == "Analytics":

    render_analytics()

# ==========================================

elif selected == "Live Logs":

    render_logs()

# ==========================================

elif selected == "History":

    render_history()