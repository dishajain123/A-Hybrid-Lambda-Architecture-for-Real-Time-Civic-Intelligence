import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from components.header      import render_header, render_section_title, render_divider
from components.event_card  import render_event_card, inject_card_css
from components.ai_panel    import render_ai_panel
from components.severity_badge import inject_badge_css
from components.filters     import render_filters, apply_filters
from services.api_client    import get_client
from utils.constants        import PLOTLY_LAYOUT
import utils.dummy_data     as _dummy

_CSS = """
<style>
.stat-card {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:14px;
    padding:1.1rem 1.2rem; text-align:center;
    box-shadow:4px 4px 0 #000; transition:all .2s ease; cursor:default;
    min-height:230px;
    height:230px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
}
.stat-card:hover { transform:translate(-2px,-2px); box-shadow:6px 6px 0 #000; }
.stat-val  { font-size:2.2rem; font-weight:900; color:#000; line-height:1; margin-bottom:.25rem; }
.stat-lbl  {
    font-size:.7rem; font-weight:700; color:#888; text-transform:uppercase;
    letter-spacing:.8px; min-height:2.3em; display:flex; align-items:center; text-align:center;
}
.stat-sub  { font-size:.75rem; color:#555; margin-top:.3rem; min-height:2.4em; display:flex; align-items:center; text-align:center; }

.trending-chip {
    display:inline-block; background:#000; color:#fff;
    border-radius:6px; padding:.22rem .65rem; margin:.2rem;
    font-size:.72rem; font-weight:700; letter-spacing:.4px; text-transform:uppercase;
}
.source-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.5rem 0; border-bottom:1px solid #f0f0f0; font-size:.84rem;
}
.source-row:last-child { border-bottom:none; }
.source-name  { font-weight:600; color:#111; }
.source-count { font-weight:800; color:#000; }

.data-bar {
    background:#f0f0f0; border-radius:20px; height:6px; margin-top:.3rem;
}
.data-bar-fill { background:#000; border-radius:20px; height:6px; }

.nav-hint {
    background:#f5f5f5; border:1.5px dashed #ccc; border-radius:10px;
    padding:.75rem 1rem; font-size:.82rem; color:#666; margin-bottom:1rem;
}
</style>
"""

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    inject_card_css()
    inject_badge_css()
    render_header("City Pulse", "Real-time civic intelligence overview", "🌐")

    client   = get_client()
    articles = client.get_endpoint_articles("search_news", limit=80)
    if not articles:
        articles = _dummy.get_articles(limit=80)
    metrics  = client.get_metrics_summary() or _dummy.get_metrics()
    geo_data = client.get_geo_coordinates()  or _dummy.get_geo_data()
    cats     = _dummy.get_category_breakdown()
    ts       = _dummy.get_time_series()

    # ── KPI Row ──────────────────────────────────────────────────────────────
    total    = metrics.get("total_articles", len(articles))
    avg_s    = metrics.get("avg_sentiment",
               round(sum(a.get("sentiment",0) for a in articles)/max(len(articles),1), 3))
    pos_pct  = metrics.get("positive_pct",
               round(sum(1 for a in articles if a.get("sentiment",0)>0.2)/max(len(articles),1)*100,1))
    neg_pct  = metrics.get("negative_pct",
               round(sum(1 for a in articles if a.get("sentiment",0)<-0.2)/max(len(articles),1)*100,1))
    today_ct = metrics.get("articles_today", min(len(articles), 43))
    locs_ct  = len(geo_data)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, val, lbl, sub in [
        (c1, f"{total:,}",                 "Total Articles",  f"↑ {today_ct} today"),
        (c2, f"{avg_s:+.3f}",              "Avg Sentiment",   "All sources"),
        (c3, f"{pos_pct:.1f}%",            "Positive",        "Favourable"),
        (c4, f"{neg_pct:.1f}%",            "Negative",        "Critical"),
        (c5, f"{locs_ct}",                 "Active Cities",   "Geo-tagged"),
        (c6, f"{metrics.get('minio_objects',1284):,}", "MinIO Objects","Bronze→Gold"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div class="stat-val">{val}</div>
              <div class="stat-lbl">{lbl}</div>
              <div class="stat-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── API Coverage info ─────────────────────────────────────────────────────
    pagination = _dummy.get_search_pagination()
    st.markdown(f"""
    <div style="background:#f9f9f9;border:1px solid #e5e5e5;border-radius:10px;
      padding:.65rem 1.1rem;font-size:.8rem;color:#555;margin-bottom:1.25rem;
      display:flex;gap:1.5rem;flex-wrap:wrap">
      <span>📡 <strong>{len(articles)}</strong> articles loaded</span>
      <span>🌐 <strong>{pagination['available']:,}</strong> available in API</span>
      <span>🕐 Updated: <strong>{datetime.now().strftime('%H:%M:%S')}</strong></span>
      <span>🔶 Layer: <strong>Bronze (Speed)</strong></span>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        render_section_title("Sentiment Distribution — Last 60 Days")
        dates = [r["date"]     for r in ts]
        pos   = [r["positive"] for r in ts]
        neg   = [r["negative"] for r in ts]
        neu   = [r["neutral"]  for r in ts]
        fig   = go.Figure()
        fig.add_trace(go.Bar(name="Positive", x=dates, y=pos,
                             marker_color="#16a34a", marker_line_width=0))
        fig.add_trace(go.Bar(name="Negative", x=dates, y=[-n for n in neg],
                             marker_color="#dc2626", marker_line_width=0))
        fig.add_trace(go.Bar(name="Neutral",  x=dates, y=neu,
                             marker_color="#d1d5db", marker_line_width=0))
        fig.update_layout(**PLOTLY_LAYOUT, barmode="relative", height=260,
                          showlegend=True, legend=dict(orientation="h",y=1.1,x=0),
                          xaxis_tickformat="%b %d")
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        render_section_title("Category Breakdown")
        grays = ["#000","#1a1a1a","#333","#555","#777","#999","#bbb","#d4d4d4"]
        fig2  = go.Figure(go.Pie(
            labels=[c.title() for c in cats], values=list(cats.values()),
            hole=.52, marker=dict(colors=grays[:len(cats)],
            line=dict(color="#fff", width=2)), textfont_size=11,
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=True,
                           legend=dict(orientation="v", x=1.02, y=.5, font_size=10))
        st.plotly_chart(fig2, use_container_width=True)

    render_divider()

    # ── Sentiment timeline ────────────────────────────────────────────────────
    render_section_title("Average Sentiment — Timeline")
    avgs = [r["avg_sentiment"] for r in ts]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=dates, y=avgs, mode="lines",
        line=dict(color="#000", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,0,0,.06)",
    ))
    fig3.add_hline(y=0, line_dash="dot", line_color="#ccc", line_width=1.5)
    fig3.update_layout(**PLOTLY_LAYOUT, height=180, showlegend=False,
                       yaxis_range=[-1,1], xaxis_tickformat="%b %d",
                       margin=dict(l=40,r=10,t=10,b=30))
    st.plotly_chart(fig3, use_container_width=True)

    render_divider()

    # ── Articles + Sidebar ────────────────────────────────────────────────────
    # Filters
    filters = render_filters(show_search=True, show_category=True,
                              show_sentiment=True, key_prefix="cp")
    filtered = apply_filters(articles, filters)

    col_feed, col_side = st.columns([3, 1])

    with col_feed:
        render_section_title(f"Latest Civic Events ({len(filtered)} articles)")

        if not filtered:
            st.info("No articles match your filters.")
        else:
            for i, a in enumerate(filtered[:15]):
                render_event_card(a, key_prefix=f"cp_{i}", show_inspect=False)

    with col_side:
        # Top Sources with bar
        render_section_title("Top Sources")
        src_counts: dict = {}
        for a in articles:
            s = (a.get("author") or "").split(",")[0].strip() or "Unknown"
            src_counts[s] = src_counts.get(s, 0) + 1
        top_srcs  = sorted(src_counts.items(), key=lambda x: -x[1])[:8]
        max_count = top_srcs[0][1] if top_srcs else 1
        src_html  = ""
        for name, cnt in top_srcs:
            pct = int(cnt / max_count * 100)
            src_html += f"""
            <div class="source-row">
              <span class="source-name">{name[:22]}</span>
              <span class="source-count">{cnt}</span>
            </div>
            <div class="data-bar"><div class="data-bar-fill" style="width:{pct}%"></div></div>"""
        st.markdown(f"""
        <div style="background:#fff;border:1.5px solid #e5e5e5;
          border-radius:12px;padding:1rem 1.25rem">{src_html}</div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Trending Keywords
        render_section_title("Trending Keywords")
        keywords = ["Trade Deal","Budget 2026","IPL 2026","ISRO","Air India",
                    "Delhi Polls","GDP Growth","UPI Record","Manipur","Cyclone Dana",
                    "Pharma City","Renewable Energy","Chandrayaan-4","Grammy 2026"]
        chips = " ".join(f'<span class="trending-chip">{k}</span>' for k in keywords)
        st.markdown(chips, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Sentiment breakdown
        render_section_title("Sentiment Split")
        pos_n = sum(1 for a in filtered if a.get("sentiment",0) >  0.2)
        neg_n = sum(1 for a in filtered if a.get("sentiment",0) < -0.2)
        neu_n = len(filtered) - pos_n - neg_n
        total_f = max(len(filtered), 1)
        for lbl, cnt, color in [
            ("Positive", pos_n, "#16a34a"),
            ("Neutral",  neu_n, "#9ca3af"),
            ("Negative", neg_n, "#dc2626"),
        ]:
            pct = int(cnt/total_f*100)
            st.markdown(f"""
            <div style="margin-bottom:.55rem">
              <div style="display:flex;justify-content:space-between;
                font-size:.8rem;font-weight:600;margin-bottom:.2rem">
                <span style="color:{color}">{lbl}</span><span>{cnt} ({pct}%)</span>
              </div>
              <div class="data-bar">
                <div class="data-bar-fill" style="width:{pct}%;background:{color}"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    render_divider()
    render_ai_panel(filtered or articles)
