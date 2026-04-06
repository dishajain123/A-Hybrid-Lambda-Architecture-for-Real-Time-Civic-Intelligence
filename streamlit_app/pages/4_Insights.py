"""
Page 4: Insights — Full historical analytics dashboard.
Covers: sentiment trends, volume, categories, trending keywords,
top sources, sentiment distribution, geo distribution, gold layer stats.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from components.header  import render_header, render_section_title, render_divider
from services.api_client import get_client
from utils.constants    import PLOTLY_LAYOUT
import utils.dummy_data as _dummy

_CSS = """
<style>
.insight-kpi {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:14px;
    padding:1.2rem 1.4rem; box-shadow:4px 4px 0 #000;
    transition:all .2s; text-align:center; cursor:default;
}
.insight-kpi:hover { transform:translate(-2px,-2px); box-shadow:6px 6px 0 #000; }
.insight-kpi-val { font-size:2rem; font-weight:900; color:#000; line-height:1; }
.insight-kpi-lbl { font-size:.68rem; font-weight:700; color:#888; text-transform:uppercase; letter-spacing:.8px; margin-top:.25rem; }

.gold-badge   { display:inline-block; background:linear-gradient(135deg,#b45309,#d97706); color:#fff; border-radius:6px; padding:.18rem .6rem; font-size:.68rem; font-weight:700; margin-left:.35rem; }
.silver-badge { display:inline-block; background:linear-gradient(135deg,#374151,#6b7280); color:#fff; border-radius:6px; padding:.18rem .6rem; font-size:.68rem; font-weight:700; margin-left:.35rem; }
.bronze-badge { display:inline-block; background:linear-gradient(135deg,#92400e,#b45309); color:#fff; border-radius:6px; padding:.18rem .6rem; font-size:.68rem; font-weight:700; margin-left:.35rem; }

.kw-chip {
    display:inline-block; padding:.3rem .8rem; border-radius:20px;
    font-size:.78rem; font-weight:600; margin:.2rem; cursor:default;
    transition:all .15s;
}
.src-bar-row { display:flex; align-items:center; gap:.75rem; margin-bottom:.6rem; }
.src-bar-label { width:120px; font-size:.82rem; font-weight:600; color:#111; text-align:right; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.src-bar-track { flex:1; background:#f0f0f0; border-radius:20px; height:8px; }
.src-bar-fill  { background:#000; border-radius:20px; height:8px; }
.src-bar-count { font-size:.78rem; font-weight:700; color:#000; width:30px; }
.layer-card { border-radius:12px; padding:1.2rem 1.4rem; margin-bottom:.75rem; border-left:4px solid; }
.layer-bronze { background:#fff7ed; border-color:#d97706; }
.layer-silver { background:#f9fafb; border-color:#6b7280; }
.layer-gold   { background:#fffbeb; border-color:#b45309; }
</style>
"""

random.seed(42)

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    render_header("Insights", "Historical analytics across the Lambda pipeline — Bronze → Silver → Gold", "📊")

    client  = get_client()
    metrics = client.get_metrics_summary() or _dummy.get_metrics()
    ts      = _dummy.get_time_series()
    cats    = _dummy.get_category_breakdown()
    articles= _dummy.get_articles(limit=100)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    k1,k2,k3,k4,k5 = st.columns(5)
    kpis = [
        (metrics.get("total_articles",847),   "Total Articles"),
        (metrics.get("bronze_objects",624),   "Bronze Objects"),
        (metrics.get("silver_objects",420),   "Silver Objects"),
        (metrics.get("gold_objects",240),     "Gold Objects"),
        (metrics.get("minio_objects",1284),   "MinIO Total"),
    ]
    for col, (val, lbl) in zip([k1,k2,k3,k4,k5], kpis):
        with col:
            st.markdown(f"""
            <div class="insight-kpi">
              <div class="insight-kpi-val">{val:,}</div>
              <div class="insight-kpi-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Date range ────────────────────────────────────────────────────────────
    render_section_title("Select Analysis Period")
    today = datetime.now().date()
    dc1, dc2, _ = st.columns([1,1,2])
    with dc1: start_date = st.date_input("From", today - timedelta(days=30), key="ins_s")
    with dc2: end_date   = st.date_input("To",   today,                       key="ins_e")

    fts = [r for r in ts
           if start_date.strftime("%Y-%m-%d") <= r["date"] <= end_date.strftime("%Y-%m-%d")]
    if not fts: fts = ts[-30:]

    dates  = [r["date"]          for r in fts]
    avgs   = [r["avg_sentiment"] for r in fts]
    counts = [r["article_count"] for r in fts]
    pos_c  = [r["positive"]      for r in fts]
    neg_c  = [r["negative"]      for r in fts]
    neu_c  = [r["neutral"]       for r in fts]

    render_divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "📈 Sentiment",
        "📊 Volume",
        "🏷️ Categories",
        "🔑 Keywords & Sources",
        "🗺️ Geographic",
        "🏆 Gold Layer",
    ])

    # ── Tab 1: Sentiment ──────────────────────────────────────────────────────
    with tab1:
        period_avg = sum(avgs)/max(len(avgs),1)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Period Avg Sentiment", f"{period_avg:+.3f}")
        m2.metric("Peak Positive Day",    f"{max(avgs):+.3f}")
        m3.metric("Peak Negative Day",    f"{min(avgs):+.3f}")
        m4.metric("Days Analysed",        len(fts))

        render_section_title("Daily Average Sentiment")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=avgs, mode="lines+markers",
            line=dict(color="#000", width=2.5),
            marker=dict(size=5,
                        color=avgs,
                        colorscale=[[0,"#dc2626"],[0.5,"#9ca3af"],[1,"#16a34a"]],
                        cmin=-1, cmax=1),
            fill="tozeroy", fillcolor="rgba(0,0,0,.06)",
        ))
        fig.add_hline(y=0, line_dash="dot", line_color="#ddd", line_width=1.5)
        fig.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_range=[-1,1],
                          xaxis_tickformat="%b %d")
        st.plotly_chart(fig, use_container_width=True)

        render_section_title("Sentiment Distribution (Overall)")
        total_arts = sum(pos_c)+sum(neg_c)+sum(neu_c)
        pos_total  = sum(pos_c); neg_total = sum(neg_c); neu_total = sum(neu_c)
        col_pie, col_stats = st.columns([1,1])
        with col_pie:
            fig_pie = go.Figure(go.Pie(
                labels=["Positive","Neutral","Negative"],
                values=[pos_total, neu_total, neg_total],
                hole=.5,
                marker=dict(
                    colors=["#16a34a","#9ca3af","#dc2626"],
                    line=dict(color="#fff", width=2),
                ),
                textinfo="label+percent",
                textfont_size=12,
            ))
            fig_pie.update_layout(**PLOTLY_LAYOUT, height=280, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_stats:
            st.markdown("<br>", unsafe_allow_html=True)
            for lbl, n, color in [
                ("Positive",pos_total,"#16a34a"),
                ("Neutral", neu_total,"#9ca3af"),
                ("Negative",neg_total,"#dc2626"),
            ]:
                pct = round(n/max(total_arts,1)*100,1)
                st.markdown(f"""
                <div style="margin-bottom:.75rem">
                  <div style="display:flex;justify-content:space-between;margin-bottom:.2rem">
                    <span style="color:{color};font-weight:700;font-size:.9rem">{lbl}</span>
                    <span style="font-weight:800">{n} &nbsp;<span style="color:#888;font-weight:400">({pct}%)</span></span>
                  </div>
                  <div style="background:#f0f0f0;border-radius:20px;height:7px">
                    <div style="background:{color};border-radius:20px;height:7px;width:{pct}%"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        render_section_title("Pos vs Neg Stacked Over Time")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Positive",x=dates,y=pos_c,marker_color="#16a34a",marker_line_width=0))
        fig2.add_trace(go.Bar(name="Negative",x=dates,y=neg_c,marker_color="#dc2626",marker_line_width=0))
        fig2.add_trace(go.Bar(name="Neutral", x=dates,y=neu_c,marker_color="#d1d5db",marker_line_width=0))
        fig2.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=260,
                           xaxis_tickformat="%b %d",
                           legend=dict(orientation="h",y=1.1,x=0))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 2: Volume ─────────────────────────────────────────────────────────
    with tab2:
        render_section_title("Daily Article Volume")
        fig3 = go.Figure(go.Bar(
            x=dates, y=counts,
            marker=dict(
                color=avgs,
                colorscale=[[0,"#dc2626"],[0.5,"#d1d5db"],[1,"#16a34a"]],
                cmin=-1, cmax=1,
                showscale=True,
                colorbar=dict(title="Sentiment", len=.6, x=1.01),
            ),
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_tickformat="%b %d")
        st.plotly_chart(fig3, use_container_width=True)

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            render_section_title("7-Day Rolling Average")
            rolling = [sum(counts[max(0,i-6):i+1])/len(counts[max(0,i-6):i+1]) for i in range(len(counts))]
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=dates, y=counts, mode="lines",
                                      line=dict(color="#e5e5e5",width=1), name="Daily"))
            fig4.add_trace(go.Scatter(x=dates, y=rolling, mode="lines",
                                      line=dict(color="#000",width=2.5), name="7-day avg"))
            fig4.update_layout(**PLOTLY_LAYOUT, height=240, showlegend=True)
            st.plotly_chart(fig4, use_container_width=True)

        with col_v2:
            render_section_title("By Day of Week")
            wday_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            wday_cnt   = {}
            for r in fts:
                try:
                    wd = datetime.strptime(r["date"],"%Y-%m-%d").weekday()
                    wday_cnt[wd] = wday_cnt.get(wd,0) + r["article_count"]
                except: pass
            wv = [wday_cnt.get(i,0) for i in range(7)]
            fig5 = go.Figure(go.Bar(
                x=wday_names, y=wv,
                marker_color=["#000" if v==max(wv) else "#e5e5e5" for v in wv],
                marker_line_width=0,
                text=wv, textposition="outside",
            ))
            fig5.update_layout(**PLOTLY_LAYOUT, height=240, showlegend=False)
            st.plotly_chart(fig5, use_container_width=True)

    # ── Tab 3: Categories ─────────────────────────────────────────────────────
    with tab3:
        col_c1, col_c2 = st.columns(2)
        grays = ["#000","#1a1a1a","#333","#555","#777","#999","#bbb","#ddd"]
        with col_c1:
            render_section_title("Category Volume")
            fig6 = go.Figure(go.Bar(
                x=list(cats.values()), y=[c.title() for c in cats],
                orientation="h",
                marker=dict(color=grays[:len(cats)], line_width=0),
                text=list(cats.values()), textposition="outside",
            ))
            fig6.update_layout(**PLOTLY_LAYOUT, height=340,
                               yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig6, use_container_width=True)

        with col_c2:
            render_section_title("Category Share")
            fig7 = go.Figure(go.Pie(
                labels=[c.title() for c in cats], values=list(cats.values()),
                hole=.52,
                marker=dict(colors=grays[:len(cats)], line=dict(color="#fff",width=2)),
                textfont_size=11,
            ))
            fig7.update_layout(**PLOTLY_LAYOUT, height=340,
                               legend=dict(orientation="v",x=1.02,y=.5,font_size=10))
            st.plotly_chart(fig7, use_container_width=True)

        render_section_title("Category × Avg Sentiment")
        cat_sent = {}
        for a in articles:
            c = a.get("category","general")
            cat_sent.setdefault(c,[]).append(a.get("sentiment",0))
        cat_avgs = {c: round(sum(v)/len(v),3) for c,v in cat_sent.items() if v}
        cs = list(cat_avgs.keys()); vs = list(cat_avgs.values())
        fig8 = go.Figure(go.Bar(
            x=[c.title() for c in cs], y=vs,
            marker=dict(
                color=vs,
                colorscale=[[0,"#dc2626"],[0.5,"#d1d5db"],[1,"#16a34a"]],
                cmin=-1, cmax=1, showscale=True,
                colorbar=dict(title="Sentiment",len=.8),
            ),
            text=[f"{v:+.2f}" for v in vs], textposition="outside",
        ))
        fig8.add_hline(y=0, line_dash="dot", line_color="#ccc")
        fig8.update_layout(**PLOTLY_LAYOUT, height=270,
                           showlegend=False, yaxis_range=[-1,1])
        st.plotly_chart(fig8, use_container_width=True)

    # ── Tab 4: Keywords & Sources ─────────────────────────────────────────────
    with tab4:
        col_k, col_s = st.columns(2)

        with col_k:
            render_section_title("Trending Keywords")
            st.markdown("""
            <p style="font-size:.8rem;color:#666;margin-bottom:.75rem">
              Most frequently referenced topics across all ingested articles
            </p>
            """, unsafe_allow_html=True)
            keywords_data = [
                ("Trade Deal", 89, "#000"),    ("Budget 2026", 76, "#1a1a1a"),
                ("ISRO", 68, "#333"),           ("IPL 2026", 62, "#444"),
                ("Air India", 54, "#555"),      ("GDP Growth", 49, "#666"),
                ("Delhi Elections", 44, "#777"),("UPI Record", 41, "#888"),
                ("Manipur Violence", 38, "#999"),("Cyclone Dana", 34, "#aaa"),
                ("Chandrayaan-4", 31, "#bbb"),  ("Renewable Energy", 28, "#ccc"),
                ("Grammy 2026", 22, "#ddd"),    ("Pharma City", 19, "#e0e0e0"),
            ]
            # Keyword chips
            chips = "".join(
                f'<span class="kw-chip" style="background:{c};color:{"#fff" if i<8 else "#333"}">'
                f'{kw} <strong>({n})</strong></span>'
                for i,(kw,n,c) in enumerate(keywords_data)
            )
            st.markdown(f'<div style="line-height:2">{chips}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            render_section_title("Keyword Frequency Chart")
            kw_names  = [k for k,_,_ in keywords_data]
            kw_counts = [n for _,n,_ in keywords_data]
            fig_kw = go.Figure(go.Bar(
                x=kw_counts, y=kw_names, orientation="h",
                marker=dict(
                    color=kw_counts,
                    colorscale=[[0,"#ddd"],[1,"#000"]],
                    showscale=False,
                ),
                text=kw_counts, textposition="outside",
            ))
            fig_kw.update_layout(**PLOTLY_LAYOUT, height=380,
                                 yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_kw, use_container_width=True)

        with col_s:
            render_section_title("Top News Sources")
            st.markdown("""
            <p style="font-size:.8rem;color:#666;margin-bottom:.75rem">
              Sources ranked by article count in current dataset
            </p>
            """, unsafe_allow_html=True)
            sources_data = [
                ("The Hindu",       24),
                ("News18",          21),
                ("Financial Express",18),
                ("Times Now",       15),
                ("NDTV",            12),
                ("India Today",      9),
                ("Hindustan Times",  8),
                ("Economic Times",   7),
            ]
            max_src = sources_data[0][1]
            bars_html = ""
            for name, cnt in sources_data:
                pct = int(cnt/max_src*100)
                bars_html += f"""
                <div class="src-bar-row">
                  <div class="src-bar-label">{name}</div>
                  <div class="src-bar-track">
                    <div class="src-bar-fill" style="width:{pct}%"></div>
                  </div>
                  <div class="src-bar-count">{cnt}</div>
                </div>"""
            st.markdown(f'<div style="padding:.5rem 0">{bars_html}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            render_section_title("Source × Sentiment")
            src_names = [s for s,_ in sources_data]
            src_sents = [round(random.uniform(-0.3, 0.7), 3) for _ in sources_data]
            random.seed(42)
            fig_ss = go.Figure(go.Bar(
                x=src_names, y=src_sents,
                marker=dict(
                    color=src_sents,
                    colorscale=[[0,"#dc2626"],[0.5,"#d1d5db"],[1,"#16a34a"]],
                    cmin=-1, cmax=1, showscale=False,
                ),
                text=[f"{v:+.2f}" for v in src_sents], textposition="outside",
            ))
            fig_ss.add_hline(y=0, line_dash="dot", line_color="#ccc")
            fig_ss.update_layout(**PLOTLY_LAYOUT, height=240,
                                 showlegend=False, yaxis_range=[-1,1],
                                 xaxis_tickangle=-35)
            st.plotly_chart(fig_ss, use_container_width=True)

    # ── Tab 5: Geographic ─────────────────────────────────────────────────────
    with tab5:
        geo_data = client.get_geo_coordinates() or _dummy.get_geo_data()
        render_section_title("Cities by Article Count")
        sorted_geo = sorted(geo_data, key=lambda x: x.get("article_count",0), reverse=True)[:15]
        city_names = [g["city"].split(",")[0] for g in sorted_geo]
        city_vals  = [g.get("article_count",0) for g in sorted_geo]
        city_sents = [g.get("avg_sentiment",0)  for g in sorted_geo]

        fig_geo = go.Figure(go.Bar(
            x=city_vals, y=city_names, orientation="h",
            marker=dict(
                color=city_sents,
                colorscale=[[0,"#dc2626"],[0.5,"#d1d5db"],[1,"#16a34a"]],
                cmin=-1, cmax=1,
                showscale=True,
                colorbar=dict(title="Avg Sentiment", len=.7),
            ),
            text=[f"{v} arts · {s:+.2f}" for v,s in zip(city_vals,city_sents)],
            textposition="outside",
        ))
        fig_geo.update_layout(**PLOTLY_LAYOUT, height=420,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_geo, use_container_width=True)

        render_divider()
        render_section_title("Region Summary Table")
        import pandas as pd
        df_rows = [{
            "City":      g["city"],
            "Region":    g.get("region","India"),
            "Country":   g.get("country","India"),
            "Articles":  g.get("article_count",0),
            "Avg Sentiment": round(g.get("avg_sentiment",0),3),
            "Mood": "Positive" if g.get("avg_sentiment",0)>0.2 else ("Negative" if g.get("avg_sentiment",0)<-0.2 else "Neutral"),
        } for g in sorted_geo]
        st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

    # ── Tab 6: Gold Layer ─────────────────────────────────────────────────────
    with tab6:
        render_section_title("MinIO Layer Breakdown")
        c1,c2,c3 = st.columns(3)
        for col, cls, badge, emoji, count, desc, eps in [
            (c1,"layer-bronze","bronze-badge","🔶",
             metrics.get("bronze_objects",624),
             "Raw, immutable objects exactly as received from the API and Kafka stream.",
             ["search_news","top_news","extract_news","feed_rss","geo_coordinates","extract_news_links"]),
            (c2,"layer-silver","silver-badge","🥈",
             metrics.get("silver_objects",420),
             "Cleaned and enriched by Flink. De-duplicated, schema-normalised, sentiment scored.",
             ["articles_cleaned","locations_enriched","keywords_extracted"]),
            (c3,"layer-gold","gold-badge","🥇",
             metrics.get("gold_objects",240),
             "Pre-aggregated analytics. Updated by scheduled Flink batch jobs every 15 min.",
             ["sentiment_timeseries","category_breakdown","trending_topics","city_heatmap","top_sources"]),
        ]:
            with col:
                ep_list = "".join(f"<li style='font-size:.77rem;color:#555'><code>{e}</code></li>" for e in eps)
                st.markdown(f"""
                <div class="{cls} layer-card">
                  <span class="{badge} {'gold-badge' if 'gold' in badge else badge}">{emoji} {badge.replace('-badge','').title()}</span>
                  <div style="font-size:1.8rem;font-weight:900;color:#000;margin:.4rem 0 .2rem">{count:,}</div>
                  <div style="font-size:.72rem;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.5rem">objects stored</div>
                  <p style="font-size:.78rem;color:#555;margin-bottom:.5rem;line-height:1.5">{desc}</p>
                  <ul style="margin:.4rem 0 0;padding-left:1rem">{ep_list}</ul>
                </div>
                """, unsafe_allow_html=True)

        render_divider()
        render_section_title("Pipeline Performance")
        pm1,pm2,pm3,pm4 = st.columns(4)
        pm1.metric("Kafka Throughput",  metrics.get("kafka_throughput","142 msg/min"))
        pm2.metric("API Latency",       f"{metrics.get('api_latency_ms',87)} ms")
        pm3.metric("Active Flink Jobs", metrics.get("flink_jobs_active",3))
        pm4.metric("Kafka Consumer Lag",metrics.get("kafka_lag",0))

        render_section_title("Objects Per Layer — Chart")
        fig_l = go.Figure(go.Bar(
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
        fig_l.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=False)
        st.plotly_chart(fig_l, use_container_width=True)