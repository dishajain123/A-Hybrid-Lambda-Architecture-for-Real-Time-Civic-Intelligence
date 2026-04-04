"""
AI panel component for insights and summaries
"""
import streamlit as st
from typing import List, Dict


def render_ai_panel(title: str, content: str, icon: str = "??", expanded: bool = True):
    """
    Render AI insights panel
    
    Args:
        title: Panel title
        content: AI-generated content
        icon: Icon to display
        expanded: Ignored (kept for backward compatibility)
    """
    st.markdown(
        f'''
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            color: white;
            margin: 1rem 0;
        ">
            <h3 style="margin: 0 0 1rem 0;">{icon} {title}</h3>
            <p style="margin: 0; line-height: 1.6;">{content}</p>
        </div>
        ''',
        unsafe_allow_html=True
    )


def render_top_events_summary(events: List[Dict], max_events: int = 3):
    """
    Render top events summary with AI-style presentation
    
    Args:
        events: List of event dictionaries
        max_events: Maximum number of events to display
    """
    if not events:
        st.info("No high-impact events at this time")
        return
    
    st.markdown("### 🎯 Top High-Impact Events")
    
    for idx, event in enumerate(events[:max_events], 1):
        with st.container():
            st.markdown(
                f'''
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 4px solid #3b82f6;
                    margin: 0.5rem 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                ">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1f2937;">
                        {idx}. {event.get('title', 'Untitled')}
                    </h4>
                    <p style="margin: 0 0 0.5rem 0; color: #4b5563; font-size: 0.875rem;">
                        {event.get('summary', '')[:200]}...
                    </p>
                    <div style="color: #9ca3af; font-size: 0.75rem;">
                        <span>📍 {event.get('source_country', 'Unknown').upper()}</span>
                        <span style="margin-left: 1rem;">📰 {event.get('source', 'Unknown')}</span>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )


def render_insight_card(title: str, value: str, icon: str, trend: str = None):
    """
    Render single insight card
    
    Args:
        title: Insight title
        value: Insight value
        icon: Icon to display
        expanded: Ignored (kept for backward compatibility)
        trend: Optional trend indicator (up/down/neutral)
    """
    trend_html = ""
    if trend:
        trend_icons = {"up": "📈", "down": "📉", "neutral": "➡️"}
        trend_colors = {"up": "#10b981", "down": "#ef4444", "neutral": "#6b7280"}
        
        trend_html = f'''
            <span style="color: {trend_colors.get(trend, '#6b7280')}; margin-left: 0.5rem;">
                {trend_icons.get(trend, '')}
            </span>
        '''
    
    st.markdown(
        f'''
        <div style="
            background: white;
            padding: 1.25rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937; margin-bottom: 0.25rem;">
                {value}{trend_html}
            </div>
            <div style="color: #6b7280; font-size: 0.875rem;">{title}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )