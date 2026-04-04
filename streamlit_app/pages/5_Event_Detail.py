"""
Page 5: Event Detail View
Deep-dive into a specific news event with related articles, links, and sentiment analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from services.api_client import APIClient
from utils.constants import (
    COLORS, get_severity_from_sentiment, 
    get_color_from_sentiment, SENTIMENT_LABELS
)



def render():
    # ============ CUSTOM CSS ============
    st.markdown("""
    <style>
        .event-header {
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
            padding: 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 2rem;
        }

        .event-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .event-meta {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: rgba(255,255,255,0.8);
        }

        .article-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }

        .article-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #0ea5e9;
        }

        .sentiment-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }

        .link-section {
            background: #f9fafb;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    client = APIClient()

    def _parse_dt(value: str):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None

    def _snapshot_records(history: dict):
        records = []
        for obj in (history or {}).get("objects", []):
            dt = _parse_dt(obj.get("last_modified"))
            if dt:
                records.append({
                    "object": obj.get("object"),
                    "last_modified": obj.get("last_modified"),
                    "dt": dt
                })
        return sorted(records, key=lambda x: x["dt"], reverse=True)

    def _load_snapshot(history: dict, label: str, start_date, end_date):
        records = _snapshot_records(history or {})
        if not records:
            st.info(f"No historical snapshots found for {label}.")
            return None

        filtered = [
            r for r in records
            if start_date <= r["dt"].date() <= end_date
        ]
        if not filtered:
            st.warning(f"No {label} snapshots in selected range.")
            return None

        options = {
            f"{r['dt'].strftime('%Y-%m-%d %H:%M')} • {r['object']}": r
            for r in filtered
        }
        selected_label = st.selectbox(f"{label} snapshot", list(options.keys()))
        selected = options[selected_label]
        bucket = (history or {}).get("bucket")
        if not bucket:
            st.warning(f"Missing bucket info for {label}.")
            return None
        snapshot = client.read_object(bucket, selected["object"])
        return (snapshot or {}).get("data")

    snapshot_search = None
    snapshot_links = None
    snapshot_rss = None

    # ============ SIDEBAR ============
    with st.sidebar:
        st.title("🎯 Filter")


        event_picker = st.empty()


        with st.expander("Historical Data (MinIO)", expanded=False):
            use_snapshot = st.checkbox("Use historical snapshot", value=False)
            if use_snapshot:
                search_history = client.get_analytics_history(
                    "search_news",
                    start_date=snapshot_start.isoformat(),
                    end_date=snapshot_end.isoformat()
                )
                search_records = _snapshot_records(search_history or {})
                if not search_records:
                    st.warning("No search_news snapshots available.")
                else:
                    min_date = min(r["dt"] for r in search_records).date()
                    max_date = max(r["dt"] for r in search_records).date()
                    snapshot_col1, snapshot_col2 = st.columns(2)
                    with snapshot_col1:
                        snapshot_start = st.date_input("Snapshot start", value=min_date)
                    with snapshot_col2:
                        snapshot_end = st.date_input("Snapshot end", value=max_date)

                    snapshot_search = _load_snapshot(search_history, "Search News", snapshot_start, snapshot_end)

                    use_links_snapshot = st.checkbox("Use snapshot for links", value=True)
                    use_rss_snapshot = st.checkbox("Use snapshot for RSS", value=True)

                    if use_links_snapshot:
                        links_history = client.get_analytics_history(
                            "extract_news_links",
                            start_date=snapshot_start.isoformat(),
                            end_date=snapshot_end.isoformat()
                        )
                        snapshot_links = _load_snapshot(links_history, "Extract Links", snapshot_start, snapshot_end)

                    if use_rss_snapshot:
                        rss_history = client.get_analytics_history(
                            "feed_rss",
                            start_date=snapshot_start.isoformat(),
                            end_date=snapshot_end.isoformat()
                        )
                        snapshot_rss = _load_snapshot(rss_history, "RSS Feed", snapshot_start, snapshot_end)

        filter_enabled = st.checkbox("Enable date filter", value=False)
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input("Start date", value=datetime.utcnow().date(), disabled=not filter_enabled)
        with date_col2:
            end_date = st.date_input("End date", value=datetime.utcnow().date(), disabled=not filter_enabled)

        show_related = st.checkbox("Show Related Events", value=True)
        show_links = st.checkbox("Show Article Links", value=True)

    # ============ MAIN CONTENT ============

    st.title("📰 Event Detail View")
    st.markdown("---")

    # Load historical analytics from Gold layer
    search_gold = snapshot_search or client.get_analytics_data("search_news")
    extract_links_gold = snapshot_links or client.get_analytics_data("extract_news_links")
    feed_rss_gold = snapshot_rss or client.get_analytics_data("feed_rss")

    if not search_gold:
        st.error("Unable to load search news data from gold layer")
        st.stop()

    # Find the event
    articles = search_gold.get("articles", [])

    def _parse_date(value: str):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except Exception:
            return None

    def _in_range(article: dict) -> bool:
        d = _parse_date(article.get("publish_date"))
        if not d:
            return False
        if start_date and d < start_date:
            return False
        if end_date and d > end_date:
            return False
        return True

    if filter_enabled:
        articles = [a for a in articles if _in_range(a)]

    if not articles:
        st.error("No articles available")
        st.stop()

    def _event_label(article: dict) -> str:
        article_id = article.get("id", "N/A")
        title = article.get("title", "Untitled")
        return f"{article_id} • {title[:80]}"

    selected_idx = event_picker.selectbox(
        "Select Event",
        options=list(range(len(articles))),
        format_func=lambda i: _event_label(articles[i])
    )
    event = articles[selected_idx]

    # ============ EVENT HEADER ============
    severity = get_severity_from_sentiment(event.get('sentiment', 0))
    severity_emoji = "🔴" if severity.value == "high" else "🟡" if severity.value == "medium" else "🟢"

    st.markdown(f"""
    <div class="event-header">
        <div class="event-title">{severity_emoji} {event.get('title', 'Untitled')}</div>
        <div class="event-meta">
            <span>📅 {event.get('publish_date', 'Unknown')}</span>
            <span>📰 {event.get('source', 'Unknown')}</span>
            <span>👤 {event.get('author', 'Unknown')}</span>
            <span>🏷️ {event.get('category', 'general').title()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============ SUMMARY & SENTIMENT ============
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📝 Summary")
        st.write(event.get('summary', 'No summary available'))

    with col2:
        st.subheader("💭 Sentiment")
        sentiment_val = event.get('sentiment', 0)
        color = get_color_from_sentiment(sentiment_val)

        st.metric(
            "Score",
            f"{sentiment_val:.2f}",
            delta=None,
            delta_color="normal"
        )

        st.markdown(f"""
        <div class="sentiment-badge" style="background-color: {color}; color: white;">
            {SENTIMENT_LABELS.get(
                'positive' if sentiment_val > 0.2 else 'negative' if sentiment_val < -0.2 else 'neutral',
                'Neutral'
            )}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ============ ARTICLE LINKS (extract_news_links) ============
    if show_links:
        st.subheader("🔗 Article Links")

        if extract_links_gold and extract_links_gold.get('urls'):
            links = extract_links_gold.get('urls', [])

            st.markdown("""
            <div class="link-section">
            """, unsafe_allow_html=True)

            for i, link in enumerate(links[:5], 1):
                st.markdown(f"**{i}. [{link.split('/')[-1] or link}]({link})**")

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No related links available")

    st.markdown("---")

    # ============ RELATED EVENTS ============
    if show_related:
        st.subheader("📚 Related Events")

        # Find events from same category/location
        same_category = [
            a for a in articles 
            if a.get('category') == event.get('category') 
            and a.get('id') != event.get('id')
        ][:5]

        if same_category:
            for rel_event in same_category:
                severity_rel = get_severity_from_sentiment(rel_event.get('sentiment', 0))
                severity_emoji_rel = "🔴" if severity_rel.value == "high" else "🟡" if severity_rel.value == "medium" else "🟢"

                st.markdown(f"""
                <div class="article-card">
                    <div>
                        <strong>{severity_emoji_rel} {rel_event.get('title', 'Untitled')[:80]}</strong>
                        <span style="float: right; color: {get_color_from_sentiment(rel_event.get('sentiment', 0))};">
                            {rel_event.get('sentiment', 0):.2f}
                        </span>
                    </div>
                    <small>📰 {rel_event.get('source', 'Unknown')} | 📅 {rel_event.get('publish_date', 'Unknown')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No related events found in same category")

    st.markdown("---")

    # ============ RSS FEED DATA ============
    st.subheader("📡 News Feed Source")

    rss_entries = (feed_rss_gold or {}).get("rss_entries", [])
    rss = (feed_rss_gold or {}).get("rss_data", {}) or (rss_entries[-1] if rss_entries else {})
    data_quality = (feed_rss_gold or {}).get("data_quality", {})

    if rss:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Source Domain",
                rss.get('domain', 'N/A')
            )

        with col2:
            st.metric(
                "Content Size (KB)",
                f"{data_quality.get('content_size_kb', 0):.2f}"
            )

        with col3:
            st.metric(
                "Feed Status",
                "✅ Active" if data_quality.get('has_content') else "⚠️ Inactive"
            )

        st.markdown(f"**Source URL:** [{rss.get('source_url', '#')}]({rss.get('source_url', '#')})")

        if rss_entries:
            with st.expander("Historical RSS Entries"):
                for entry in rss_entries:
                    st.markdown(f"- {entry.get('domain', 'Unknown')} • {entry.get('source_url', 'N/A')}")
    else:
        st.info("No RSS feed data available for this event")

    st.markdown("---")

    # ============ METADATA ============
    with st.expander("📊 Full Metadata"):
        st.json({
            "id": event.get('id'),
            "title": event.get('title'),
            "source": event.get('source'),
            "source_country": event.get('source_country'),
            "category": event.get('category'),
            "sentiment": event.get('sentiment'),
            "publish_date": event.get('publish_date'),
            "language": event.get('language'),
            "has_image": bool(event.get('image')),
            "has_video": bool(event.get('video'))
        })

