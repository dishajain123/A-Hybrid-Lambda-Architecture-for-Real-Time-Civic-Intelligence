import streamlit as st
import sys
from pathlib import Path
import importlib.util

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="City Pulse — Civic Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; font-family: 'Inter', sans-serif; }

/* Hide default multipage nav */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── App shell ── */
.stApp { background: #fafafa; }
.stMainBlockContainer { padding: 1.5rem 2rem 3rem; }
section[data-testid="stSidebar"] { background: #000 !important; }
section[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Sidebar inner ── */
.sidebar-wrap { padding: 1.25rem 1rem 1rem; }

.brand-block {
    background: linear-gradient(135deg,rgba(255,255,255,.07),rgba(255,255,255,.02));
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 14px;
    padding: 1.4rem 1.2rem 1.25rem;
    margin-bottom: 1.5rem;
    text-align: center;
    transition: border-color .25s;
}
.brand-block:hover { border-color: rgba(255,255,255,.28); }
.brand-icon { font-size: 2.2rem; margin-bottom: .3rem; }
.brand-name {
    font-size: 1.35rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; margin: 0;
}
.brand-tag { font-size: .72rem; color: #888; letter-spacing: .8px; text-transform: uppercase; }

.section-label {
    font-size: .65rem; font-weight: 700; letter-spacing: 1.4px;
    text-transform: uppercase; color: #555; margin: 0 0 .5rem .25rem;
}
.divider { border-top: 1px solid rgba(255,255,255,.08); margin: 1rem 0; }

/* ── Nav radio ── */
.stRadio > label { display: none; }
.stRadio > div { gap: .3rem !important; }
.stRadio > div > label {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid transparent !important;
    border-radius: 9px !important;
    padding: .65rem 1rem !important;
    color: #fff !important;
    font-size: .875rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all .18s ease !important;
    width: 100%;
}
.stRadio > div > label:hover {
    background: rgba(255,255,255,.09) !important;
    color: #fff !important;
}
.stRadio > div > label[data-checked="true"] {
    background: rgba(255,255,255,.16) !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-color: transparent !important;
}
.stRadio > div > label,
.stRadio > div > label *,
.stRadio > div > label p,
.stRadio > div > label span,
.stRadio > div > label div,
.stRadio > div > label[data-checked="true"] p,
.stRadio > div > label[data-checked="true"] span,
.stRadio > div > label[data-checked="true"] div {
    color: #fff !important;
    fill: #fff !important;
}
.stRadio > div > label p { margin: 0; }

/* ── Sidebar widgets ── */
section[data-testid="stSidebar"] .stCheckbox label { color: #bbb !important; font-size: .85rem !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #bbb !important; font-size: .82rem !important; }
section[data-testid="stSidebar"] select { background: #1a1a1a !important; color: #ddd !important; border: 1px solid #333 !important; }

.sidebar-footer {
    font-size: .72rem; color: #555; text-align: center;
    line-height: 1.7; padding: 1rem .5rem 0;
    border-top: 1px solid rgba(255,255,255,.07);
    margin-top: 1.5rem;
}
.sidebar-footer strong { color: #888; display: block; }

/* ── Global main styles ── */
h1, h2, h3, h4 { color: #111; font-weight: 700; letter-spacing: -.4px; }
p { color: #333; line-height: 1.7; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #fff; border: 1.5px solid #e5e5e5;
    border-radius: 12px; padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    transition: box-shadow .2s;
}
[data-testid="stMetric"]:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); }
[data-testid="stMetricLabel"] { font-size: .78rem !important; font-weight: 600; color: #777; text-transform: uppercase; letter-spacing: .6px; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800; color: #000; }

/* Buttons */
.stButton > button {
    background: #000; color: #fff; border: none;
    border-radius: 8px; font-weight: 600; font-size: .875rem;
    padding: .6rem 1.25rem; transition: all .2s;
    box-shadow: 0 1px 3px rgba(0,0,0,.2);
}
.stButton > button:hover { background: #1a1a1a; box-shadow: 0 3px 8px rgba(0,0,0,.25); transform: translateY(-1px); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #f0f0f0; border-radius: 10px; padding: .35rem; gap: .3rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; padding: .55rem 1.1rem;
    font-weight: 600; font-size: .83rem; color: #666;
}
.stTabs [aria-selected="true"] { background: #000; color: #fff !important; }
.stTabs [aria-selected="true"] *,
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div {
    color: #fff !important;
    fill: #fff !important;
}

/* Expander */
.streamlit-expanderHeader { background: #f5f5f5; border-radius: 8px; font-weight: 600; color: #111; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f0f0f0; }
::-webkit-scrollbar-thumb { background: #bbb; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #888; }

/* Info / warning / error banners */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* Spinner */
.stSpinner > div { border-top-color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "selected_article_id": None,
    "auto_refresh":        False,
    "refresh_interval":    30,
    "current_page":        "🏙️  City Pulse",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
NAV = {
    "🏙️  City Pulse":     "1_City_Pulse.py",
    "📡  Live Feed":      "2_Live_Feed.py",
    "🗺️  Live Map":       "3_Live_Map.py",
    "📊  Insights":       "4_Insights.py",
    "🔍  Event Detail":   "5_Event_Detail.py",
    "⚙️  System Insights":"6_System_Insights.py",
}

with st.sidebar:
    st.markdown("""
    <div class="sidebar-wrap">
      <div class="brand-block">
        <div class="brand-icon">🌐</div>
        <p class="brand-name">CITY PULSE</p>
        <p class="brand-tag">Real-time Civic Intelligence</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div style="padding:0 1rem"><p class="section-label">Navigate</p></div>', unsafe_allow_html=True)
        page = st.radio("Page", list(NAV.keys()), label_visibility="collapsed")
        st.markdown('<div style="padding:0 1rem"><div class="divider"></div></div>', unsafe_allow_html=True)

    live_pages = {"📡  Live Feed", "🗺️  Live Map"}
    with st.container():
        st.markdown('<div style="padding:0 1rem"><p class="section-label">Settings</p></div>', unsafe_allow_html=True)
        if page in live_pages:
            st.session_state.auto_refresh = st.checkbox(
                "Auto-refresh", value=st.session_state.auto_refresh, key="ar_cb"
            )
            if st.session_state.auto_refresh:
                st.session_state.refresh_interval = st.selectbox(
                    "Interval (sec)", [10, 30, 60, 120],
                    index=[10,30,60,120].index(st.session_state.refresh_interval),
                    key="ar_sel",
                )
        else:
            st.session_state.auto_refresh = False
            st.caption("Auto-refresh available on Live pages.")

    st.markdown("""
    <div style="padding:0 1rem">
      <div class="sidebar-footer">
        <strong>CITY PULSE v2.1</strong>
        Lambda Architecture · Civic Intelligence<br>
        <strong style="margin-top:.4rem">Stack</strong>
        FastAPI · Kafka · Flink<br>MinIO · MongoDB · Streamlit
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Page routing ───────────────────────────────────────────────────────────────
def load_page(filename: str):
    path = BASE_DIR / "pages" / filename
    if not path.exists():
        st.error(f"Page not found: {filename}")
        return None
    spec = importlib.util.spec_from_file_location(filename, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

try:
    mod = load_page(NAV[page])
    if mod and hasattr(mod, "render"):
        mod.render()
except Exception as exc:
    st.error(f"Error loading page: {exc}")
    st.exception(exc)
