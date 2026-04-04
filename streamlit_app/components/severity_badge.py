import streamlit as st
from utils.constants import Severity, get_severity_from_sentiment

def render_severity_badge(sentiment: float, size: str = "md"):
    """Render severity badge based on sentiment
    
    Args:
        sentiment: Sentiment score (-1 to 1)
        size: Badge size (sm, md, lg)
    """
    severity = get_severity_from_sentiment(sentiment)
    emoji, label, color = severity.value
    
    size_map = {
        "sm": {"font": "0.75rem", "padding": "0.25rem 0.5rem"},
        "md": {"font": "0.85rem", "padding": "0.35rem 0.75rem"},
        "lg": {"font": "1rem", "padding": "0.5rem 1rem"}
    }
    
    styles = size_map.get(size, size_map["md"])
    
    st.markdown(f"""
    <span style='
        display: inline-block;
        background-color: {color};
        color: white;
        padding: {styles["padding"]};
        border-radius: 20px;
        font-size: {styles["font"]};
        font-weight: 600;
        margin-right: 0.5rem;
    '>
        {emoji} {label}
    </span>
    """, unsafe_allow_html=True)

def get_severity_emoji(sentiment: float) -> str:
    """Get severity emoji"""
    severity = get_severity_from_sentiment(sentiment)
    return severity.value[0]

def get_severity_label(sentiment: float) -> str:
    """Get severity label"""
    severity = get_severity_from_sentiment(sentiment)
    return severity.value[1]

def get_severity_color(sentiment: float) -> str:
    """Get severity color"""
    severity = get_severity_from_sentiment(sentiment)
    return severity.value[2]