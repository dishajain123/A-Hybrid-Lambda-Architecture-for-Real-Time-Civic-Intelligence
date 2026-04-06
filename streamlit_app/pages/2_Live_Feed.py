import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import hashlib

from components.header      import render_header, render_section_title, render_divider
from components.event_card  import render_event_card, render_compact_card, inject_card_css
from components.filters     import render_filters, apply_filters
from components.severity_badge import inject_badge_css
from services.api_client    import get_client, reset_client
import utils.dummy_data     as _dummy

_CSS = """
<style>
.feed-stats { display:flex; gap:.75rem; margin-bottom:1.5rem; flex-wrap:wrap; }
.feed-stat-pill {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:10px;
    padding:.6rem 1rem; flex:1 1 110px; text-align:center;
    box-shadow:0 1px 3px rgba(0,0,0,.05);
}
.feed-stat-val { font-size:1.4rem; font-weight:800; color:#000; line-height:1; }
.feed-stat-lbl { font-size:.68rem; color:#888; text-transform:uppercase; letter-spacing:.5px; font-weight:600; margin-top:.15rem; }
.stream-header {
    background:#000; color:#fff; border-radius:10px;
    padding:.8rem 1.25rem; display:flex; align-items:center;
    justify-content:space-between; margin-bottom:1rem;
}
.stream-header-title { font-weight:700; font-size:.95rem; }
.live-dot {
    width:8px; height:8px; background:#ef4444; border-radius:50%;
    display:inline-block; margin-right:.4rem;
    animation:pulse-dot 1.5s infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.5; transform:scale(.8); }
}
.refresh-stamp { font-size:.72rem; color:#888; text-align:right; margin-bottom:.75rem; }
.pagination-bar {
    background:#f5f5f5; border-radius:10px; padding:.75rem 1.1rem;
    font-size:.82rem; color:#444; margin-bottom:1rem;
    display:flex; gap:1.5rem; flex-wrap:wrap; align-items:center;
}
.pagination-bar strong { color:#000; }
.rss-panel {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:12px;
    padding:1rem 1.1rem; font-size:.82rem; margin-bottom:1rem;
}
.rss-panel h5 { margin:0 0 .6rem; font-size:.85rem; font-weight:700; color:#000; }
.rss-preview {
    background:#f5f5f5; border-radius:8px; padding:.65rem .85rem;
    font-size:.72rem; font-family:monospace; color:#555;
    max-height:100px; overflow-y:auto; white-space:pre-wrap;
    word-break:break-all; margin-top:.5rem; line-height:1.5;
}
.links-panel {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:12px;
    padding:1rem 1.1rem; margin-bottom:1rem;
}
.links-panel h5 { margin:0 0 .6rem; font-size:.85rem; font-weight:700; }
.extracted-link {
    display:block; font-size:.73rem; color:#000; padding:.3rem 0;
    border-bottom:1px solid #f0f0f0; text-decoration:none;
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.extracted-link:hover { text-decoration:underline; }
.extracted-link:last-child { border-bottom:none; }
</style>
"""

def _parse_dt(value: str) -> datetime:
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return datetime.min

def _pulse_order(articles: list, pulse: int) -> list:
    """Live-like order: recent + impactful + small pulse jitter."""
    def _score(a: dict):
        recency = _parse_dt(a.get("publish_date")).timestamp()
        impact = abs(float(a.get("sentiment", 0)))
        stable_id = str(a.get("id") or a.get("url") or a.get("title") or "")
        jitter = int(hashlib.md5(f"{stable_id}-{pulse}".encode()).hexdigest()[:6], 16) % 1000
        return (recency, impact, jitter)

    return sorted(articles or [], key=_score, reverse=True)

def _windowed(items: list, size: int, pulse: int) -> list:
    """Rotate visible slice by pulse so refreshed pages show new cards."""
    if not items:
        return []
    if len(items) <= size:
        return items
    start = (pulse * 17) % len(items)
    ordered = items[start:] + items[:start]
    return ordered[:size]

