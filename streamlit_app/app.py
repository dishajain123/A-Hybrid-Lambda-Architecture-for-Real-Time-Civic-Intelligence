import streamlit as st
import sys
from pathlib import Path
import importlib.util

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

# Page configuration
st.set_page_config(
    page_title="City Pulse - News Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's default multipage UI
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# BLACK AND WHITE PREMIUM CSS THEME
st.markdown("""
    <style>
    /* Root Variables - Black & White Theme */
    :root {
        --color-primary: #000000;
        --color-secondary: #333333;
        --color-accent: #666666;
        --color-light-gray: #999999;
        --color-bg: #FFFFFF;
        --color-bg-secondary: #F5F5F5;
        --color-bg-tertiary: #E8E8E8;
        --color-border: #D0D0D0;
        --color-text: #000000;
        --color-text-muted: #666666;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.16);
        --shadow-lg: 0 10px 24px rgba(0, 0, 0, 0.20);
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main Container */
    .stApp {
        background-color: var(--color-bg);
    }
    
    .stMainBlockContainer {
        background: var(--color-bg);
        padding: 2rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
        border-right: 2px solid var(--color-secondary);
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] [role="radiogroup"] label {
        color: #F3F4F6 !important;
    }
    
    /* Sidebar Header */
    .sidebar-header {
        padding: 2rem 1rem 1.5rem 1rem;
        margin-bottom: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-header:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-header h1 {
        margin: 0 0 0.5rem 0;
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }
    
    .sidebar-header p {
        margin: 0;
        font-size: 0.85rem;
        color: #AAAAAA !important;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Section Divider */
    .sidebar-divider {
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        margin: 1.5rem 0;
    }
    
    /* Section Title */
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #E5E7EB !important;
    }
    
    /* Radio Buttons */
    .stRadio > label {
        background: transparent !important;
    }
    
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        color: #F9FAFB !important;
        -webkit-text-fill-color: #F9FAFB !important;
    }

    .stRadio > div > label * {
        color: #F9FAFB !important;
        -webkit-text-fill-color: #F9FAFB !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }
    
    .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    .stRadio > div > label[data-checked="true"] {
        background: rgba(255, 255, 255, 0.12) !important;
        color: #F9FAFB !important;
        border-color: rgba(255, 255, 255, 0.32) !important;
        font-weight: 600 !important;
    }
    
    .stRadio > div > label[data-checked="true"] * {
        color: #F9FAFB !important;
        -webkit-text-fill-color: #F9FAFB !important;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: #FFFFFF !important;
        font-size: 0.9rem !important;
    }
    
    /* Selectbox */
    .stSelectbox > label {
        color: #FFFFFF !important;
        font-size: 0.9rem !important;
    }
    
    /* Footer */
    .sidebar-footer {
        padding: 1.5rem 1rem;
        margin-top: 2rem;
        text-align: center;
        font-size: 0.85rem;
        color: #888888 !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        line-height: 1.6;
    }
    
    .sidebar-footer strong {
        color: #FFFFFF !important;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    /* Brand header card (stable, always readable) */
    .brand-card {
        background: #F3F4F6;
        border: 1px solid #D1D5DB;
        border-radius: 14px;
        padding: 0.65rem 0.65rem;
        text-align: center;
        margin-bottom: 0.15rem;
    }

    .brand-title {
        margin: 0;
        font-size: 1.55rem;
        line-height: 1.25;
        font-weight: 800;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }

    .brand-subtitle {
        margin: 0.2rem 0 0 0;
        font-size: 0.72rem;
        font-weight: 700;
        color: #374151 !important;
        -webkit-text-fill-color: #374151 !important;
        opacity: 1 !important;
    }
    
    /* Main Content Styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--color-text);
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    p {
        color: var(--color-text);
        line-height: 1.7;
    }
    
    /* Cards */
    .stMetric {
        background: var(--color-bg-secondary);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--color-border);
        box-shadow: var(--shadow-sm);
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--color-primary);
        color: #FFFFFF;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--color-secondary);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    /* Secondary buttons (used for Refresh) */
    .stButton > button[kind="secondary"] {
        background: #F3F4F6 !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #E5E7EB !important;
        color: #111827 !important;
        border-color: #9CA3AF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.12) !important;
    }

    .stButton > button[kind="secondary"]:active {
        transform: translateY(0) scale(0.98) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.10) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--color-bg-secondary);
        border: 1px solid var(--color-border);
        border-radius: 8px;
        font-weight: 600;
        color: var(--color-text);
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--color-bg-tertiary);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: var(--color-bg-secondary);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--color-text-muted);
        background-color: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #E5E7EB;
        color: #111827;
        border: 1px solid #D1D5DB;
        box-shadow: inset 0 -3px 0 #FF4D4D;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--color-primary) !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid var(--color-border);
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--color-bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--color-accent);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-secondary);
    }
    
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False
if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 30

# Sidebar navigation
with st.sidebar:
    # Brand header
    st.markdown("""
    <div class="brand-card">
        <p class="brand-title">🌍 CITY PULSE</p>
        <p class="brand-subtitle">Real-time News Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Navigation section
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
        <div style="width: 3px; height: 1rem; background: #FFFFFF; border-radius: 2px;"></div>
        <p class="sidebar-section-title" style="margin: 0;">NAVIGATE</p>
    </div>
    """, unsafe_allow_html=True)
    
    page_labels = {
        "1_City_Pulse": "City Pulse",
        "2_Live_Feed": "Live Feed",
        "3_Live_Map": "Geo Intelligence",
        "4_Insights": "Insights",
        "5_Event_Detail": "Event Detail",
        "6_System_Insights": "System Insights",
    }

    page = st.radio(
        "Select page",
        [
            "1_City_Pulse",
            "2_Live_Feed",
            "3_Live_Map",
            "4_Insights",
            "5_Event_Detail",
            "6_System_Insights"
        ],
        format_func=lambda x: page_labels.get(x, x),
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Settings section
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
        <div style="width: 3px; height: 1rem; background: #888888; border-radius: 2px;"></div>
        <p class="sidebar-section-title" style="margin: 0;">SETTINGS</p>
    </div>
    """, unsafe_allow_html=True)
    
    live_pages = {"2_Live_Feed", "3_Live_Map"}
    if page in live_pages:
        st.session_state.auto_refresh = st.checkbox(
            "Auto-refresh",
            value=st.session_state.auto_refresh
        )

        st.session_state.refresh_interval = st.selectbox(
            "Refresh interval (seconds)",
            [10, 30, 60, 120],
            index=[10, 30, 60, 120].index(st.session_state.refresh_interval),
            help="Seconds between refreshes"
        )
    else:
        st.session_state.auto_refresh = False
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="sidebar-footer">
        <strong>CITY PULSE v2.0</strong>
        Real-time civic intelligence platform
        <br><br>
        <strong>Stack:</strong>
        FastAPI · MongoDB · MinIO<br>
        Kafka · Flink · Streamlit
    </div>
    """, unsafe_allow_html=True)

def load_page(module_filename: str):
    """Load a Streamlit page module from the pages directory."""
    module_path = BASE_DIR / "pages" / module_filename
    if not module_path.exists():
        st.error(f"Page file not found: {module_filename}")
        return None
    
    spec = importlib.util.spec_from_file_location(module_filename, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Route to appropriate page
try:
    if page == "1_City_Pulse":
        page_module = load_page("1_City_Pulse.py")
        if page_module:
            page_module.render()
    elif page == "2_Live_Feed":
        page_module = load_page("2_Live_Feed.py")
        if page_module:
            page_module.render()
    elif page == "3_Live_Map":
        page_module = load_page("3_Live_Map.py")
        if page_module:
            page_module.render()
    elif page == "4_Insights":
        page_module = load_page("4_Insights.py")
        if page_module:
            page_module.render()
    elif page == "5_Event_Detail":
        page_module = load_page("5_Event_Detail.py")
        if page_module:
            page_module.render()
    elif page == "6_System_Insights":
        page_module = load_page("6_System_Insights.py")
        if page_module:
            page_module.render()
except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    st.exception(e)
