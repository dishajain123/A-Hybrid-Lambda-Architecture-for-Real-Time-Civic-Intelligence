import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import MarkerCluster

from components.header      import render_header, render_section_title, render_divider
from components.severity_badge import inject_badge_css
from services.api_client    import get_client
from utils.constants        import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_MAP_ZOOM
import utils.dummy_data     as _dummy

_CSS = """
<style>
.map-legend {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:12px;
    padding:1.1rem 1.25rem; margin-bottom:1rem;
    box-shadow:0 1px 4px rgba(0,0,0,.05);
}
.map-legend h4 { margin:0 0 .75rem; font-size:.85rem; font-weight:700; }
.legend-row { display:flex; align-items:center; gap:.5rem; margin:.35rem 0; font-size:.8rem; color:#444; }
.legend-dot { width:12px; height:12px; border-radius:50%; flex-shrink:0; }
.city-card {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:10px;
    padding:.8rem 1rem; margin-bottom:.6rem; cursor:pointer;
    transition:all .18s; box-shadow:0 1px 3px rgba(0,0,0,.04);
}
.city-card:hover { border-color:#000; box-shadow:0 3px 10px rgba(0,0,0,.08); }
.city-name { font-weight:700; font-size:.875rem; color:#111; }
.city-meta { font-size:.75rem; color:#888; margin-top:.2rem; }
.city-articles { font-size:1.1rem; font-weight:800; color:#000; float:right; }
</style>
"""

def _get_marker_color(sentiment: float) -> str:
    if sentiment > 0.3:  return "#16a34a"
    if sentiment > 0.0:  return "#65a30d"
    if sentiment > -0.3: return "#ca8a04"
    return "#dc2626"

def _get_radius(count: int) -> int:
    return min(8 + count * 1.5, 35)

def _has_valid_coordinates(loc: dict) -> bool:
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    return lat is not None and lon is not None

def _merge_locations(primary: list, secondary: list, target_count: int = 12) -> list:
    """Merge locations by city name, preferring primary (real) data."""
    merged = []
    seen = set()

    for source in (primary, secondary):
        for loc in source:
            city = (loc.get("city") or "").strip().lower()
            if not city or city in seen or not _has_valid_coordinates(loc):
                continue
            merged.append(loc)
            seen.add(city)
            if len(merged) >= target_count:
                return merged

    return merged

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    inject_badge_css()
    render_header("Geo Intelligence", "Geospatial view of civic events and regional sentiment", "🗺️", live=False)

    client = get_client()

    if st.session_state.get("auto_refresh"):
        interval = int(st.session_state.get("refresh_interval", 30))
        components.html(
            f"<script>setTimeout(()=>window.location.reload(),{interval*1000});</script>",
            height=0,
        )

    with st.spinner("Loading geo-intelligence data…"):
        real_geo_data = client.get_geo_coordinates() or []
        dummy_geo_data = _dummy.get_geo_data()

        if not real_geo_data:
            geo_data = dummy_geo_data
        else:
            # If backend has too few points, enrich with dummy so map remains useful.
            geo_data = _merge_locations(real_geo_data, dummy_geo_data, target_count=16)

        articles = client.get_endpoint_articles("search_news", limit=100)
        if not articles:
            articles = _dummy.get_articles(limit=50)

    # ── Controls ─────────────────────────────────────────────────────────────
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        min_articles = st.slider("Min articles threshold", 1, 20, 1, key="map_min_art")
    with col_ctrl2:
        show_clusters = st.checkbox("Enable clustering", value=False, key="map_cluster")
    with col_ctrl3:
        map_tiles = st.selectbox("Map style", ["CartoDB positron","OpenStreetMap","CartoDB dark_matter"], key="map_tile")

    render_divider()

    col_map, col_list = st.columns([3, 1])

    with col_map:
        # Build folium map
        m = folium.Map(
            location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE],
            zoom_start=DEFAULT_MAP_ZOOM,
            tiles=map_tiles,
        )

        layer = MarkerCluster() if show_clusters else None
        if layer:
            layer.add_to(m)

        active_locs = [g for g in geo_data if g.get("article_count", 0) >= min_articles]

        for loc in active_locs:
            lat  = loc.get("latitude")
            lon  = loc.get("longitude")
            city = loc.get("city", "Unknown")
            cnt  = loc.get("article_count", 1)
            avg  = loc.get("avg_sentiment", 0)
            if not lat or not lon:
                continue
            color  = _get_marker_color(avg)
            radius = _get_radius(cnt)
            sent_label = "Positive" if avg>0.2 else ("Negative" if avg<-0.2 else "Neutral")
            popup_html = f"""
            <div style="font-family:Inter,sans-serif;width:200px">
              <h4 style="margin:0 0 .4rem;font-size:.9rem">{city}</h4>
              <table style="width:100%;font-size:.78rem">
                <tr><td><b>Events</b></td><td>{cnt}</td></tr>
                <tr><td><b>Avg Sentiment</b></td><td style="color:{color}">{avg:+.3f}</td></tr>
                <tr><td><b>Mood</b></td><td>{sent_label}</td></tr>
                <tr><td><b>Region</b></td><td>{loc.get('region','India')}</td></tr>
              </table>
            </div>"""
            circle = folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.65,
                opacity=0.9,
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=f"{city} — {cnt} events ({avg:+.2f})",
            )
            if show_clusters and layer:
                circle.add_to(layer)
            else:
                circle.add_to(m)

        # Render map as raw HTML to avoid streamlit-folium JSON marshalling issues.
        import io
        buf = io.BytesIO()
        m.save(buf, close_file=False)
        html_content = buf.getvalue().decode()
        components.html(html_content, height=540, scrolling=False)

    with col_list:
        render_section_title(f"Active Cities ({len(active_locs)})")
        sorted_locs = sorted(active_locs, key=lambda x: x.get("article_count",0), reverse=True)
        for loc in sorted_locs[:15]:
            city = loc.get("city","Unknown")
            cnt  = loc.get("article_count",0)
            avg  = loc.get("avg_sentiment",0)
            color = _get_marker_color(avg)
            st.markdown(f"""
            <div class="city-card">
              <span class="city-articles" style="color:{color}">{cnt}</span>
              <div class="city-name">{city}</div>
              <div class="city-meta">Sentiment: <b style="color:{color}">{avg:+.3f}</b></div>
            </div>
            """, unsafe_allow_html=True)

    render_divider()

    # ── Summary stats below map ───────────────────────────────────────────────
    render_section_title("Geographic Intelligence Summary")
    c1, c2, c3, c4 = st.columns(4)
    total_events = sum(g.get("article_count",0) for g in active_locs)
    overall_sent = sum(g.get("avg_sentiment",0)*g.get("article_count",1) for g in active_locs) / max(total_events,1)
    hottest = max(active_locs, key=lambda x: x.get("article_count",0), default={})
    most_pos = max(active_locs, key=lambda x: x.get("avg_sentiment",-99), default={})

    c1.metric("Active Locations", len(active_locs))
    c2.metric("Total Geo Events", total_events)
    c3.metric("Weighted Sentiment", f"{overall_sent:+.3f}")
    c4.metric("Most Active City", hottest.get("city","N/A").split(",")[0])
