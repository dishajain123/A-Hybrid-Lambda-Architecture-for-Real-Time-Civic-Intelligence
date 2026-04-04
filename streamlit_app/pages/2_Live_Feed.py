import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def render():
    """Render Live Feed page with BLACK & WHITE theme and LIVE data"""
    
    # Import here to avoid circular dependency
    from services.api_client import get_client
    
    # BLACK & WHITE CSS
    st.markdown("""
    <style>
        .feed-header {
            background: #000000;
            color: #FFFFFF;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 4px 4px 0px #666666;
        }
        
        .event-card-high {
            background: #FFFFFF;
            border: 3px solid #000000;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 4px 4px 0px #000000;
            transition: all 0.2s ease;
        }
        
        .event-card-high:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0px #000000;
        }
        
        .event-card-medium {
            background: #FFFFFF;
            border: 2px solid #666666;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 3px 3px 0px #666666;
            transition: all 0.2s ease;
        }
        
        .event-card-medium:hover {
            transform: translate(-1px, -1px);
            box-shadow: 4px 4px 0px #666666;
        }
        
        .event-card-low {
            background: #F5F5F5;
            border: 2px solid #CCCCCC;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 2px 2px 0px #CCCCCC;
            transition: all 0.2s ease;
        }
        
        .event-card-low:hover {
            transform: translate(-1px, -1px);
            box-shadow: 3px 3px 0px #CCCCCC;
        }
        
        .severity-badge-high {
            background: #000000;
            color: #FFFFFF;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.85rem;
            display: inline-block;
        }
        
        .severity-badge-medium {
            background: #666666;
            color: #FFFFFF;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.85rem;
            display: inline-block;
        }
        
        .severity-badge-low {
            background: #CCCCCC;
            color: #000000;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.85rem;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="feed-header">
        <h1 style="font-size: 2.5rem; font-weight: 900; margin: 0;">
            📡 LIVE CIVIC FEED
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem;">
            Real-time local signal tracking · Updated continuously
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data from API
    client = get_client()
    
    # Auto-refresh for live page
    if st.session_state.get("auto_refresh"):
        interval_s = int(st.session_state.get("refresh_interval", 30))
        st.markdown(f"""
        <div style="background: #F5F5F5; padding: 0.5rem 1rem; border-radius: 6px; border-left: 4px solid #000000; margin-bottom: 1rem;">
            🔄 Auto-refresh enabled · Refreshing every {interval_s} seconds
        </div>
        """, unsafe_allow_html=True)
        components.html(
            f"<script>setTimeout(() => window.location.reload(), {interval_s * 1000});</script>",
            height=0,
        )

    # Load LIVE feed data from MongoDB-backed endpoint
    with st.spinner("⚡ Loading live feed from MongoDB..."):
        articles = client.get_endpoint_articles("search_news", limit=200)

    if not articles:
        st.markdown("""
        <div style="background: #F5F5F5; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #CCCCCC;">
            <h3>No live articles available</h3>
            <p>Data may still be loading from the pipeline. Please check back in a moment.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Show data freshness
    st.markdown(f"""
    <div style="background: #FFFFFF; padding: 1rem; border-radius: 6px; border: 2px solid #000000; margin-bottom: 1.5rem;">
        <strong>📊 Live Feed Status:</strong> {len(articles)} articles loaded · 
        <strong>Updated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · 
        <strong>Source:</strong> MongoDB (Real-time Layer)
    </div>
    """, unsafe_allow_html=True)
    
    # === ORGANIZE BY SEVERITY ===
    high_severity = [a for a in articles if a.get('sentiment', 0) < -0.3]
    medium_severity = [a for a in articles if -0.3 <= a.get('sentiment', 0) <= 0.3]
    low_severity = [a for a in articles if a.get('sentiment', 0) > 0.3]
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: #000000; color: #FFFFFF; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{len(high_severity)}</div>
            <div style="font-size: 0.9rem;">HIGH SEVERITY</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #666666; color: #FFFFFF; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{len(medium_severity)}</div>
            <div style="font-size: 0.9rem;">MEDIUM SEVERITY</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #F5F5F5; color: #000000; padding: 1rem; border-radius: 8px; text-align: center; border: 2px solid #CCCCCC;">
            <div style="font-size: 2rem; font-weight: 700;">{len(low_severity)}</div>
            <div style="font-size: 0.9rem;">LOW SEVERITY</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === DISPLAY HIGH SEVERITY EVENTS ===
    if high_severity:
        st.markdown("""
        <div style="background: #000000; color: #FFFFFF; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
            <h3 style="margin: 0; font-weight: 700;">⚠️ HIGH SEVERITY EVENTS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, article in enumerate(high_severity[:5]):
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown')
            publish_date = article.get('publish_date', 'Unknown')
            sentiment = article.get('sentiment', 0)
            summary = article.get('summary', '')[:200]
            
            st.markdown(f"""
            <div class="event-card-high">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                    <h4 style="margin: 0; font-weight: 700; flex: 1;">{title}</h4>
                    <span class="severity-badge-high">CRITICAL</span>
                </div>
                <p style="color: #333333; margin-bottom: 0.75rem; line-height: 1.6;">{summary}...</p>
                <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; color: #666666;">
                    <span><strong>📰</strong> {source}</span>
                    <span><strong>📅</strong> {publish_date}</span>
                    <span><strong>📊</strong> Sentiment: {sentiment:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # === DISPLAY MEDIUM SEVERITY EVENTS ===
    if medium_severity:
        st.markdown("""
        <div style="background: #666666; color: #FFFFFF; padding: 1rem 1.5rem; border-radius: 8px; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; font-weight: 700;">📊 MEDIUM SEVERITY EVENTS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for article in medium_severity[:5]:
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown')
            publish_date = article.get('publish_date', 'Unknown')
            sentiment = article.get('sentiment', 0)
            
            st.markdown(f"""
            <div class="event-card-medium">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; font-weight: 600; flex: 1; font-size: 1rem;">{title}</h4>
                    <span class="severity-badge-medium">MODERATE</span>
                </div>
                <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; color: #666666;">
                    <span><strong>📰</strong> {source}</span>
                    <span><strong>📅</strong> {publish_date}</span>
                    <span><strong>📊</strong> {sentiment:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # === DISPLAY LOW SEVERITY EVENTS ===
    if low_severity:
        st.markdown("""
        <div style="background: #F5F5F5; color: #000000; padding: 1rem 1.5rem; border-radius: 8px; margin: 2rem 0 1rem 0; border: 2px solid #CCCCCC;">
            <h3 style="margin: 0; font-weight: 700;">✓ LOW SEVERITY EVENTS (Positive News)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for article in low_severity[:5]:
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown')
            publish_date = article.get('publish_date', 'Unknown')
            sentiment = article.get('sentiment', 0)
            
            st.markdown(f"""
            <div class="event-card-low">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; font-weight: 600; flex: 1; font-size: 1rem;">{title}</h4>
                    <span class="severity-badge-low">POSITIVE</span>
                </div>
                <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; color: #666666;">
                    <span><strong>📰</strong> {source}</span>
                    <span><strong>📅</strong> {publish_date}</span>
                    <span><strong>📊</strong> {sentiment:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show info if there are more events
    total_shown = min(5, len(high_severity)) + min(5, len(medium_severity)) + min(5, len(low_severity))
    if len(articles) > total_shown:
        st.markdown(f"""
        <div style="background: #F5F5F5; padding: 1rem; border-radius: 6px; text-align: center; margin-top: 2rem; border: 2px dashed #CCCCCC;">
            <strong>ℹ️ Showing {total_shown} of {len(articles)} events</strong><br>
            <small>Adjust filters or refresh to see more</small>
        </div>
        """, unsafe_allow_html=True)