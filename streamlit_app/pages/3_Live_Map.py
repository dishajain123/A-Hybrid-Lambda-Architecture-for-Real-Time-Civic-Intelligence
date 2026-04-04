import streamlit as st
import folium
import streamlit.components.v1 as components
try:
    from streamlit_folium import st_folium, folium_static
except Exception:
    st_folium = None
    folium_static = None
from components.header import render_header, render_divider, render_section_title
from components.severity_badge import get_severity_color, get_severity_emoji
from services.api_client import get_client
from utils.constants import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_MAP_ZOOM

def render():
    """Render Live Map page with proper backend data integration"""
    
    render_header("Live Map", "Geographic distribution of civic events", "🗺️")
    
    # Info banner explaining the map
    st.info("""
    **🗺️ What you're seeing:** This map shows real-time civic events across India based on news articles. 
    Each **hotspot** (colored circle) represents a location with tracked events. The size and color indicate 
    the number of events and their sentiment.
    """)
    
    # Get data from API
    client = get_client()
    
    # Auto-refresh for live page only
    if st.session_state.get("auto_refresh"):
        interval_s = int(st.session_state.get("refresh_interval", 30))
        components.html(
            f"<script>setTimeout(() => window.location.reload(), {interval_s * 1000});</script>",
            height=0,
        )

    with st.spinner("Loading map data from backend..."):
        # Fetch geocoded data from backend
        geo_data = client.get_endpoint_articles("geo_coordinates", limit=500)
        articles = client.get_endpoint_articles("search_news", limit=200)
    
    # === CREATE MAP ===
    m = folium.Map(
        location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE],
        zoom_start=DEFAULT_MAP_ZOOM,
        tiles="OpenStreetMap"
    )
    
    # === ADD MARKERS FROM GEO_COORDINATES BACKEND DATA ===
    if geo_data and isinstance(geo_data, list):
        st.success(f"✅ Loaded {len(geo_data)} geocoded locations from backend")
        
        # Process geocoded data
        for location in geo_data:
            city = location.get('city', 'Unknown')
            lat = location.get('latitude')
            lon = location.get('longitude')
            article_count = location.get('article_count', 0)
            region = location.get('region', '')
            country = location.get('country', 'India')
            
            # Skip if missing coordinates
            if lat is None or lon is None:
                continue
            
            # Get sentiment data for this location
            avg_sentiment = location.get('avg_sentiment', 0)
            
            # Determine color based on sentiment
            if avg_sentiment > 0.2:
                color = '#10b981'  # Green - Positive
                severity = 'Low Severity (Positive)'
                severity_emoji = '🟢'
            elif avg_sentiment < -0.2:
                color = '#ef4444'  # Red - Negative
                severity = 'High Severity (Negative)'
                severity_emoji = '🔴'
            else:
                color = '#f59e0b'  # Orange - Neutral
                severity = 'Medium Severity (Neutral)'
                severity_emoji = '🟡'
            
            # Calculate marker size (scale with article count)
            base_radius = 8
            radius = base_radius + min(article_count * 1.5, 30)  # Cap at reasonable size
            
            # Create detailed popup
            popup_html = f"""
            <div style='font-family: Arial; width: 280px; padding: 10px;'>
                <h3 style='margin: 0 0 10px 0; color: #1f77b4; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px;'>
                    📍 {city}
                </h3>
                <div style='background: #f9fafb; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                    <p style='margin: 5px 0; font-size: 14px;'>
                        <strong>Location:</strong> {region}, {country}
                    </p>
                    <p style='margin: 5px 0; font-size: 14px;'>
                        <strong>Coordinates:</strong> {lat:.4f}, {lon:.4f}
                    </p>
                </div>
                <div style='background: #fef3c7; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>
                    <p style='margin: 5px 0; font-size: 16px; font-weight: bold;'>
                        📊 <strong>{article_count}</strong> events tracked
                    </p>
                    <p style='margin: 5px 0; font-size: 14px;'>
                        <strong>Avg Sentiment:</strong> {avg_sentiment:+.2f}
                    </p>
                    <p style='margin: 5px 0; font-size: 14px;'>
                        {severity_emoji} <strong>{severity}</strong>
                    </p>
                </div>
                <div style='font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; padding-top: 8px;'>
                    <strong>💡 What this means:</strong><br>
                    • Circle size = Number of events<br>
                    • Circle color = Overall sentiment<br>
                    • Click for event details
                </div>
            </div>
            """
            
            # Add circle marker with tooltip
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{city}: {article_count} events ({severity_emoji})",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=2,
                opacity=0.8
            ).add_to(m)
    
    # Fallback to article-based mapping if geo_coordinates is empty
    elif articles:
        st.warning("⚠️ No geocoded data found from backend. Using fallback city detection from articles.")
        
        # Fallback: Default Indian cities with coordinates
        cities = {
            "Mumbai": [19.0760, 72.8777],
            "Delhi": [28.7041, 77.1025],
            "Bangalore": [12.9716, 77.5946],
            "Chennai": [13.0827, 80.2707],
            "Kolkata": [22.5726, 88.3639],
            "Hyderabad": [17.3850, 78.4867]
        }
        
        # Count articles by city mentions
        location_counts = {}
        location_sentiments = {}
        
        for article in articles:
            title_lower = article.get('title', '').lower() + article.get('summary', '').lower()
            
            for city, coords in cities.items():
                if city.lower() in title_lower:
                    if city not in location_counts:
                        location_counts[city] = 0
                        location_sentiments[city] = []
                    
                    location_counts[city] += 1
                    location_sentiments[city].append(article.get('sentiment', 0))
        
        # Add markers for cities with articles
        for city, coords in cities.items():
            if city in location_counts:
                count = location_counts[city]
                avg_sentiment = sum(location_sentiments[city]) / len(location_sentiments[city])
                
                # Determine color
                color = get_severity_color(avg_sentiment)
                
                # Create popup
                popup_html = f"""
                <div style='font-family: Arial; width: 250px;'>
                    <h4 style='margin: 0;'>{city}</h4>
                    <p style='margin: 5px 0;'><strong>{count}</strong> articles tracked</p>
                    <p style='margin: 5px 0;'><strong>Sentiment:</strong> {avg_sentiment:+.2f}</p>
                    <p style='margin: 5px 0; font-size: 0.9em;'>
                        {get_severity_emoji(avg_sentiment)} Top category: {articles[0].get('category', 'general')}
                    </p>
                </div>
                """
                
                folium.CircleMarker(
                    location=coords,
                    radius=10 + (count * 2),
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{city}: {count} events",
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(m)
    else:
        st.error("❌ No data available from backend. Please check API connection.")
    
    # === DISPLAY MAP ===
    st.markdown("### 🌍 Interactive Event Map")
    st.markdown("""
    **How to use this map:**
    - **Hover** over a hotspot to see quick info
    - **Click** on a hotspot to see detailed event statistics
    - **Zoom** and pan to explore different regions
    """)
    
    if folium_static is not None:
        folium_static(m, width=1400, height=600)
    else:
        st_folium(m, width=1400, height=600)
    
    render_divider()
    
    # === ENHANCED LEGEND WITH EXPLANATIONS ===
    st.markdown("### 📖 Map Legend & Guide")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;'>
        <h4 style='margin: 0 0 15px 0;'>🎯 What Are Hotspots?</h4>
        <p style='margin: 0; font-size: 16px; line-height: 1.6;'>
            <strong>Hotspots</strong> are colored circles on the map that represent locations where civic events 
            have been detected from news articles. Each hotspot aggregates multiple news events from that location.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: #10b981; padding: 15px; border-radius: 10px; color: white;'>
            <h4 style='margin: 0 0 10px 0;'>🟢 Low Severity (Green)</h4>
            <p style='margin: 0; font-size: 14px;'>
                <strong>Sentiment:</strong> Positive (>0.2)<br>
                <strong>Indicates:</strong> Positive developments, good news, community events<br>
                <strong>Example:</strong> Development projects, celebrations, achievements
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #f59e0b; padding: 15px; border-radius: 10px; color: white;'>
            <h4 style='margin: 0 0 10px 0;'>🟡 Medium Severity (Orange)</h4>
            <p style='margin: 0; font-size: 14px;'>
                <strong>Sentiment:</strong> Neutral (-0.2 to 0.2)<br>
                <strong>Indicates:</strong> Balanced reporting, routine events<br>
                <strong>Example:</strong> Policy announcements, general updates, administrative news
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: #ef4444; padding: 15px; border-radius: 10px; color: white;'>
            <h4 style='margin: 0 0 10px 0;'>🔴 High Severity (Red)</h4>
            <p style='margin: 0; font-size: 14px;'>
                <strong>Sentiment:</strong> Negative (<-0.2)<br>
                <strong>Indicates:</strong> Crisis events, alerts, concerning news<br>
                <strong>Example:</strong> Protests, accidents, infrastructure issues
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    render_divider()
    
    # === HOTSPOT SIZE EXPLANATION ===
    st.markdown("### 📏 Understanding Hotspot Sizes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: #f3f4f6; padding: 20px; border-radius: 10px;'>
            <h4 style='margin: 0 0 10px 0; color: #1f77b4;'>Size Indicates Activity Level</h4>
            <ul style='margin: 5px 0; padding-left: 20px;'>
                <li><strong>Small circles:</strong> 1-5 events</li>
                <li><strong>Medium circles:</strong> 6-15 events</li>
                <li><strong>Large circles:</strong> 16+ events</li>
            </ul>
            <p style='margin: 10px 0 0 0; font-size: 14px; color: #6b7280;'>
                Larger hotspots indicate more news activity in that location
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #f3f4f6; padding: 20px; border-radius: 10px;'>
            <h4 style='margin: 0 0 10px 0; color: #1f77b4;'>Data Source</h4>
            <ul style='margin: 5px 0; padding-left: 20px;'>
                <li><strong>Backend Endpoint:</strong> <code>geo_coordinates</code></li>
                <li><strong>Data Freshness:</strong> Real-time</li>
                <li><strong>Update Frequency:</strong> Continuous</li>
            </ul>
            <p style='margin: 10px 0 0 0; font-size: 14px; color: #6b7280;'>
                All data is validated and geocoded by the backend API
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    render_divider()
    
    # === CITY STATISTICS TABLE ===
    st.markdown("### 📊 Event Distribution by Location")
    
    if geo_data and isinstance(geo_data, list):
        # Create statistics from geo_data
        stats_data = []
        for location in geo_data:
            if location.get('latitude') and location.get('longitude'):
                stats_data.append({
                    'City': location.get('city', 'Unknown'),
                    'Region': location.get('region', ''),
                    'Events': location.get('article_count', 0),
                    'Avg Sentiment': f"{location.get('avg_sentiment', 0):+.2f}",
                    'Severity': '🟢' if location.get('avg_sentiment', 0) > 0.2 else ('🔴' if location.get('avg_sentiment', 0) < -0.2 else '🟡')
                })
        
        if stats_data:
            # Sort by event count
            stats_data.sort(key=lambda x: x['Events'], reverse=True)
            
            # Display as table
            import pandas as pd
            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Locations", len(stats_data))
            with col2:
                total_events = sum(loc['Events'] for loc in stats_data)
                st.metric("Total Events", total_events)
            with col3:
                avg_events = total_events / len(stats_data) if stats_data else 0
                st.metric("Avg Events/Location", f"{avg_events:.1f}")
            with col4:
                high_severity = sum(1 for loc in stats_data if loc['Severity'] == '🔴')
                st.metric("High Severity Locations", high_severity)
    elif articles:
        # Fallback statistics
        cities = {
            "Mumbai": [19.0760, 72.8777],
            "Delhi": [28.7041, 77.1025],
            "Bangalore": [12.9716, 77.5946],
            "Chennai": [13.0827, 80.2707],
            "Kolkata": [22.5726, 88.3639],
            "Hyderabad": [17.3850, 78.4867]
        }
        
        location_counts = {}
        for article in articles:
            title_lower = article.get('title', '').lower() + article.get('summary', '').lower()
            for city in cities:
                if city.lower() in title_lower:
                    location_counts[city] = location_counts.get(city, 0) + 1
        
        cols = st.columns(3)
        for idx, (city, count) in enumerate(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)):
            with cols[idx % 3]:
                st.metric(city, count, help=f"Articles mentioning {city}")
    
    render_divider()
    
    # === TECHNICAL INFORMATION ===
    with st.expander("🔧 Technical Details & Data Flow"):
        st.markdown("""
        **Backend Integration:**
        - **Primary Endpoint:** `geo_coordinates` (FastAPI)
        - **Fallback Endpoint:** `search_news` (article-based detection)
        - **Data Validation:** All coordinates validated by backend
        - **Geocoding:** Automatic location extraction from news content
        
        **Data Pipeline:**
        ```
        News Articles → NLP Processing → Entity Extraction → Geocoding → 
        geo_coordinates API → Frontend Map Visualization
        ```
        
        **Real-time Updates:**
        - Map refreshes every 30 seconds (if auto-refresh enabled)
        - Backend data updated continuously from news streams
        - No frontend caching (always fresh data)
        
        **Hotspot Calculation:**
        - **Size:** Proportional to article_count (min: 8px, max: 38px)
        - **Color:** Based on avg_sentiment (-1 to +1 scale)
        - **Position:** Exact lat/lon from backend geocoding
        """)

if __name__ == "__main__":
    render()