import streamlit as st

_CSS = """
<style>
.page-header {
    background: #000;
    border-radius: 14px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    box-shadow: 0 4px 20px rgba(0,0,0,.15);
}
.page-header-icon { font-size: 2.2rem; }
.page-header-text h1 {
    margin: 0; font-size: 1.75rem; font-weight: 800;
    color: #fff; letter-spacing: -.5px;
}
.page-header-text p {
    margin: .2rem 0 0; font-size: .875rem; color: #999;
}
.live-badge {
    background: #ef4444;
    color: #fff; font-size: .65rem; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    padding: .2rem .55rem; border-radius: 20px;
    display: inline-block; margin-left: .5rem;
    animation: pulse-badge 2s infinite;
}
@keyframes pulse-badge {
    0%,100% { opacity:1; }
    50%      { opacity:.6; }
}
.section-title {
    font-size: 1rem; font-weight: 700; color: #111;
    text-transform: uppercase; letter-spacing: .6px;
    border-left: 3px solid #000; padding-left: .65rem;
    margin: 1.5rem 0 1rem;
}
.metric-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.metric-pill {
    background: #fff; border: 1.5px solid #e5e5e5;
    border-radius: 10px; padding: .75rem 1.1rem;
    flex: 1 1 140px; min-width: 120px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.metric-pill-val { font-size: 1.6rem; font-weight: 800; color: #000; line-height: 1; }
.metric-pill-lbl { font-size: .72rem; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: .6px; margin-top: .2rem; }
hr.section-hr { border: none; border-top: 1.5px solid #e8e8e8; margin: 1.5rem 0; }
</style>
"""

def inject_header_css():
    st.markdown(_CSS, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = "", icon: str = "🌐", live: bool = False):
    inject_header_css()
    live_html = '<span class="live-badge">LIVE</span>' if live else ""
    st.markdown(f"""
    <div class="page-header">
      <div class="page-header-icon">{icon}</div>
      <div class="page-header-text">
        <h1>{title}{live_html}</h1>
        {'<p>' + subtitle + '</p>' if subtitle else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_section_title(text: str):
    st.markdown(f'<p class="section-title">{text}</p>', unsafe_allow_html=True)

def render_divider():
    st.markdown('<hr class="section-hr">', unsafe_allow_html=True)

def render_metric_row(metrics: list):
    """metrics = [{"value": "123", "label": "Total Articles"}, ...]"""
    html = '<div class="metric-row">'
    for m in metrics:
        html += f"""
        <div class="metric-pill">
          <div class="metric-pill-val">{m['value']}</div>
          <div class="metric-pill-lbl">{m['label']}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)