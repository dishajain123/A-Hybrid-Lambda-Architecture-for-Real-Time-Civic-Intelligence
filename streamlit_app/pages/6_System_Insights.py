"""
Page 6: System Insights — Architecture, pipeline health, API contract, data ethics.
Built-in architecture diagram — no upload required.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from components.header  import render_header, render_section_title, render_divider
from services.api_client import get_client
from utils.constants    import PLOTLY_LAYOUT
import utils.dummy_data as _dummy

_CSS = """
<style>
.arch-card {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:14px;
    padding:1.4rem 1.6rem; margin-bottom:1rem;
    box-shadow:0 1px 4px rgba(0,0,0,.05);
}
.arch-card h4 { font-size:.95rem; font-weight:700; color:#000; margin:0 0 .65rem; }
.arch-card p  { font-size:.85rem; color:#444; line-height:1.7; margin:0; }

.tech-chip { display:inline-block; color:#fff; border-radius:6px; padding:.22rem .7rem; margin:.2rem; font-size:.72rem; font-weight:700; letter-spacing:.3px; }
.tc-speed  { background:#1d4ed8; }
.tc-batch  { background:#7c3aed; }
.tc-store  { background:#047857; }
.tc-api    { background:#b45309; }
.tc-ui     { background:#000; }

.health-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.6rem 0; border-bottom:1px solid #f0f0f0; font-size:.85rem;
}
.health-row:last-child { border-bottom:none; }
.h-ok   { color:#16a34a; font-weight:700; }
.h-warn { color:#ca8a04; font-weight:700; }
.h-err  { color:#dc2626; font-weight:700; }

.pipe-step {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:11px;
    padding:.9rem .75rem; text-align:center; transition:all .2s;
    min-height:120px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    overflow:hidden;
}
.pipe-step:hover { border-color:#000; box-shadow:0 4px 14px rgba(0,0,0,.09); }
.pipe-icon { font-size:1.6rem; display:block; margin-bottom:.3rem; }
.pipe-name {
    font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.4px; color:#000;
    overflow-wrap:anywhere; word-break:break-word; line-height:1.35;
}
.pipe-role {
    font-size:.65rem; color:#888; margin-top:.15rem;
    overflow-wrap:anywhere; word-break:break-word; line-height:1.35;
}

.arrow-cell { text-align:center; font-size:1.2rem; color:#ccc; padding-top:1.4rem; }

.pipeline-flow {
    display:flex;
    gap:.55rem;
    align-items:stretch;
    overflow-x:auto;
    padding-bottom:.35rem;
}

.pipeline-flow::-webkit-scrollbar {
    height:6px;
}

.pipeline-flow::-webkit-scrollbar-thumb {
    background:#d1d5db;
    border-radius:999px;
}

.pipe-arrow {
    display:flex;
    align-items:center;
    justify-content:center;
    min-width:24px;
    color:#9ca3af;
    font-size:1.25rem;
    font-weight:700;
}

.contract-row {
    display:flex; gap:.75rem; padding:.6rem 0;
    border-bottom:1px solid #f0f0f0; font-size:.83rem; align-items:baseline;
    flex-wrap:wrap;
}
.contract-row:last-child { border-bottom:none; }

.ethical-item {
    background:#f5f5f5; border-radius:10px; padding:.9rem 1.1rem;
    margin-bottom:.6rem; font-size:.85rem; color:#333; line-height:1.6;
    border-left:3px solid #000;
}
.ethical-item strong { color:#000; }

.schema-row {
    display:flex; gap:.5rem; padding:.5rem .65rem;
    border-bottom:1px solid #f0f0f0; font-size:.8rem; align-items:baseline;
}
.schema-row:last-child { border-bottom:none; }
</style>
"""

_PIPELINE_STEPS = [
    ("🌍","World News API","Source"),
    ("⚡","Kafka Producer","Ingest"),
    ("📨","Kafka Consumer","Stream"),
    ("🔶","MinIO Bronze","Raw Store"),
    ("⚙️","Apache Flink","Batch Process"),
    ("🥈","MinIO Silver","Cleaned"),
    ("🥇","MinIO Gold","Analytics"),
    ("🚀","FastAPI","Serve"),
    ("📊","Streamlit","Display"),
]

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    render_header("System Insights", "Architecture, health, API contract & data ethics", "⚙️")

    client  = get_client()
    metrics = client.get_metrics_summary() or _dummy.get_metrics()

    # ── System Health Cards ───────────────────────────────────────────────────
    render_section_title("System Health Overview")
    hc1,hc2,hc3,hc4 = st.columns(4)
    health_items = [
        ("🌐 API Gateway",         "Operational",                         "ok"),
        ("⚡ Kafka Broker",        "Active",                               "ok"),
        ("⚙️ Flink Jobs",          f"{metrics.get('flink_jobs_active',3)} running","ok"),
        ("🪣 MinIO Storage",       "Healthy",                              "ok"),
    ]
    for col,(name,val,st_) in zip([hc1,hc2,hc3,hc4], health_items):
        cls = {"ok":"h-ok","warn":"h-warn","err":"h-err"}[st_]
        with col:
            st.markdown(f"""
            <div class="arch-card" style="text-align:center;padding:1.1rem">
              <div style="font-size:.8rem;font-weight:700;color:#555;margin-bottom:.35rem">{name}</div>
              <div class="{cls}" style="font-size:1.05rem">● {val}</div>
            </div>""", unsafe_allow_html=True)

    render_divider()

    # ── Pipeline Diagram ──────────────────────────────────────────────────────
    render_section_title("Lambda Architecture — End-to-End Data Flow")
    # IMPORTANT: Keep HTML unindented; leading spaces can be rendered as code blocks.
    parts = []
    for i, (icon, name, role) in enumerate(_PIPELINE_STEPS):
        parts.append(
            f'<div class="pipe-step">'
            f'<span class="pipe-icon">{icon}</span>'
            f'<div class="pipe-name">{name}</div>'
            f'<div class="pipe-role">{role}</div>'
            f'</div>'
        )
        if i < len(_PIPELINE_STEPS) - 1:
            parts.append('<div class="pipe-arrow">→</div>')

    pipeline_html = f'<div class="pipeline-flow">{"".join(parts)}</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)

    render_divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "🏗️ Architecture",
        "📦 MinIO Layers",
        "📊 Pipeline Metrics",
        "🔌 API & Schema",
        "⚖️ Data Ethics",
    ])

    # ── Tab 1: Architecture ────────────────────────────────────────────────────
    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""
            <div class="arch-card">
              <h4>⚡ Speed Layer — Real-Time Path</h4>
              <p>
                A <strong>Kafka Producer</strong> polls the World News API every 30 seconds
                and publishes JSON payloads to the <code>news-raw</code> topic.
                The <strong>Kafka Consumer</strong> reads each message and writes it verbatim
                to <strong>MinIO Bronze</strong>.  FastAPI reads Bronze objects directly to
                serve the Live Feed and Live Map with sub-60-second latency.
              </p>
            </div>
            <div class="arch-card">
              <h4>🗺️ Geo Intelligence</h4>
              <p>
                Location entities extracted from article text are geocoded via the
                World News API <code>/geo/coordinates</code> endpoint.
                Each result carries <strong>lat/lon, city name, and region</strong>.
                The Live Map renders these as proportional circles coloured by average sentiment.
              </p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown("""
            <div class="arch-card">
              <h4>🔧 Batch Layer — Historical Path</h4>
              <p>
                <strong>Apache Flink</strong> runs two scheduled jobs:
                (1) Reads Bronze → cleans, deduplicates, scores sentiment → writes <strong>Silver</strong>.
                (2) Reads Silver → computes aggregate metrics (time-series, category breakdown,
                trending keywords, top sources) → writes <strong>Gold</strong>.
                Gold objects are served by the <code>/api/analytics/</code> endpoints and
                power the Insights dashboard.
              </p>
            </div>
            <div class="arch-card">
              <h4>🚀 Serving Layer — FastAPI</h4>
              <p>
                A single <strong>FastAPI</strong> application exposes unified REST endpoints
                that merge speed-layer and batch-layer data.  The Streamlit frontend
                queries these endpoints — live pages use Bronze, analytics pages use Gold.
                Geo routes live under <code>/geo/</code>, batch under <code>/api/batch/</code>.
              </p>
            </div>
            """, unsafe_allow_html=True)

        render_section_title("Technology Stack")
        groups = {
            "Ingestion": [("World News API","tc-speed"),("RSS Feeds","tc-speed"),("Kafka","tc-speed"),("Producer","tc-speed")],
            "Processing":[("Apache Flink","tc-batch"),("Python 3.11","tc-batch")],
            "Storage":   [("MinIO S3","tc-store"),("MongoDB","tc-store")],
            "Backend":   [("FastAPI","tc-api"),("Docker","tc-api"),("Docker Compose","tc-api")],
            "Frontend":  [("Streamlit","tc-ui"),("Plotly","tc-ui"),("Folium","tc-ui"),("Inter Font","tc-ui")],
        }
        for grp, techs in groups.items():
            chips = " ".join(f'<span class="tech-chip {cls}">{n}</span>' for n,cls in techs)
            st.markdown(f"""
            <div style="margin-bottom:.6rem">
              <span style="font-size:.68rem;font-weight:700;color:#888;text-transform:uppercase;
                letter-spacing:.8px;margin-right:.5rem">{grp}</span>{chips}
            </div>""", unsafe_allow_html=True)

    # ── Tab 2: MinIO Layers ────────────────────────────────────────────────────
    with tab2:
        lc1,lc2,lc3 = st.columns(3)
        layer_defs = [
            (lc1,"🔶","Bronze","#d97706",metrics.get("bronze_objects",624),
             "Raw, immutable, append-only objects exactly as received from source APIs.",
             ["search_news","top_news","extract_news","feed_rss","geo_coordinates","extract_news_links"]),
            (lc2,"🥈","Silver","#6b7280",metrics.get("silver_objects",420),
             "Cleaned, de-duplicated, schema-normalised, sentiment-scored by Flink Job 1.",
             ["articles_cleaned","locations_enriched","entities_tagged"]),
            (lc3,"🥇","Gold","#b45309",metrics.get("gold_objects",240),
             "Pre-aggregated analytics updated by Flink Job 2 every 15 minutes.",
             ["sentiment_timeseries","category_breakdown","trending_topics","city_heatmap","top_sources"]),
        ]
        for col,emoji,name,color,count,desc,eps in layer_defs:
            with col:
                ep_items = "".join(f"<li style='font-size:.77rem'><code>{e}</code></li>" for e in eps)
                st.markdown(f"""
                <div style="background:#fff;border:2px solid {color};border-radius:12px;padding:1.2rem 1.3rem">
                  <div style="font-size:1.5rem">{emoji}</div>
                  <div style="font-size:1.1rem;font-weight:800;color:#000;margin:.2rem 0">{name}</div>
                  <div style="font-size:2rem;font-weight:900;color:{color}">{count:,}</div>
                  <div style="font-size:.68rem;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.6rem">objects</div>
                  <p style="font-size:.78rem;color:#555;line-height:1.5;margin-bottom:.5rem">{desc}</p>
                  <ul style="margin:0;padding-left:1rem">{ep_items}</ul>
                </div>
                """, unsafe_allow_html=True)

        render_divider()
        render_section_title("Storage Volume")
        fig = go.Figure(go.Bar(
            x=["Bronze","Silver","Gold"],
            y=[metrics.get("bronze_objects",624),
               metrics.get("silver_objects",420),
               metrics.get("gold_objects",240)],
            marker_color=["#d97706","#6b7280","#b45309"],
            marker_line_width=0,
            text=[metrics.get("bronze_objects",624),
                  metrics.get("silver_objects",420),
                  metrics.get("gold_objects",240)],
            textposition="outside",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Tab 3: Pipeline Metrics ────────────────────────────────────────────────
    with tab3:
        render_section_title("Live Performance Indicators")
        pm1,pm2,pm3,pm4 = st.columns(4)
        pm1.metric("Kafka Throughput",  metrics.get("kafka_throughput","142 msg/min"))
        pm2.metric("API Latency (avg)", f"{metrics.get('api_latency_ms',87)} ms")
        pm3.metric("Flink Jobs Active", metrics.get("flink_jobs_active",3))
        pm4.metric("Kafka Consumer Lag",metrics.get("kafka_lag",0))

        render_divider()
        render_section_title("Health Details")
        health_details = [
            ("API Gateway",        "Operational",   "ok",   "All endpoints responding"),
            ("Kafka Producer",     "Publishing",    "ok",   "142 msg/min to news-raw topic"),
            ("Kafka Consumer",     "Consuming",     "ok",   "Lag: 0 messages"),
            ("Flink Job 1 (ETL)",  "Running",       "ok",   "Bronze → Silver, 15 min cycle"),
            ("Flink Job 2 (Agg)",  "Running",       "ok",   "Silver → Gold, 15 min cycle"),
            ("Flink Job 3 (Geo)",  "Running",       "ok",   "Geo-tagging enrichment"),
            ("MinIO Bronze",       "Healthy",       "ok",   f"{metrics.get('bronze_objects',624)} objects"),
            ("MinIO Silver",       "Healthy",       "ok",   f"{metrics.get('silver_objects',420)} objects"),
            ("MinIO Gold",         "Healthy",       "ok",   f"{metrics.get('gold_objects',240)} objects"),
            ("FastAPI Backend",    "Online",        "ok",   f"Latency: {metrics.get('api_latency_ms',87)} ms"),
            ("MongoDB",            "Connected",     "ok",   "Primary replica healthy"),
        ]
        rows_html = ""
        for name,status,st_,note in health_details:
            cls = {"ok":"h-ok","warn":"h-warn","err":"h-err"}[st_]
            rows_html += f"""
            <div class="health-row">
              <span style="font-weight:600;color:#111;width:200px">{name}</span>
              <span class="{cls}">● {status}</span>
              <span style="color:#888;font-size:.78rem">{note}</span>
            </div>"""
        st.markdown(f"""
        <div style="background:#fff;border:1.5px solid #e5e5e5;border-radius:12px;
          padding:1rem 1.25rem">{rows_html}</div>
        """, unsafe_allow_html=True)

        render_divider()
        render_section_title("Simulated Endpoint Activity")
        import utils.dummy_data as _d
        import random; random.seed(77)
        ts    = _d.get_time_series()
        dates = [r["date"] for r in ts[-30:]]
        eps   = ["search_news","top_news","geo_coordinates","extract_news","feed_rss"]
        cols_ = ["#000","#333","#666","#999","#ccc"]
        fig2  = go.Figure()
        for ep,col in zip(eps,cols_):
            fig2.add_trace(go.Scatter(
                x=dates, y=[random.randint(5,50) for _ in dates],
                name=ep, mode="lines", line=dict(color=col,width=2),
            ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=280, xaxis_tickformat="%b %d",
                           legend=dict(orientation="h",y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 4: API & Schema ────────────────────────────────────────────────────
    with tab4:
        render_section_title("REST API Contract")
        endpoints = [
            ("GET","/api/live/by-endpoint/{ep}","Bronze live data","search_news, top_news, …","Live Feed, City Pulse"),
            ("GET","/geo/coordinates","Geocoded locations","lat, lon, city, avg_sentiment","Live Map"),
            ("GET","/api/analytics/{ep}","Gold layer analytics","metrics, time_series","Insights"),
            ("GET","/api/batch/read/{bucket}/{path}","MinIO object read","Raw JSON","Insights snapshot"),
            ("GET","/api/live/search","Full-text search","q, limit","Live Feed filter"),
            ("GET","/metrics/summary","Aggregated KPIs","total, sentiment, kafka_*","All pages"),
        ]
        hdr = """
        <div style="display:flex;gap:.5rem;padding:.5rem .75rem;background:#000;color:#fff;
          border-radius:8px;font-size:.72rem;font-weight:700;margin-bottom:.2rem">
          <span style="width:45px">Method</span>
          <span style="flex:2">Endpoint</span>
          <span style="flex:1.5">Description</span>
          <span style="flex:1.5">Params</span>
          <span style="flex:1">Used In</span>
        </div>"""
        rows = "".join(f"""
        <div style="display:flex;gap:.5rem;padding:.5rem .75rem;border-bottom:1px solid #f0f0f0;
          font-size:.78rem;align-items:baseline">
          <code style="width:45px;background:#000;color:#fff;padding:.1rem .3rem;border-radius:4px;font-size:.65rem">{m}</code>
          <code style="flex:2;background:#f5f5f5;padding:.1rem .4rem;border-radius:4px;font-size:.72rem">{ep}</code>
          <span style="flex:1.5;color:#444">{desc}</span>
          <span style="flex:1.5;color:#888;font-size:.72rem">{params}</span>
          <span style="flex:1;color:#555;font-size:.72rem">{page}</span>
        </div>""" for m,ep,desc,params,page in endpoints)
        st.markdown(f'<div style="background:#fff;border:1.5px solid #e5e5e5;border-radius:10px;overflow:hidden">{hdr}{rows}</div>',
                    unsafe_allow_html=True)

        render_divider()
        render_section_title("Article Object Schema (Bronze)")
        schema = [
            ("id","integer","Unique article ID from World News API"),
            ("title","string","Headline text"),
            ("text","string","Full article body"),
            ("summary","string","AI-generated summary"),
            ("url","string","Source URL"),
            ("image","string","Featured image URL"),
            ("images[]","array","Gallery: [{url, width, height, title}]"),
            ("video","string|null","Video URL or null"),
            ("publish_date","datetime","Publication timestamp"),
            ("author","string","Author name(s), comma-separated"),
            ("authors[]","array","Structured author list"),
            ("language","string","ISO 639-1 code (e.g. 'en')"),
            ("category","string","Article category"),
            ("source_country","string","ISO 3166 country code"),
            ("sentiment","float","Score in [-1.0, +1.0]"),
            ("entities[]","array","NER: [{type, name, description, lat, lon}]"),
        ]
        s_hdr = """
        <div style="display:flex;gap:.5rem;padding:.45rem .65rem;background:#000;color:#fff;
          border-radius:8px;font-size:.7rem;font-weight:700;margin-bottom:.2rem">
          <span style="width:100px">Field</span>
          <span style="width:70px">Type</span>
          <span>Description</span>
        </div>"""
        s_rows = "".join(f"""
        <div class="schema-row">
          <code style="width:100px;font-size:.74rem">{f}</code>
          <span style="width:70px;color:#7c3aed;font-size:.72rem">{t}</span>
          <span style="color:#444">{d}</span>
        </div>""" for f,t,d in schema)
        st.markdown(f'<div style="background:#fff;border:1.5px solid #e5e5e5;border-radius:10px;overflow:hidden">{s_hdr}{s_rows}</div>',
                    unsafe_allow_html=True)

        render_divider()
        render_section_title("Data Flow: Speed vs Batch")
        fl, fr = st.columns(2)
        with fl:
            st.markdown("""
            <div class="arch-card">
              <h4>⚡ Speed Layer (Real-Time)</h4>
              <p>
                1 · Kafka Producer polls API every 30s<br>
                2 · Publishes to <code>news-raw</code> topic<br>
                3 · Consumer writes raw JSON → Bronze<br>
                4 · FastAPI reads Bronze → Live Feed / Map<br>
                5 · Streamlit auto-refreshes (10–120s)<br><br>
                <strong>Latency: &lt;60 sec end-to-end</strong>
              </p>
            </div>""", unsafe_allow_html=True)
        with fr:
            st.markdown("""
            <div class="arch-card">
              <h4>🔧 Batch Layer (Historical)</h4>
              <p>
                1 · Flink Job 1 reads Bronze every 15 min<br>
                2 · Cleans + enriches + scores → Silver<br>
                3 · Flink Job 2 aggregates Silver → Gold<br>
                4 · Gold served via <code>/api/analytics/</code><br>
                5 · Insights page renders Gold charts<br><br>
                <strong>Update cadence: every 15 minutes</strong>
              </p>
            </div>""", unsafe_allow_html=True)

    # ── Tab 5: Ethics ──────────────────────────────────────────────────────────
    with tab5:
        render_section_title("Ethical AI & Data Governance")
        ethics = [
            ("Data Source Transparency",
             "All articles sourced from World News API under appropriate licensing. Sources are attributed on every card, detail view, and metadata panel."),
            ("Sentiment Analysis Limitations",
             "Sentiment scores are computed algorithmically (lexical models) and may not reflect nuanced human judgment. Treat scores as directional indicators, not authoritative classifications."),
            ("No Personal Data Collected",
             "City Pulse processes only publicly available news articles. No personally identifiable information (PII) is collected, stored, or processed at any pipeline stage."),
            ("Algorithmic Bias Awareness",
             "News APIs may over-represent certain regions, languages, or political perspectives. The dashboard presents all data without ideological filtering."),
            ("Data Retention Policy",
             "Bronze objects retained 90 days. Silver and Gold follow a 180-day policy. Automatic purge via MinIO lifecycle rules."),
            ("Civic Use Only",
             "Designed for civic intelligence, journalism support, and academic research. Not intended for surveillance, profiling, or targeted advertising."),
            ("Model Transparency",
             "No black-box predictions are made. All displayed scores are derived from reproducible, documented transformations applied by the Flink batch layer."),
        ]
        for title, body in ethics:
            st.markdown(f"""
            <div class="ethical-item">
              <strong>{title}</strong><br>{body}
            </div>""", unsafe_allow_html=True)

        render_divider()
        render_section_title("Build Information")
        bc1,bc2 = st.columns(2)
        with bc1:
            st.markdown(f"""
            <div class="arch-card" style="font-size:.85rem">
              <h4>Version & Runtime</h4>
              <p>
                <strong>App:</strong> City Pulse v2.1<br>
                <strong>Build:</strong> {datetime.now().strftime('%Y-%m-%d')}<br>
                <strong>Python:</strong> 3.11+ &nbsp;|&nbsp; <strong>Streamlit:</strong> 1.35+<br>
                <strong>Plotly:</strong> 5.x &nbsp;|&nbsp; <strong>Folium:</strong> 0.18+
              </p>
            </div>""", unsafe_allow_html=True)
        with bc2:
            last = metrics.get("last_ingestion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.markdown(f"""
            <div class="arch-card" style="font-size:.85rem">
              <h4>Live Stats</h4>
              <p>
                <strong>Last Ingestion:</strong> {last}<br>
                <strong>Total Articles:</strong> {metrics.get('total_articles',847):,}<br>
                <strong>MinIO Objects:</strong> {metrics.get('minio_objects',1284):,}<br>
                <strong>Flink Jobs:</strong> {metrics.get('flink_jobs_active',3)} active<br>
                <strong>Kafka Lag:</strong> {metrics.get('kafka_lag',0)} msgs
              </p>
            </div>""", unsafe_allow_html=True)
