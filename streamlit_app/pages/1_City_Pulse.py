import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from components.header import render_header, render_metric_row, render_divider, render_section_title
from components.severity_badge import render_severity_badge
from components.filters import render_filters, apply_filters
from components.ai_panel import render_ai_panel
from services.api_client import get_client

def render():
    """Render City Pulse overview page with BLACK & WHITE theme"""
    
    # BLACK & WHITE PAGE CSS
    st.markdown("""
    <style>
        /* Black & White Cards */
        .metric-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #000000;
            box-shadow: 4px 4px 0px #000000;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0px #000000;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #000000;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Article Card */
        .article-card {
            background: #FFFFFF;
            border: 2px solid #000000;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 3px 3px 0px #000000;
            transition: all 0.2s ease;
        }
        
        .article-card:hover {
            transform: translate(-1px, -1px);
            box-shadow: 4px 4px 0px #000000;
        }
        
        .article-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #000000;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }
        
        .article-meta {
            font-size: 0.85rem;
            color: #666666;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        /* Section Header */
        .section-header {
            background: #000000;
            color: #FFFFFF;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: 0.5px;
        }
        
        /* Sentiment Badge */
        .sentiment-positive {
            background: #000000;
            color: #FFFFFF;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .sentiment-neutral {
            background: #666666;
            color: #FFFFFF;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .sentiment-negative {
            background: #CCCCCC;
            color: #000000;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; border-bottom: 3px solid #000000;">
        <h1 style="font-size: 3rem; font-weight: 900; color: #000000; margin: 0;">
            🌍 CITY PULSE
        </h1>
        <p style="font-size: 1.1rem; color: #666666; margin: 0.5rem 0 0 0;">
            Live civic intelligence overview · Real-time news analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get data from API
    client = get_client()
    
    # Load all data sources
    with st.spinner("⚡ Loading fresh data from backend..."):
        search_gold = client.get_analytics_data("search_news")
        top_gold = client.get_analytics_data("top_news")
        # Also get live feed data
        live_articles = client.get_endpoint_articles("search_news", limit=200)
    
    if not search_gold and not live_articles:
        st.error("❌ Unable to load data. Please check the API connection.")
        st.info("💡 Make sure the FastAPI backend is running at: " + client.base_url)
        return

    # Use live articles if gold not available
    if not search_gold:
        st.warning("⚠️ Using live data (Gold layer not available)")
        search_articles = live_articles
        analytics_metrics = {}
        avg_sentiment = 0
        total_articles = len(live_articles)
        category_breakdown = {}
        trending_keywords = []
        top_sources = []
    else:
        search_articles = search_gold.get('articles', [])
        top_articles = (top_gold or {}).get('articles', [])
        analytics_metrics = search_gold.get('metrics', {})
        if not isinstance(analytics_metrics, dict):
            analytics_metrics = {}
        avg_sentiment = analytics_metrics.get('avg_sentiment', 0)
        total_articles = analytics_metrics.get('total_articles', len(search_articles))
        category_breakdown = analytics_metrics.get('category_breakdown', {})
        trending_keywords = analytics_metrics.get('trending_keywords', [])
        top_sources = analytics_metrics.get('top_sources', [])
    
    # Show data freshness indicator
    st.markdown(f"""
    <div style="background: #F5F5F5; padding: 0.75rem 1rem; border-radius: 6px; border-left: 4px solid #000000; margin-bottom: 1.5rem;">
        <strong>📊 Data Status:</strong> Showing {total_articles} articles · 
        <strong>Live Feed:</strong> {len(live_articles)} articles available · 
        <strong>Last Updated:</strong> {datetime.now().strftime("%H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)
    
    # === KEY METRICS ===
    st.markdown('<div class="section-header">📊 KEY METRICS</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_articles}</div>
            <div class="metric-label">Total Articles</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sentiment_label = "POSITIVE" if avg_sentiment > 0.2 else "NEGATIVE" if avg_sentiment < -0.2 else "NEUTRAL"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_sentiment:.2f}</div>
            <div class="metric-label">Avg Sentiment · {sentiment_label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        num_categories = len(category_breakdown)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{num_categories}</div>
            <div class="metric-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        num_sources = len(top_sources) if isinstance(top_sources, list) else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{num_sources}</div>
            <div class="metric-label">News Sources</div>
        </div>
        """, unsafe_allow_html=True)
    
    # === CATEGORY BREAKDOWN CHART ===
    if category_breakdown:
        st.markdown('<div class="section-header">📈 CATEGORY DISTRIBUTION</div>', unsafe_allow_html=True)
        
        # Create bar chart (black and white)
        categories = list(category_breakdown.keys())
        counts = list(category_breakdown.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=counts,
                marker=dict(
                    color='#000000',
                    line=dict(color='#FFFFFF', width=2)
                ),
                text=counts,
                textposition='outside',
                textfont=dict(size=12, color='#000000', family='Inter, sans-serif', weight='bold')
            )
        ])
        
        fig.update_layout(
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF',
            font=dict(family='Inter, sans-serif', color='#000000'),
            xaxis=dict(
                title="Category",
                showgrid=True,
                gridcolor='#E8E8E8',
                linecolor='#000000',
                linewidth=2
            ),
            yaxis=dict(
                title="Article Count",
                showgrid=True,
                gridcolor='#E8E8E8',
                linecolor='#000000',
                linewidth=2
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # === TRENDING KEYWORDS ===
    if trending_keywords:
        st.markdown('<div class="section-header">🔥 TRENDING KEYWORDS</div>', unsafe_allow_html=True)
        
        # Display as styled tags
        keywords_html = ' '.join([
            f'<span style="background: #000000; color: #FFFFFF; padding: 0.5rem 1rem; border-radius: 20px; margin: 0.25rem; display: inline-block; font-weight: 600;">{kw}</span>'
            for kw in trending_keywords[:15]
        ])
        st.markdown(f'<div style="margin: 1rem 0;">{keywords_html}</div>', unsafe_allow_html=True)
    
    # === RECENT ARTICLES ===
    st.markdown('<div class="section-header">📰 RECENT ARTICLES</div>', unsafe_allow_html=True)
    
    # Use live articles if available, fallback to gold
    display_articles = live_articles if live_articles else search_articles
    
    if display_articles:
        for article in display_articles[:10]:
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown')
            publish_date = article.get('publish_date', 'Unknown')
            sentiment = article.get('sentiment', 0)
            category = article.get('category', 'general')
            
            # Sentiment badge
            if sentiment > 0.2:
                sentiment_class = "sentiment-positive"
                sentiment_emoji = "✓"
            elif sentiment < -0.2:
                sentiment_class = "sentiment-negative"
                sentiment_emoji = "✗"
            else:
                sentiment_class = "sentiment-neutral"
                sentiment_emoji = "◯"
            
            st.markdown(f"""
            <div class="article-card">
                <div class="article-title">{sentiment_emoji} {title}</div>
                <div class="article-meta">
                    <span><strong>📰 Source:</strong> {source}</span>
                    <span><strong>📅 Date:</strong> {publish_date}</span>
                    <span><strong>📂 Category:</strong> {category}</span>
                    <span class="{sentiment_class}">Sentiment: {sentiment:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No articles available. Data may still be loading from the pipeline.")
    
    # === TOP SOURCES ===
    if top_sources and isinstance(top_sources, list):
        st.markdown('<div class="section-header">🏆 TOP NEWS SOURCES</div>', unsafe_allow_html=True)
        
        source_cols = st.columns(min(len(top_sources), 4))
        for idx, source in enumerate(top_sources[:4]):
            if isinstance(source, dict):
                with source_cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{source.get('count', 0)}</div>
                        <div class="metric-label">{source.get('name', 'Unknown')}</div>
                    </div>
                    """, unsafe_allow_html=True)