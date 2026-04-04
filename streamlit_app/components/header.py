import streamlit as st

def render_header(title: str, subtitle: str = "", emoji: str = ""):
    """Render page header with premium styling"""
    col1, col2 = st.columns([0.8, 0.2])
    
    with col1:
        if emoji:
            st.markdown(f"# {emoji} {title}")
        else:
            st.markdown(f"# {title}")
        
        if subtitle:
            st.markdown(f"*{subtitle}*")
    
    with col2:
        st.markdown("")  # Spacing
    
    st.markdown("---")

def render_metric_row(metrics: list, cols: int = 4):
    """Render a row of metric cards
    
    Args:
        metrics: List of dicts with keys: label, value, unit, icon
        cols: Number of columns
    """
    columns = st.columns(cols)
    
    for idx, metric in enumerate(metrics):
        with columns[idx % cols]:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 0.9rem; color: #6c757d; margin-bottom: 0.5rem;'>
                    {metric.get('icon', '')} {metric['label']}
                </div>
                <div style='font-size: 2rem; font-weight: 700; color: #1f77b4;'>
                    {metric['value']}
                </div>
                <div style='font-size: 0.85rem; color: #6c757d;'>
                    {metric.get('unit', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_divider():
    """Render styled divider"""
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

def render_section_title(title: str):
    """Render section title"""
    st.markdown(f"## {title}")