def _cycle_reorder(items: list, pulse: int) -> list:
    """Deterministic reshuffle per cycle so visible cards change on refresh."""
    return sorted(
        items or [],
        key=lambda a: hashlib.md5(
            f"{a.get('id') or a.get('url') or a.get('title')}-{pulse}".encode()
        ).hexdigest()
    )

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    inject_card_css()
    inject_badge_css()
    render_header("Live Feed", "Real-time civic event stream from Kafka → Bronze layer", "📡", live=True)

    # Force fresh backend check each render so new data can be pulled in quickly.
    reset_client()
    client = get_client()

    # Auto-refresh
    if st.session_state.get("auto_refresh"):
        interval = int(st.session_state.get("refresh_interval", 30))
        components.html(
            f"<script>setTimeout(()=>window.location.reload(),{interval*1000});</script>",
            height=0,
        )

    # Controls
    col_a, col_b = st.columns([5, 2])
    with col_a:
        filters = render_filters(show_category=True, show_sentiment=True, show_search=True, key_prefix="lf")
    with col_b:
        if st.button("Refresh Now", type="secondary", use_container_width=True):
            st.session_state["lf_manual_refresh_tick"] = st.session_state.get("lf_manual_refresh_tick", 0) + 1
            st.rerun()

    # Fetch
    with st.spinner("Streaming latest events from Kafka…"):
        articles = client.get_endpoint_articles("search_news", limit=80)
        if not articles:
            articles = _dummy.get_articles(limit=80)
        top_arts  = client.get_endpoint_articles("top_news", limit=10)
        if not top_arts:
            top_arts = _dummy.get_top_news(limit=10)

    filtered   = apply_filters(articles, filters)
    pulse_window = max(10, int(st.session_state.get("refresh_interval", 30)))
    auto_pulse = int(datetime.utcnow().timestamp() // pulse_window)
    manual_tick = int(st.session_state.get("lf_manual_refresh_tick", 0))
    pulse = auto_pulse + manual_tick
    filtered = _pulse_order(filtered, pulse)
    top_arts = _pulse_order(top_arts, pulse)
    visible_feed = _windowed(filtered, 60, pulse)
    visible_top = _windowed(top_arts, 8, pulse)
    display_feed = _cycle_reorder(visible_feed, pulse)
    display_top = _cycle_reorder(visible_top, pulse)
    pagination = _dummy.get_search_pagination()
    rss        = _dummy.get_rss_feed()
    ext_links  = _dummy.get_extracted_links()

    # Pagination info bar
    st.markdown(f"""
    <div class="pagination-bar">
      <span>📦 Showing <strong>{len(filtered)}</strong> of <strong>{pagination['number']}</strong> fetched</span>
      <span>🗄️ Total available in API: <strong>{pagination['available']:,}</strong></span>
      <span>📍 Offset: <strong>{pagination['offset']}</strong></span>
      <span>🕐 Last updated: <strong>{datetime.now().strftime('%H:%M:%S')}</strong></span>
      <span>⚡ Feed cycle: <strong>#{pulse}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    # Stats bar
    pos   = sum(1 for a in filtered if a.get("sentiment",0) >  0.2)
    neg   = sum(1 for a in filtered if a.get("sentiment",0) < -0.2)
    neu   = len(filtered) - pos - neg
    avg_s = sum(a.get("sentiment",0) for a in filtered) / max(len(filtered),1)

    st.markdown(f"""
    <div class="feed-stats">
      <div class="feed-stat-pill"><div class="feed-stat-val">{len(filtered)}</div><div class="feed-stat-lbl">Events</div></div>
      <div class="feed-stat-pill"><div class="feed-stat-val" style="color:#16a34a">{pos}</div><div class="feed-stat-lbl">Positive</div></div>
      <div class="feed-stat-pill"><div class="feed-stat-val" style="color:#dc2626">{neg}</div><div class="feed-stat-lbl">Negative</div></div>
      <div class="feed-stat-pill"><div class="feed-stat-val" style="color:#888">{neu}</div><div class="feed-stat-lbl">Neutral</div></div>
      <div class="feed-stat-pill"><div class="feed-stat-val">{avg_s:+.3f}</div><div class="feed-stat-lbl">Avg Sentiment</div></div>
    </div>
    """, unsafe_allow_html=True)

    render_divider()
    col_main, col_side = st.columns([3, 1])

    # ── Main feed ─────────────────────────────────────────────────────────────
    with col_main:
        st.markdown(f"""
        <div class="stream-header">
          <span><span class="live-dot"></span><span class="stream-header-title">KAFKA → BRONZE LAYER STREAM</span></span>
          <span style="font-size:.75rem;color:#aaa">{len(filtered)} events loaded</span>
        </div>
        """, unsafe_allow_html=True)

        if not filtered:
            st.info("No events match your filters.")
        else:
            tabs = st.tabs(["All Events","High Impact","Positive","Negative"])
            with tabs[0]:
                for i, a in enumerate(display_feed[:30]):
                    render_event_card(a, key_prefix=f"lf_all_{i}", show_inspect=False)
            with tabs[1]:
                high_impact = sorted(display_feed, key=lambda x: abs(x.get("sentiment",0)), reverse=True)
                high_impact = _windowed(high_impact, min(15, len(high_impact)), pulse)
                for i, a in enumerate(high_impact):
                    render_event_card(a, key_prefix=f"lf_hi_{i}", show_inspect=False)
            with tabs[2]:
                positive = [x for x in display_feed if x.get("sentiment",0)>0.2]
                positive = _windowed(positive, min(20, len(positive)), pulse)
                for i, a in enumerate(positive):
                    render_event_card(a, key_prefix=f"lf_pos_{i}", show_inspect=False)
            with tabs[3]:
                negative = sorted([x for x in display_feed if x.get("sentiment",0)<-0.2],
                                  key=lambda x: x["sentiment"])
                negative = _windowed(negative, min(20, len(negative)), pulse)
                for i, a in enumerate(negative):
                    render_event_card(a, key_prefix=f"lf_neg_{i}", show_inspect=False)

    # ── Sidebar panel ─────────────────────────────────────────────────────────
    with col_side:
        render_section_title("Top Stories")
        for a in display_top[:6]:
            render_compact_card(a)

        render_divider()

        # RSS Feed panel — shows source_url, content_length, preview
        render_section_title("RSS Feed Source")
        st.markdown(f"""
        <div class="rss-panel">
          <h5>📡 Active Feed</h5>
          <div style="margin-bottom:.4rem">
            <a href="{rss['source_url']}" target="_blank" style="color:#000;font-size:.8rem;font-weight:600">
              {rss['source_url']}
            </a>
          </div>
          <div style="font-size:.75rem;color:#666;margin-bottom:.25rem">
            📦 Content length: <strong>{rss['content_length']:,} bytes</strong>
          </div>
          <div style="font-size:.75rem;color:#666;margin-bottom:.25rem">
            🕐 Ingested: <strong>{rss.get('ingestion_time','')[:16]}</strong>
          </div>
          <div style="font-size:.75rem;color:#666;margin-bottom:.4rem">
            ⚡ Layer: <strong>{rss.get('layer','speed').upper()}</strong>
          </div>
          <div style="font-size:.72rem;color:#888;margin-bottom:.2rem;font-weight:600">RSS PREVIEW</div>
          <div class="rss-preview">{rss['preview'][:400]}</div>
        </div>
        """, unsafe_allow_html=True)

        render_divider()

        # Extracted links panel — shows extracted_urls + count
        render_section_title("Extracted Links")
        st.markdown(f"""
        <div class="links-panel">
          <h5>🔗 extract_news_links <span style="background:#e5e5e5;border-radius:20px;
            padding:.1rem .5rem;font-size:.7rem;margin-left:.3rem">{ext_links['count']} URLs</span></h5>
          <div style="font-size:.72rem;color:#888;margin-bottom:.5rem">
            Ingested: {ext_links.get('ingestion_time','')[:16]} · Layer: {ext_links.get('layer','speed').upper()}
          </div>
          {"".join(f'<a class="extracted-link" href="{u}" target="_blank" title="{u}">{u.split("/")[2]} › {u.split("/")[-1][:35]}…</a>' for u in ext_links['extracted_urls'])}
        </div>
        """, unsafe_allow_html=True)
