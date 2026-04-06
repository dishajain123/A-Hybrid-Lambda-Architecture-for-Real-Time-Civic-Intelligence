import streamlit as st

_BADGE_CSS = """
<style>
.badge {
    display:inline-block; padding:.22rem .65rem; border-radius:20px;
    font-size:.72rem; font-weight:700; letter-spacing:.5px; text-transform:uppercase;
}
.badge-positive  { background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; }
.badge-negative  { background:#fee2e2; color:#b91c1c; border:1px solid #fecaca; }
.badge-neutral   { background:#f3f4f6; color:#374151; border:1px solid #e5e7eb; }
.badge-high      { background:#000;    color:#fff;    border:1px solid #000; }
.badge-medium    { background:#fef3c7; color:#92400e; border:1px solid #fde68a; }
.badge-low       { background:#d1fae5; color:#065f46; border:1px solid #a7f3d0; }
.badge-tag       { background:#f5f5f5; color:#444;    border:1px solid #e0e0e0; }
</style>
"""

def _inject():
    st.markdown(_BADGE_CSS, unsafe_allow_html=True)

def render_severity_badge(sentiment: float) -> str:
    _inject()
    if sentiment > 0.2:
        return '<span class="badge badge-positive">▲ Positive</span>'
    if sentiment < -0.2:
        return '<span class="badge badge-negative">▼ Negative</span>'
    return '<span class="badge badge-neutral">◆ Neutral</span>'

def sentiment_badge_html(sentiment: float) -> str:
    if sentiment > 0.2:
        return '<span class="badge badge-positive">▲ Positive</span>'
    if sentiment < -0.2:
        return '<span class="badge badge-negative">▼ Negative</span>'
    return '<span class="badge badge-neutral">◆ Neutral</span>'

def category_badge_html(category: str) -> str:
    return f'<span class="badge badge-tag">{category.title()}</span>'

def get_severity_color(sentiment: float) -> str:
    if sentiment > 0.2:  return "#16a34a"
    if sentiment < -0.2: return "#dc2626"
    return "#6b7280"

def get_severity_emoji(sentiment: float) -> str:
    if sentiment > 0.2:  return "▲"
    if sentiment < -0.2: return "▼"
    return "◆"

def inject_badge_css():
    _inject()