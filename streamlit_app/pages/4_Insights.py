"""
Page 4: Insights - Historical Analytics Dashboard
Uses: search_news.metrics, top_news.metrics, time_series, category_breakdown, trending_keywords
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from services.api_client import get_client
from utils.constants import COLORS, SEVERITY_MAP

def render():
    """Render Insights page"""
    st.title("📈 Insights")
    st.markdown("Historical analytics, trends, and predictive patterns across civic events")
    st.markdown("---")
    
    # Try to fetch analytics data
    try:
        client = get_client()
        search_history = client.get_analytics_history("search_news")
        top_history = client.get_analytics_history("top_news")

        search_gold = (search_history or {}).get("data")
        top_gold = (top_history or {}).get("data")

        if not search_gold:
            st.error("Unable to load analytics from gold layer.")
            return

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

        st.markdown("### Historical Data (MinIO)")
        use_snapshot = st.checkbox("Use historical snapshot", value=False)
        if use_snapshot:
            search_records = _snapshot_records(search_history or {})
            if not search_records:
                st.warning("No historical snapshots available for search_news.")
            else:
                min_date = min(r["dt"] for r in search_records).date()
                max_date = max(r["dt"] for r in search_records).date()
                date_col1, date_col2 = st.columns(2)
                with date_col1:
                    snapshot_start = st.date_input("Snapshot start", value=min_date)
                with date_col2:
                    snapshot_end = st.date_input("Snapshot end", value=max_date)

                snapshot_data = _load_snapshot(search_history, "Search News", snapshot_start, snapshot_end)
                if snapshot_data:
                    search_gold = snapshot_data

                if top_history and (top_history or {}).get("objects"):
                    top_snapshot = _load_snapshot(top_history, "Top News", snapshot_start, snapshot_end)
                    if top_snapshot:
                        top_gold = top_snapshot

        analytics_data = {
            "time_series": search_gold.get("metrics", {}).get("time_series", {}),
            "category_breakdown": search_gold.get("metrics", {}).get("category_breakdown", {}),
            "sentiment_distribution": search_gold.get("metrics", {}).get("sentiment_distribution", {}),
            "trending_keywords": search_gold.get("metrics", {}).get("trending_keywords", []),
            "top_sources": search_gold.get("metrics", {}).get("top_sources", []),
            "avg_sentiment": search_gold.get("metrics", {}).get("avg_sentiment", 0),
            "total_articles": search_gold.get("metrics", {}).get("total_articles", 0),
            "top_news_total": (top_gold or {}).get("metrics", {}).get("total_articles", 0),
            "date_range": (search_gold.get("data_quality", {}) or {}).get("date_range", {})
        }
        search_articles = search_gold.get("articles", [])
        top_articles = (top_gold or {}).get("articles", [])
        if not top_articles:
            featured = (top_gold or {}).get("featured", {}) or {}
            top_articles = featured.get("latest", []) or featured.get("trending", [])

        # Date filter (historical)
        st.markdown("**Filter by publish date**")
        filter_enabled = st.checkbox("Enable date filter", value=False)
        date_col1, date_col2 = st.columns(2)

        def _parse_date(value: str):
            if not value:
                return None
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            except Exception:
                return None

        earliest = analytics_data.get("date_range", {}).get("earliest")
        latest = analytics_data.get("date_range", {}).get("latest")
        default_start = _parse_date(earliest) or datetime.utcnow().date()
        default_end = _parse_date(latest) or datetime.utcnow().date()
        with date_col1:
            start_date = st.date_input("Start date", value=default_start, disabled=not filter_enabled)
        with date_col2:
            end_date = st.date_input("End date", value=default_end, disabled=not filter_enabled)

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
            search_articles = [a for a in search_articles if _in_range(a)]
            top_articles = [a for a in top_articles if _in_range(a)]
            filtered_time_series = {}
            for k, v in analytics_data["time_series"].items():
                try:
                    kd = datetime.fromisoformat(k.replace("Z", "+00:00")).date()
                except Exception:
                    continue
                if start_date <= kd <= end_date:
                    filtered_time_series[k] = v
            analytics_data["time_series"] = filtered_time_series
        
        # Tabs for different analytics views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Trends", "🏷️ Categories", "😊 Sentiment", "📍 Areas", "🔝 Top News"
        ])
        
        # ============ TAB 1: TRENDS ============
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Articles", analytics_data["total_articles"], "📰")
            with col2:
                st.metric("Avg Sentiment", f"{analytics_data['avg_sentiment']:.3f}", "😊")
            with col3:
                st.metric("Positive %", f"{(analytics_data['sentiment_distribution']['positive']/analytics_data['total_articles']*100):.1f}%", "🟢")
            with col4:
                st.metric("Negative %", f"{(analytics_data['sentiment_distribution']['negative']/analytics_data['total_articles']*100):.1f}%", "🔴")
            
            earliest = analytics_data.get("date_range", {}).get("earliest")
            latest = analytics_data.get("date_range", {}).get("latest")
            if earliest or latest:
                st.caption(f"Historical range: {earliest or 'Unknown'} → {latest or 'Unknown'}")

            st.markdown("---")
            
            # Time series trend
            st.subheader("Article Frequency Over Time")
            
            times = list(analytics_data["time_series"].keys())
            counts = list(analytics_data["time_series"].values())
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=times, y=counts,
                mode='lines+markers',
                name='Articles',
                line=dict(color=COLORS["primary"], width=3),
                marker=dict(size=10, color=COLORS["secondary"], line=dict(color=COLORS["primary"], width=2)),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.1)',
                hovertemplate='<b>%{x}</b><br>Articles: %{y}<extra></extra>'
            ))
            
            fig_trend.update_layout(
                template='plotly_white',
                height=400,
                margin=dict(l=0, r=0, b=0, t=0),
                hovermode='x unified',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.1)'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.1)'),
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # ============ TAB 2: CATEGORIES ============
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Category Breakdown")
                
                categories = list(analytics_data["category_breakdown"].keys())
                cat_counts = list(analytics_data["category_breakdown"].values())
                
                fig_cat = go.Figure(data=[
                    go.Bar(
                        x=categories, y=cat_counts,
                        marker=dict(color=[COLORS["primary"], COLORS["secondary"]]),
                        text=cat_counts,
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                    )
                ])
                
                fig_cat.update_layout(
                    template='plotly_white',
                    height=350,
                    margin=dict(l=0, r=0, b=0, t=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.1)'),
                )
                
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with col2:
                st.subheader("Trending Keywords")
                
                keywords = [kw["keyword"] for kw in analytics_data["trending_keywords"][:10]]
                keyword_counts = [kw["count"] for kw in analytics_data["trending_keywords"][:10]]
                
                fig_kw = go.Figure(data=[
                    go.Bar(
                        y=keywords, x=keyword_counts,
                        orientation='h',
                        marker=dict(color=keyword_counts, colorscale='Blues', showscale=False),
                        text=keyword_counts,
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>Mentions: %{x}<extra></extra>'
                    )
                ])
                
                fig_kw.update_layout(
                    template='plotly_white',
                    height=350,
                    margin=dict(l=0, r=0, b=0, t=0),
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.1)'),
                    yaxis=dict(showgrid=False),
                )
                
                st.plotly_chart(fig_kw, use_container_width=True)
        
        # ============ TAB 3: SENTIMENT ============
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sentiment Distribution")
                
                sentiments = list(analytics_data["sentiment_distribution"].keys())
                sent_counts = list(analytics_data["sentiment_distribution"].values())
                sent_colors = [SEVERITY_MAP["positive"]["color"], SEVERITY_MAP["neutral"]["color"], SEVERITY_MAP["negative"]["color"]]
                
                fig_sent = go.Figure(data=[
                    go.Pie(
                        labels=sentiments,
                        values=sent_counts,
                        marker=dict(colors=sent_colors),
                        textposition='inside',
                        textinfo='label+percent+value',
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                    )
                ])
                
                fig_sent.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, b=0, t=0),
                )
                
                st.plotly_chart(fig_sent, use_container_width=True)
            
            with col2:
                st.subheader("Top Sources by Article Count")
                
                sources = [src["name"] for src in analytics_data["top_sources"]]
                src_counts = [src["count"] for src in analytics_data["top_sources"]]
                
                fig_src = go.Figure(data=[
                    go.Bar(
                        x=sources, y=src_counts,
                        marker=dict(color=COLORS["primary"]),
                        text=src_counts,
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>Articles: %{y}<extra></extra>'
                    )
                ])
                
                fig_src.update_layout(
                    template='plotly_white',
                    height=400,
                    margin=dict(l=0, r=0, b=0, t=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.1)'),
                )
                
                st.plotly_chart(fig_src, use_container_width=True)
        
        # ============ TAB 4: AREAS ============
        with tab4:
            st.subheader("Geographic Distribution")
            
            st.info("📍 City-wise article distribution and dominant categories per location")
            
            # Derive city distribution from gold search articles
            city_counts = {}
            cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
            for article in search_articles:
                title = (article.get("title", "") + " " + article.get("summary", "")).lower()
                for city in cities:
                    if city.lower() in title:
                        city_counts[city] = city_counts.get(city, 0) + 1

            col1, col2 = st.columns([2, 1])
            
            with col1:
                cities = list(city_counts.keys())
                city_values = [city_counts[city] for city in cities]
                
                fig_cities = go.Figure(data=[
                    go.Bar(
                        x=cities, y=city_values,
                        marker=dict(color=COLORS["accent"]),
                        text=city_values,
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>Articles: %{y}<extra></extra>'
                    )
                ])
                
                fig_cities.update_layout(
                    template='plotly_white',
                    height=350,
                    margin=dict(l=0, r=0, b=0, t=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.1)'),
                )
                
                st.plotly_chart(fig_cities, use_container_width=True)
            
            with col2:
                st.markdown("### Most Active Cities")
                for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"**{city}** - Articles: {count}")
        
        # ============ TAB 5: TOP NEWS ANALYTICS ============
        with tab5:
            st.subheader("Top News Editorial Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📰 Top Headlines")
                if top_articles:
                    for i, article in enumerate(top_articles[:5], 1):
                        st.markdown(f"{i}. **{article.get('title', 'Untitled')}**")
                    with st.expander("Show all top news articles"):
                        st.dataframe(
                            [
                                {
                                    "title": a.get("title", "Untitled"),
                                    "source": a.get("source", "Unknown"),
                                    "publish_date": a.get("publish_date", "Unknown"),
                                    "sentiment": a.get("sentiment", 0),
                                    "category": a.get("category", "general"),
                                    "url": a.get("url", "")
                                }
                                for a in top_articles
                            ],
                            use_container_width=True
                        )
                else:
                    st.info("No top news articles available.")
            
            with col2:
                st.markdown("### 🎯 Editorial Insights")
                top_metrics = (top_gold or {}).get("metrics", {})
                dominant_category = max(
                    top_metrics.get("category_breakdown", {}).items(),
                    default=("N/A", 0),
                    key=lambda x: x[1]
                )[0]
                avg_top_sentiment = top_metrics.get("avg_sentiment", 0)
                st.markdown(f"""
                **Dominant Theme:** {dominant_category.title()}
                
                **Sentiment Trend:** {avg_top_sentiment:+.3f}
                
                **Coverage Depth:** {top_metrics.get('total_articles', 0)} articles
                
                **Update Frequency:** Hourly
                """)
            
            st.markdown("---")
            st.markdown("### Top News Metrics Summary")
            
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                st.metric("Total Top Stories", top_metrics.get("total_articles", 0), "📰")
            with metrics_col2:
                st.metric("Avg Top News Sentiment", f"{top_metrics.get('avg_sentiment', 0):.3f}", "😊")
            with metrics_col3:
                st.metric("Most Common Category", dominant_category.title() if dominant_category else "N/A", "🏷️")
            with metrics_col4:
                top_source = (top_metrics.get("top_sources") or [{}])[0].get("name", "N/A")
                st.metric("Leading Source", top_source, "📡")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        st.info("Please ensure the API server is running and accessible")
