def load_css():

    return """
    <style>

    /* ========================================
       GLOBAL APP
    ======================================== */

    .stApp {
        background-color: #0B1120;
        color: white;
        overflow-x: hidden;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* ========================================
       SIDEBAR
    ======================================== */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* ========================================
       TYPOGRAPHY
    ======================================== */

    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-bottom: 0;
        letter-spacing: -1px;
    }

    .sub-title {
        font-size: 17px;
        color: #94A3B8;
        margin-top: 8px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 18px;
        color: white;
    }

    /* ========================================
       METRIC CARDS
    ======================================== */

    [data-testid="metric-container"] {

        background: linear-gradient(
            145deg,
            rgba(17,24,39,0.95),
            rgba(30,41,59,0.92)
        );

        border: 1px solid rgba(255,255,255,0.06);

        padding: 18px;

        border-radius: 18px;

        box-shadow:
            0 4px 20px rgba(0,0,0,0.25);

        transition: 0.3s ease;
    }

    [data-testid="metric-container"]:hover {

        transform: translateY(-2px);

        border: 1px solid rgba(99,102,241,0.4);
    }

    [data-testid="metric-container"] label {

        color: #94A3B8 !important;
    }

    [data-testid="metric-container"] div {

        color: white !important;
    }

    /* ========================================
       GLASS CARDS
    ======================================== */

    .glass-card {

        background: rgba(17,24,39,0.82);

        border: 1px solid rgba(255,255,255,0.06);

        border-radius: 20px;

        padding: 22px;

        backdrop-filter: blur(14px);

        box-shadow:
            0 8px 32px rgba(0,0,0,0.25);

        margin-bottom: 20px;
    }

    /* ========================================
       QUERY INPUT
    ======================================== */

    .stTextInput > div > div > input {

        background-color: #111827;

        color: white;

        border-radius: 14px;

        border: 1px solid rgba(255,255,255,0.06);

        padding: 14px;

        font-size: 15px;
    }

    /* ========================================
       BUTTONS
    ======================================== */

    .stButton > button {

        width: 100%;

        border-radius: 14px;

        background: linear-gradient(
            90deg,
            #2563EB,
            #7C3AED
        );

        color: white;

        border: none;

        padding: 12px;

        font-weight: 600;

        transition: 0.25s ease;
    }

    .stButton > button:hover {

        transform: scale(1.02);

        background: linear-gradient(
            90deg,
            #1D4ED8,
            #6D28D9
        );
    }

    /* ========================================
       LOG PANELS
    ======================================== */

    .log-card {

        background: #111827;

        border-radius: 14px;

        padding: 14px;

        margin-bottom: 12px;

        border: 1px solid rgba(255,255,255,0.05);

        font-family: monospace;
    }

    /* ========================================
       SCROLLBAR
    ======================================== */

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #111827;
    }

    ::-webkit-scrollbar-thumb {
        background: #374151;
        border-radius: 10px;
    }

    /* ========================================
       DATAFRAMES
    ======================================== */

    .stDataFrame {

        border-radius: 16px;

        overflow: hidden;
    }

    /* ========================================
       PLOTLY
    ======================================== */

    .js-plotly-plot {

        border-radius: 18px;

        overflow: hidden;
    }

    </style>
    """