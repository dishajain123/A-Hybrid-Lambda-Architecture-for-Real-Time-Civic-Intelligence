import streamlit as st
from components.severity_badge import render_severity_badge
from datetime import datetime

def render_event_card(article: dict, featured: bool = False):
    """Render a single event/article card
    
    Args:
        article: Article dict with keys: title, summary, source, image, url, sentiment, publish_date, category, author
        featured: Whether to highlight as featured
    """
    col1, col2 = st.columns([0.3, 0.7])
    
    # Image
    with col1:
        if article.get('image'):
            st.image(article['image'], use_column_width=True)
        else:
            st.markdown("""
            <div style='
                background: #f0f0f0;
                height: 200px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
            '>
                <span style='color: #999; font-size: 3rem;'>📰</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Content
    with col2:
        # Featured badge
        if featured:
            st.markdown("""
            <span style='
                background: #fef3c7;
                color: #92400e;
                padding: 0.3rem 0.6rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
            '>
                ⭐ Featured
            </span>
            """, unsafe_allow_html=True)
        
        # Title
        st.markdown(f"### {article.get('title', 'Untitled')}")
        
        # Summary
        summary = article.get('summary', '')
        if len(summary) > 200:
            summary = summary[:200] + "..."
        st.markdown(f"*{summary}*")
        
        # Metadata row
        col_source, col_cat, col_badge = st.columns([0.4, 0.3, 0.3])
        
        with col_source:
            source = article.get('source', 'Unknown')
            st.markdown(f"**{source}** · {article.get('author', 'Unknown author')}")
        
        with col_cat:
            category = article.get('category', 'general').capitalize()
            st.markdown(f"📂 {category}")
        
        with col_badge:
            sentiment = article.get('sentiment', 0)
            render_severity_badge(sentiment, size="sm")
        
        # Timestamp
        pub_date = article.get('publish_date', '')
        if pub_date:
            st.markdown(f"<small style='color: #999;'>📅 {pub_date}</small>", unsafe_allow_html=True)
        
        # Link button
        if article.get('url'):
            st.markdown(f"[Read Full Article →]({article['url']})", help="Open in news source")

def render_event_card_compact(article: dict):
    """Render compact event card for lists"""
    col1, col2 = st.columns([0.15, 0.85])
    
    with col1:
        render_severity_badge(article.get('sentiment', 0), size="sm")
    
    with col2:
        st.markdown(f"**{article.get('title', 'Untitled')[:80]}...**")
        st.markdown(f"<small>{article.get('source', 'Unknown')} · {article.get('category', 'general')}</small>", 
                   unsafe_allow_html=True)
    
    if article.get('url'):
        st.markdown(f"[Read]({article['url']})")