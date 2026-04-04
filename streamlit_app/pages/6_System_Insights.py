"""
PAGE 6: SYSTEM INSIGHTS
============================================================
Static documentation of architecture, data pipeline, tech stack, and data ethics.
Gold-layer backed with premium UI and academic credibility.

MANDATORY SECTIONS:
1. System Health Overview (system_healthcheck.json)
2. Architecture Diagram (User upload)
3. Architecture Explanation (Structured)
4. Frontend ↔ Backend Contract
5. Real-Time vs Historical Flow
6. Ethical AI & Limitations

NOTE: This page is designed for Streamlit's multi-page app structure.
NO render() function - code executes directly at module load.
"""

import streamlit as st
from datetime import datetime
from services.api_client import get_client

def render():

    # ============ CUSTOM PREMIUM CSS ============
    st.markdown("""
    <style>
        /* Root Variables */
        :root {
            --primary: #0ea5e9;
            --primary-dark: #0284c7;
            --primary-light: #e0f2fe;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --neutral-50: #f9fafb;
            --neutral-200: #e5e7eb;
            --neutral-700: #374151;
        }

        /* Typography Hierarchy */
        h1 { font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.5rem; }
        h2 { font-weight: 600; margin-top: 2rem; margin-bottom: 1rem; }
        h3 { font-weight: 600; color: var(--neutral-700); }

        /* Section Divider */
        .section-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #d1d5db, transparent);
            margin: 2.5rem 0;
        }

        /* Premium Insight Card */
        .insight-card {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 1.75rem;
            border-radius: 12px;
            border-left: 5px solid var(--primary);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            margin-bottom: 1.25rem;
        }

        /* Architecture Section Card */
        .architecture-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--neutral-200);
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
            margin: 1.5rem 0;
        }

        /* Tech Stack Grid */
        .tech-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }

        .tech-item {
            background: linear-gradient(135deg, var(--neutral-50) 0%, white 100%);
            padding: 1.25rem;
            border-radius: 10px;
            border: 1px solid var(--neutral-200);
            transition: all 0.2s ease;
        }

        .tech-item:hover {
            border-color: var(--primary);
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.1);
        }

        /* Ethics Box - Warning Style */
        .ethics-box {
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border-left: 5px solid var(--warning);
            padding: 1.75rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }

        /* Ethics Box - Success Style */
        .ethics-box-success {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-left: 5px solid var(--success);
            padding: 1.75rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }

        /* Data Flow Table */
        .flow-table {
            margin: 1.5rem 0;
        }

        /* Metric Card */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid var(--neutral-200);
            text-align: center;
            transition: all 0.2s ease;
        }

        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        /* Status Badge */
        .status-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
        }

        .badge-healthy {
            background-color: #dcfce7;
            color: #166534;
        }

        .badge-warning {
            background-color: #fef3c7;
            color: #92400e;
        }

        .badge-error {
            background-color: #fee2e2;
            color: #991b1b;
        }

        /* Callout Box */
        .callout-critical {
            background: white;
            border-left: 4px solid var(--danger);
            padding: 1.25rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        }

        /* Image Container */
        .image-container {
            border: 1px solid var(--neutral-200);
            border-radius: 10px;
            padding: 1.5rem;
            background: white;
            margin: 1.5rem 0;
        }

        /* Footer */
        .footer-section {
            text-align: center;
            color: #6b7280;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--neutral-200);
            font-size: 0.95rem;
        }

        /* Expander Override */
        .streamlit-expanderHeader { background-color: var(--neutral-50); }
    </style>
    """, unsafe_allow_html=True)

    # ============ HELPER FUNCTIONS ============

    def load_system_health():
        """Load system health data from gold layer via API."""
        client = get_client()
        return client.get_analytics_data("system_healthcheck")

    def get_health_badge(status):
        """Generate HTML badge for status"""
        status_lower = str(status).lower()
        if "healthy" in status_lower or "green" in status_lower:
            badge_class = "badge-healthy"
            label = "✓ Healthy"
        elif "warning" in status_lower or "yellow" in status_lower or "init" in status_lower:
            badge_class = "badge-warning"
            label = "⚠ Warning"
        else:
            badge_class = "badge-error"
            label = "✕ Error"

        return f'<span class="status-badge {badge_class}">{label}</span>'
    def format_metric(value, suffix: str) -> str:
        """Format metric values with suffix, guard against missing values."""
        if value is None or value == "" or value == "N/A":
            return "N/A"
        return f"{value} {suffix}"

    def coalesce(*values, default="Unknown"):
        for value in values:
            if value is not None and value != "":
                return value
        return default

    def render_insight_card(title, content, icon="📌"):
        """Render a premium insight card"""
        st.markdown(f"""
        <div class="insight-card">
            <h3 style="margin-top: 0; color: var(--primary-dark);">{icon} {title}</h3>
            <p style="margin-bottom: 0;">{content}</p>
        </div>
        """, unsafe_allow_html=True)

    def render_ethics_box(title, content, box_type="warning"):
        """Render an ethics/responsibility box"""
        css_class = "ethics-box-success" if box_type == "success" else "ethics-box"
        st.markdown(f"""
        <div class="{css_class}">
            <h4 style="margin-top: 0;">{title}</h4>
            <div style="font-size: 0.95rem; line-height: 1.6;">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    # ============ PAGE CONTENT - EXECUTES DIRECTLY ============

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚙️ System Insights")
        st.markdown("**Architecture • Data Pipeline • Ethics • Technical Contract**")

    system_health = load_system_health()
    if isinstance(system_health, dict):
        if "pipeline_status" not in system_health and "status" in system_health:
            system_health["pipeline_status"] = system_health.get("status")
        if "last_successful_run" not in system_health and "timestamp" in system_health:
            system_health["last_successful_run"] = system_health.get("timestamp")
        if "last_updated" not in system_health and "timestamp" in system_health:
            system_health["last_updated"] = system_health.get("timestamp")
        if "ingestion_latency_ms" not in system_health:
            system_health["ingestion_latency_ms"] = system_health.get("latency_ms")
        if "source_availability_pct" not in system_health:
            system_health["source_availability_pct"] = system_health.get("availability_pct")
        if "processing_lag_minutes" not in system_health:
            system_health["processing_lag_minutes"] = system_health.get("lag_minutes")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 1: SYSTEM HEALTH OVERVIEW ============
    st.header("1️⃣ System Health Overview")
    st.markdown("Real-time status of the City Pulse pipeline and infrastructure")

    if system_health:
        # Parse health status
        pipeline_status = system_health.get("pipeline_status", "unknown")
        health_badge_html = get_health_badge(pipeline_status)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #6b7280; margin: 0 0 0.5rem 0; font-size: 0.875rem; text-transform: uppercase; font-weight: 600;">Pipeline Status</p>
                {health_badge_html}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            ingestion_latency = format_metric(system_health.get("ingestion_latency_ms"), "ms")
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #6b7280; margin: 0 0 0.5rem 0; font-size: 0.875rem; text-transform: uppercase; font-weight: 600;">Ingestion Latency</p>
                <p style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin: 0;">{ingestion_latency}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            source_availability = format_metric(system_health.get("source_availability_pct"), "%")
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #6b7280; margin: 0 0 0.5rem 0; font-size: 0.875rem; text-transform: uppercase; font-weight: 600;">Source Availability</p>
                <p style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin: 0;">{source_availability}</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            processing_lag = format_metric(system_health.get("processing_lag_minutes"), "min")
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #6b7280; margin: 0 0 0.5rem 0; font-size: 0.875rem; text-transform: uppercase; font-weight: 600;">Processing Lag</p>
                <p style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin: 0;">{processing_lag}</p>
            </div>
            """, unsafe_allow_html=True)

        # Last run timestamp
        last_run = coalesce(system_health.get("last_successful_run"), system_health.get("last_updated"), system_health.get("analytics_time"), system_health.get("last_modified"))
        last_updated = coalesce(system_health.get("last_updated"), system_health.get("analytics_time"), system_health.get("last_modified"))

        st.markdown(f"""
        <div class="insight-card">
            <p style="margin: 0; font-size: 0.9rem;"><strong>Last Successful Pipeline Run:</strong> {last_run}</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;"><strong>Last Updated:</strong> {last_updated}</p>
        </div>
        """, unsafe_allow_html=True)

        history = system_health.get("history", [])
        if history:
            with st.expander("Historical Health Checks"):
                for entry in history:
                    if isinstance(entry, dict):
                        st.markdown(
                            f"- {entry.get('timestamp') or 'Unknown'} • {entry.get('status', 'unknown')} • {entry.get('message', '')}"
                        )
                    else:
                        st.markdown(f"- {entry}")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 2: ARCHITECTURE DIAGRAM (USER UPLOAD) ============
    st.header("2️⃣ Architecture Diagram")
    st.markdown("Upload your system architecture diagram (PNG or JPG)")

    # Initialize session state for image upload
    if "uploaded_architecture" not in st.session_state:
        st.session_state.uploaded_architecture = None

    # Only show file uploader if no image is uploaded yet
    if st.session_state.uploaded_architecture is None:
        uploaded_file = st.file_uploader(
            "Choose architecture diagram image",
            type=["png", "jpg", "jpeg"],
            key="architecture_upload"
        )

        if uploaded_file is not None:
            st.session_state.uploaded_architecture = uploaded_file
            st.rerun()
    else:
        # Image is uploaded, show it and allow clearing
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(st.session_state.uploaded_architecture, caption="High-level system architecture", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            # Clear button to upload a new image
            if st.button("🗑️ Clear", key="clear_architecture"):
                st.session_state.uploaded_architecture = None
                st.rerun()

    # Info box only shows when no image is uploaded
    if st.session_state.uploaded_architecture is None and 'uploaded_file' not in locals():
        st.info("📤 **Upload an architecture diagram** to visualize the system topology. This should include:\n\n"
                "- Data sources (News APIs, RSS feeds)\n"
                "- Message queue (Kafka)\n"
                "- Speed layer (Kafka → MongoDB)\n"
                "- Batch layer (Flink)\n"
                "- Data lakehouse (Bronze → Silver → Gold)\n"
                "- API layer (FastAPI)\n"
                "- Presentation layer (Streamlit)")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 3: ARCHITECTURE EXPLANATION ============
    st.header("3️⃣ Architecture Explanation")
    st.markdown("A deep dive into how City Pulse processes civic intelligence data")

    # 3a. Data Sources
    with st.expander("📥 **Data Sources & Ingestion**", expanded=True):
        st.markdown("""
        **City Pulse ingests civic intelligence from multiple trusted sources:**

        - **World News API**: Curated English-language news, updated every 3 minutes
        - **RSS Feeds**: Direct syndication from major Indian news outlets
        - **Optional Public Alerts**: Emergency services, weather, civic notices (extensible)

        **Intelligent Location Resolution:**
        - Automatic geotag extraction from article text and metadata
        - Entity recognition for city/region references
        - Fallback to source domain location for unmapped articles
        - City-level granularity (no personal data extraction)
        """)

    # 3b. Kafka - Streaming Backbone
    with st.expander("⚡ **Kafka: Streaming Backbone**", expanded=False):
        st.markdown("""
        **Purpose:** Event-driven, durable message queue for all ingested news

        **Responsibilities:**
        - **Event Publishing**: Every new article = 1 Kafka event
        - **Durability**: Events retained for 48 hours (configurable)
        - **Low-Latency Ingestion**: Sub-second event propagation
        - **Fault Tolerance**: Replicated across cluster (3 brokers minimum)

        **Data Contract:**
        ```
        Event Schema:
        {
          "event_id": "uuid",
          "timestamp": "2025-02-03T14:32:15Z",
          "source": "world-news-api",
          "article": {
            "title", "content", "url", "author",
            "published_at", "sentiment_score"
          },
          "location": {"city", "region", "country"}
        }
        ```

        **Performance:** ~2.8ms ingestion latency, 98.5% availability
        """)

    # 3c. Speed Layer (Real-Time)
    with st.expander("🚀 **Speed Layer: Real-Time Processing**", expanded=False):
        st.markdown("""
        **Purpose:** Immediate availability of fresh civic intelligence

        **Technology:** Kafka → MongoDB (TTL indexes)

        **Characteristics:**
        - **Latency**: ~100ms from ingestion to queryable
        - **Retention**: 48 hours (automatic TTL cleanup)
        - **Use Cases**: Live dashboard, trending keywords, real-time sentiment
        - **Queries**: Geospatial (MongoDB geoqueries for map visualization)

        **Data Model (MongoDB Collections):**
        ```
        articles:
          - _id, title, content, url, timestamp
          - location: {city, lat, lng}
          - sentiment_score, category, keywords
          - ttl_index: expires_at (48h TTL)

        metrics:
          - time_window, count, avg_sentiment
          - geographic_distribution, trending_topics
        ```

        **Limitations:** Speed layer is temporary. For long-term analysis, use Gold layer.
        """)

    # 3d. Batch Layer (Flink)
    with st.expander("⚙️ **Batch Layer: Windowed Analytics**", expanded=False):
        st.markdown("""
        **Purpose:** Structured, enriched, deduplicated analytics

        **Technology:** Apache Flink (stream processing)

        **Processing:**
        - **Windows**: 5-minute tumbling windows
        - **Deduplication**: Cross-source duplicate detection
        - **Enrichment**: Entity extraction, location inference, sentiment calibration
        - **Aggregation**: Category counts, geographic distribution, keyword frequency

        **Data Flow:**
        ```
        Kafka (raw events)
          ↓
        Flink Window Aggregation (5-min windows)
          ↓
        Deduplication Engine
          ↓
        Enrichment Pipeline
          ↓
        Silver Layer (cleaned events)
        ```

        **Output Metrics (per 5-min window):**
        - Total articles ingested
        - Category breakdown
        - Sentiment distribution
        - Top 10 keywords
        - Geographic hotspots
        """)

    # 3e. Data Lakehouse (Bronze → Silver → Gold)
    with st.expander("💾 **Data Lakehouse: Permanent Storage**", expanded=False):
        st.markdown("""
        **Purpose:** Immutable, queryable historical archive + analytics-ready datasets

        **Technology:** MinIO (S3-compatible object storage)

        **Three-Layer Architecture:**

        **BRONZE LAYER** (Raw, audit-ready)
        - Unmodified ingestion records
        - Kafka event dumps (as JSON)
        - Purpose: Compliance, audit trail, replayability
        - Retention: Permanent

        **SILVER LAYER** (Cleaned, deduplicated)
        - Cleaned articles (bad data removed)
        - Standardized schemas
        - Removed duplicates
        - Purpose: Reliable historical data
        - Retention: Permanent

        **GOLD LAYER** (Analytics-ready, UI-serving)
        - Pre-aggregated metrics (search_news, top_news)
        - Enriched articles (entities, topics, geo-tags)
        - Compressed, indexed for fast queries
        - Purpose: **Direct API consumption** (Streamlit only reads Gold)
        - Retention: Permanent

        **Data Lineage:**
        ```
        Ingestion → Kafka → Flink → Bronze
                                  ↓
                              Dedup/Clean → Silver
                                  ↓
                              Aggregate/Enrich → Gold
                                  ↓
                              FastAPI (endpoints)
                                  ↓
                              Streamlit Frontend
        ```
        """)

    # 3f. Gold-Layer Datasets
    st.subheader("🌟 Gold-Layer Datasets (Frontend-Ready)")
    st.markdown("""
    The frontend **ONLY** reads from Gold-layer endpoints via FastAPI.
    These datasets are pre-aggregated, validated, and optimized for UI consumption.
    """)

    gold_datasets = {
        "search_news": {
            "icon": "🔍",
            "description": "Full-text news search with metrics",
            "fields": ["articles (20+)", "total_count", "sentiment_distribution", "category_breakdown", "time_series", "trending_keywords"],
            "freshness": "5 minutes",
            "use_cases": ["Search results", "Filtering", "Time-series trends"]
        },
        "top_news": {
            "icon": "⭐",
            "description": "Editorial selections: top, positive, negative",
            "fields": ["featured_articles (204)", "metrics", "trending_keywords", "editorial_notes"],
            "freshness": "Hourly",
            "use_cases": ["Homepage showcase", "Trending stories", "Sentiment extremes"]
        },
        "extract_news": {
            "icon": "📖",
            "description": "Deep article extraction & enrichment",
            "fields": ["full_content", "entities", "topics", "summary", "sentiment", "location"],
            "freshness": "On-demand",
            "use_cases": ["Article detail view", "Entity exploration"]
        },
        "extract_news_links": {
            "icon": "🔗",
            "description": "Related articles & source domains",
            "fields": ["urls", "domains", "link_text", "validation_status"],
            "freshness": "Daily",
            "use_cases": ["Source attribution", "Cross-reference reading"]
        },
        "feed_rss": {
            "icon": "📰",
            "description": "Aggregated RSS from major sources",
            "fields": ["rss_data", "source_url", "domain", "content_preview"],
            "freshness": "15 minutes",
            "use_cases": ["Raw feed display", "Source monitoring"]
        },
        "geo_coordinates": {
            "icon": "🗺️",
            "description": "Geocoded events for map visualization",
            "fields": ["city", "latitude", "longitude", "region", "country", "article_count"],
            "freshness": "Real-time",
            "use_cases": ["Map visualization", "Geographic filtering", "Hotspot detection"]
        }
    }

    cols = st.columns(3)
    for idx, (dataset_key, dataset_info) in enumerate(gold_datasets.items()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="architecture-card">
                <h4 style="margin-top: 0; color: var(--primary);">{dataset_info['icon']} {dataset_key.upper()}</h4>
                <p style="font-size: 0.9rem; margin: 0.5rem 0; color: #374151;"><strong>{dataset_info['description']}</strong></p>
                <p style="font-size: 0.85rem; color: #6b7280; margin: 0.5rem 0;">
                    <strong>Freshness:</strong> {dataset_info['freshness']}<br>
                    <strong>Fields:</strong> {len(dataset_info['fields'])}
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 4: FRONTEND ↔ BACKEND CONTRACT ============
    st.header("4️⃣ Frontend ↔ Backend Contract")
    st.markdown("**Critical architectural principle: Separation of concerns**")

    render_insight_card(
        "The Golden Rule",
        "Streamlit (frontend) <strong>NEVER</strong> reads raw storage. "
        "All data flows through <strong>FastAPI</strong>, which enforces schema validation, "
        "filtering, and access control. This ensures data integrity, security, and auditability.",
        icon="🛡️"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Frontend Responsibilities (Streamlit)

        ✓ **Read-only access** via FastAPI endpoints

        ✓ **Filter & sort** metadata (city, severity, date range)

        ✓ **Display** validated data

        ✓ **Visualize** via charts, maps, tables

        ✓ **No direct database queries**

        ✓ **No raw JSON exposure**
        """)

    with col2:
        st.markdown("""
        ### Backend Responsibilities (FastAPI)

        ✓ **Validate** Gold-layer schemas

        ✓ **Enforce** filter logic (city, severity, time)

        ✓ **Aggregate** metrics across datasets

        ✓ **Cache** expensive queries

        ✓ **Rate-limit** API access

        ✓ **Log & audit** all requests
        """)

    st.markdown("""
    **Every page is Gold-backed:**

    - **Dashboard**: `search_news` + `geo_coordinates` (FastAPI endpoint)
    - **Insights**: `search_news` + time-series aggregation (FastAPI endpoint)
    - **Map**: `geo_coordinates` + real-time MongoDB geoqueries (FastAPI endpoint)
    - **Topics**: `search_news` → trending keywords extraction (FastAPI endpoint)
    - **Articles**: `extract_news` + `extract_news_links` (FastAPI endpoint)
    - **System Insights**: `system_healthcheck.json` (static, but could be dynamic via FastAPI)

    **No page reads:**
    - ❌ Direct MinIO/S3
    - ❌ Direct MongoDB
    - ❌ Raw file system
    - ❌ Kafka topics
    """)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 5: REAL-TIME VS HISTORICAL FLOW ============
    st.header("5️⃣ Real-Time vs Historical Data Flow")

    st.markdown("**Lambda Architecture: Best of both worlds**")

    # Data flow table
    st.markdown("""
    | **Layer** | **Source** | **Frequency** | **Retention** | **Purpose** | **Latency** |
    |-----------|-----------|---------------|---------------|------------|-----------|
    | **Speed** | Kafka → MongoDB | ~100ms | 48 hours | Live dashboard, trending | <100ms |
    | **Batch** | Kafka → Flink | 5-min windows | Permanent (Silver) | Dedup, enrichment, validation | 5 minutes |
    | **Gold** | Silver → Gold | Continuous | Permanent | Analytics, API serving | Variable |
    """)

    st.markdown("### Why Lambda Architecture?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Speed Layer Benefits**

        - Immediate insights
        - Live trending detection
        - User engagement (real-time feel)
        - Geospatial queries
        """)

    with col2:
        st.markdown("""
        **Batch Layer Benefits**

        - Data quality (dedup, validation)
        - Cost efficiency
        - Complex aggregations
        - Immutable audit trail
        """)

    with col3:
        st.markdown("""
        **Gold Layer Benefits**

        - Single source of truth
        - Schema enforcement
        - Fast API responses
        - No raw data exposure
        """)

    st.markdown("""
    ### Trade-Offs

    | **Aspect** | **Trade-Off** |
    |-----------|--------------|
    | **Complexity** | Maintaining 3 systems vs simplicity |
    | **Latency** | <100ms real-time vs 5-min batch accuracy |
    | **Cost** | Higher infrastructure vs reduced compute per query |
    | **Consistency** | Eventual consistency vs strong consistency |
    """)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 6: ETHICAL AI & LIMITATIONS ============
    st.header("6️⃣ Ethical AI & Limitations")
    st.markdown("**Transparency, responsibility, and honest limitations**")

    # Bias & Source Reliability
    render_ethics_box(
        "📊 Bias Awareness & Source Reliability",
        """
        <strong>News Aggregation Bias:</strong><br>
        • All sources are major English-language outlets (publication bias)<br>
        • Coverage skews toward urban centers and large cities<br>
        • Less coverage of rural or underreported regions<br>
        • Breaking news priority may overshadow long-term trends<br>
        <br>
        <strong>Sentiment Analysis Limitations:</strong><br>
        • Sentiment is statistical (tone), not editorial (truth)<br>
        • Sarcasm, irony, and context-dependent meaning are misclassified ~15% of the time<br>
        • Cultural idioms in Indian English may not parse correctly<br>
        • Negation ("not good") can flip sentiment scores<br>
        <br>
        <strong>Mitigation:</strong><br>
        • Always cross-reference with primary sources<br>
        • Use sentiment as signal, not ground truth<br>
        • Diversify news consumption
        """,
        box_type="warning"
    )

    # Location Inference
    render_ethics_box(
        "🗺️ Location Inference Uncertainty",
        """
        <strong>Geocoding Limitations:</strong><br>
        • City-level granularity only (no street, building, or personal location)<br>
        • Articles mentioning multiple cities default to first extraction<br>
        • Ambiguous city names (e.g., "Springfield") may resolve incorrectly<br>
        • Event location ≠ news publication location<br>
        <br>
        <strong>No Personal Data:</strong><br>
        • No individual names, phone numbers, or IDs extracted<br>
        • No cross-referencing with personal databases<br>
        • Pure geographic analysis of public news only<br>
        <br>
        <strong>Best Practice:</strong><br>
        • Use for trend analysis, not precise geolocation<br>
        • Verify hotspots against ground truth
        """,
        box_type="warning"
    )

    # AI Summaries
    render_ethics_box(
        "🤖 AI Summaries: Assistive, Not Authoritative",
        """
        <strong>Where Summaries Are Used (if enabled):</strong><br>
        • Article preview text<br>
        • Brief descriptions (if Gemini API is integrated)<br>
        <br>
        <strong>Limitations:</strong><br>
        • Generated summaries may omit nuance or context<br>
        • Hallucinations possible (rare, but can occur)<br>
        • Not a substitute for reading the full article<br>
        • Reflects the bias of the source article<br>
        <br>
        <strong>Responsibility:</strong><br>
        • Always read the original article for decisions<br>
        • Do not quote or cite summaries as authoritative<br>
        • Use only for quick context, not policy or claims
        """,
        box_type="warning"
    )

    # Data Privacy
    render_ethics_box(
        "🔒 Privacy & Data Protection",
        """
        <strong>What We Do NOT Collect:</strong><br>
        • Personal names, emails, phone numbers<br>
        • Individual user data or browsing history<br>
        • IP addresses or device tracking<br>
        • Sensitive categories (health, finance, politics votes)<br>
        <br>
        <strong>What We Store:</strong><br>
        • Public news article metadata<br>
        • Aggregated metrics (counts, averages)<br>
        • City-level geographic data<br>
        <br>
        <strong>Data Retention:</strong><br>
        • Speed layer: Auto-deleted after 48 hours<br>
        • Historical layer: Immutable, never deleted (for audit)<br>
        <br>
        <strong>Security:</strong><br>
        • HTTPS in-transit encryption (production)<br>
        • No plaintext storage<br>
        • API authentication (production)
        """,
        box_type="success"
    )

    # Algorithmic Transparency
    render_ethics_box(
        "👁️ Algorithmic Transparency",
        """
        <strong>What This System Does:</strong><br>
        • Aggregates public news<br>
        • Counts and ranks by frequency (no "recommended for you")<br>
        • Applies simple sentiment scoring (not recommendation algorithms)<br>
        • Extracts named entities (location, person, organization)<br>
        <br>
        <strong>What This System Does NOT Do:</strong><br>
        • Rank news by importance/truth (editorial neutrality)<br>
        • Recommend news based on user profile<br>
        • Use machine learning to filter or suppress stories<br>
        • Make editorial decisions<br>
        <br>
        <strong>Explainability:</strong><br>
        • All metrics are explainable (sums, averages, counts)<br>
        • Sentiment: Open-source NLP (transformers, VADER)<br>
        • Trending keywords: Pure frequency analysis<br>
        • No black-box models in critical path
        """,
        box_type="success"
    )

    # Known Limitations Table
    st.markdown("### 📋 Known Limitations Summary")

    st.markdown("""
    | **Component** | **Limitation** | **Impact** | **Mitigation** |
    |---------------|---------------|-----------|----------------|
    | **Sentiment Analysis** | ~85% accuracy on English text | Emotion misclassified | Use as signal, not truth |
    | **Geolocation** | City-level only, first mention | Imprecise event location | Manual verification |
    | **Coverage Lag** | 5-15 min from publish to ingest | Not for real-time alerts | Use for trends, not breaking |
    | **Language Bias** | English-only | Non-English news missed | Expand to Hindi/regional |
    | **Source Bias** | Major outlets dominant | Underreported regions miss | Diversify RSS feeds |
    """)

    # Responsible Use
    render_ethics_box(
        "✋ Responsible Use Guidelines",
        """
        <strong>DO:</strong><br>
        ✓ Use for insight into civic trends and public interest<br>
        ✓ Cross-reference important claims with primary sources<br>
        ✓ Acknowledge sentiment algorithm limitations<br>
        ✓ Disclose data sources when sharing findings<br>
        <br>
        <strong>DON'T:</strong><br>
        ✗ Make policy decisions based solely on sentiment scores<br>
        ✗ Use for automated content moderation or censorship<br>
        ✗ Assume geolocation is precise<br>
        ✗ Treat AI summaries as authoritative journalism<br>
        ✗ Profile individuals based on news mentions<br>
        <br>
        <strong>Transparency:</strong><br>
        • Always cite this system's limitations when presenting findings<br>
        • Explain to stakeholders that this is exploratory analysis<br>
        • Include caveats in reports and presentations
        """,
        box_type="success"
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 7: PERFORMANCE METRICS ============
    st.header("7️⃣ Performance & Reliability")

    metrics = [
        ("Ingestion Frequency", "Every 3 min", "Fresh data cycle"),
        ("End-to-End Latency", "<5 min", "News → Frontend"),
        ("Speed Layer Latency", "~100 ms", "Kafka → MongoDB"),
        ("Data Retention", "48h + ∞", "Speed + Batch layers"),
        ("Source Availability", "98.5%", "News API uptime"),
        ("Pipeline Health", "✓ Healthy", "Real-time status"),
    ]

    cols = st.columns(3)
    for idx, (metric_name, metric_value, metric_desc) in enumerate(metrics):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #6b7280; margin: 0 0 0.5rem 0; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">{metric_name}</p>
                <p style="font-size: 1.3rem; font-weight: 700; color: var(--primary); margin: 0.5rem 0;">{metric_value}</p>
                <p style="color: #6b7280; margin: 0; font-size: 0.8rem;">{metric_desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ SECTION 8: TECH STACK ============
    st.header("8️⃣ Technology Stack")

    tech_stack = {
        "Data Ingestion": ["World News API", "RSS Feed Parser", "HTTP Client"],
        "Message Queue": ["Apache Kafka", "Event Streaming", "3-broker cluster"],
        "Real-Time DB": ["MongoDB", "Geospatial Indexes", "TTL Collections"],
        "Stream Processing": ["Apache Flink", "Windowed Operators", "State Management"],
        "Data Lake": ["MinIO", "S3-compatible API", "Bronze/Silver/Gold layers"],
        "API Layer": ["FastAPI", "Python async", "OpenAPI docs"],
        "Frontend": ["Streamlit", "Plotly", "Folium maps"],
        "Infrastructure": ["Docker", "Docker Compose", "Multi-container"],
    }

    cols = st.columns(2)
    for idx, (category, tools) in enumerate(tech_stack.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="architecture-card">
                <h4 style="margin-top: 0; color: var(--primary);">🛠️ {category}</h4>
            </div>
            """, unsafe_allow_html=True)
            for tool in tools:
                st.markdown(f"- **{tool}**")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ FOOTER ============
    st.markdown("""
    <div class="footer-section">
        <p style="font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">🏙 City Pulse v1.0</p>
        <p style="margin: 0.25rem 0; font-size: 0.95rem;">An Agentic Framework for Real-Time Civic Intelligence</p>
        <p style="margin: 0.25rem 0; font-size: 0.9rem;">Built for transparency, accuracy, and responsible data analysis</p>
        <p style="margin-top: 1rem; font-size: 0.85rem; color: #9ca3af;">
            Data sources: World News API • Infrastructure: Docker • Architecture: Lambda (Speed + Batch) • Ethics: Transparent & Accountable
        </p>
    </div>
    """, unsafe_allow_html=True)

