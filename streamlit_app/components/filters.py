import streamlit as st
from utils.constants import CATEGORIES

def render_filters(expanded: bool = False):
    """Render filter controls
    
    Returns:
        Dict with filter values
    """
    with st.expander("🔍 Filters", expanded=expanded):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.multiselect(
                "Category",
                CATEGORIES,
                default=[],
                help="Filter by news category"
            )
        
        with col2:
            source = st.text_input(
                "Source",
                placeholder="e.g., Times of India",
                help="Filter by news source"
            )
        
        with col3:
            limit = st.number_input(
                "Results limit",
                min_value=10,
                max_value=200,
                value=50,
                step=10
            )
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            sentiment_min = st.slider(
                "Min Sentiment",
                min_value=-1.0,
                max_value=1.0,
                value=-1.0,
                step=0.1
            )
        
        with col5:
            sentiment_max = st.slider(
                "Max Sentiment",
                min_value=-1.0,
                max_value=1.0,
                value=1.0,
                step=0.1
            )
        
        with col6:
            sort_by = st.selectbox(
                "Sort by",
                ["Recent", "Relevance", "Sentiment+", "Sentiment-"]
            )
    
    return {
        "category": category if category else None,
        "source": source if source else None,
        "limit": limit,
        "sentiment_min": sentiment_min,
        "sentiment_max": sentiment_max,
        "sort_by": sort_by
    }

def apply_filters(articles: list, filters: dict) -> list:
    """Apply filters to articles list
    
    Args:
        articles: List of article dicts
        filters: Filter dict from render_filters
    
    Returns:
        Filtered list
    """
    result = articles.copy()
    
    # Category filter
    if filters.get('category'):
        result = [a for a in result if a.get('category') in filters['category']]
    
    # Source filter
    if filters.get('source'):
        result = [a for a in result if filters['source'].lower() in a.get('source', '').lower()]
    
    # Sentiment filter
    min_sent = filters.get('sentiment_min', -1.0)
    max_sent = filters.get('sentiment_max', 1.0)
    result = [a for a in result if min_sent <= a.get('sentiment', 0) <= max_sent]
    
    # Sort
    sort_by = filters.get('sort_by', 'Recent')
    if sort_by == 'Recent':
        result.sort(key=lambda x: x.get('publish_date', ''), reverse=True)
    elif sort_by == 'Sentiment+':
        result.sort(key=lambda x: x.get('sentiment', 0), reverse=True)
    elif sort_by == 'Sentiment-':
        result.sort(key=lambda x: x.get('sentiment', 0))
    
    # Limit
    limit = filters.get('limit', 50)
    return result[:limit]