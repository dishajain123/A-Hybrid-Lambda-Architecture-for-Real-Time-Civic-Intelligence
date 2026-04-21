import streamlit as st
import plotly.graph_objects as go
from urllib.parse import urlparse
import re

from components.header      import render_header, render_section_title, render_divider
from components.severity_badge import sentiment_badge_html, inject_badge_css, get_severity_color
from components.event_card  import inject_card_css, render_compact_card
from services.api_client    import get_client
from utils.constants        import PLOTLY_LAYOUT
import utils.dummy_data     as _dummy

_CSS = """
<style>
.detail-hero {
    background:#000; border-radius:16px; padding:2rem 2.25rem;
    margin-bottom:1.75rem; position:relative; overflow:hidden;
}
.detail-hero::before {
    content:''; position:absolute; top:-40px; right:-40px;
    width:180px; height:180px; border-radius:50%;
    background:rgba(255,255,255,.03);
}
.detail-hero h2 { color:#fff; font-size:1.5rem; margin:0 0 .75rem; line-height:1.4; }
.detail-hero-meta { display:flex; gap:1rem; flex-wrap:wrap; margin-top:.75rem; }
.detail-hero-meta span { font-size:.78rem; color:#aaa; }
.detail-hero-meta strong { color:#ddd; }
.detail-body {
    background:#fff; border:1.5px solid #e5e5e5; border-radius:14px;
    padding:1.5rem 1.75rem; margin-bottom:1.25rem;
    box-shadow:0 1px 4px rgba(0,0,0,.05);
}
.detail-body h4 { color:#000; font-weight:700; margin:0 0 .6rem; font-size:.95rem; }
.meta-table { width:100%; border-collapse:collapse; font-size:.84rem; }
.meta-table td { padding:.5rem .65rem; border-bottom:1px solid #f0f0f0; vertical-align:top; }
.meta-table td:first-child { font-weight:600; color:#555; width:130px; white-space:nowrap; }
.meta-table td:last-child  { color:#111; }

/* Entity cards */
.entity-card {
    display:inline-flex; align-items:center; gap:.5rem;
    background:#f5f5f5; border:1px solid #e5e5e5; border-radius:10px;
    padding:.45rem .75rem; margin:.25rem; font-size:.78rem;
    transition:border-color .2s;
}
.entity-card:hover { border-color:#000; }
.entity-type-badge {
    font-size:.62rem; font-weight:700; letter-spacing:.5px;
    padding:.15rem .45rem; border-radius:4px; text-transform:uppercase;
}
.entity-PER  { background:#dbeafe; color:#1e40af; }
.entity-ORG  { background:#fef3c7; color:#92400e; }
.entity-LOC  { background:#dcfce7; color:#166534; }
.entity-name { font-weight:600; color:#111; }
.entity-desc { color:#666; font-size:.72rem; }

/* Image gallery */
.img-gallery { display:flex; gap:.75rem; flex-wrap:wrap; margin:.75rem 0; }
.img-thumb {
    border:1.5px solid #e5e5e5; border-radius:10px;
    overflow:hidden; position:relative; cursor:pointer;
    transition:border-color .2s, box-shadow .2s;
}
.img-thumb:hover { border-color:#000; box-shadow:0 4px 12px rgba(0,0,0,.12); }
.img-thumb img { display:block; object-fit:cover; }
.img-dim { font-size:.65rem; color:#888; text-align:center; padding:.2rem 0 .3rem; background:#f9f9f9; }

/* Bronze metadata strip */
.bronze-strip {
    background:linear-gradient(135deg,#fff7ed,#fffbeb);
    border:1.5px solid #fed7aa; border-radius:10px;
    padding:.75rem 1rem; font-size:.78rem; color:#78350f;
    display:flex; flex-wrap:wrap; gap:1rem; align-items:center;
    margin-bottom:1rem;
}
.bronze-strip strong { color:#92400e; }

.pick-container { background:#f5f5f5; border-radius:12px; padding:1.25rem; margin-bottom:1.5rem; }
.pick-label { font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.8px; color:#888; margin-bottom:.75rem; }

/* Make action buttons readable regardless of theme */
div[data-testid="stButton"] > button {
    background:#111 !important;
    color:#fff !important;
    border:1px solid #111 !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background:#000 !important;
    color:#fff !important;
    border:1px solid #000 !important;
}
div[data-testid="stButton"] > button:hover {
    background:#000 !important;
    color:#fff !important;
}
div[data-testid="stButton"] > button *,
div[data-testid="stButton"] > button span,
div[data-testid="stButton"] > button p {
    color:#fff !important;
    -webkit-text-fill-color:#fff !important;
    opacity:1 !important;
}
div[data-testid="stButton"] > button:disabled,
div[data-testid="stButton"] > button:disabled * {
    color:#fff !important;
    -webkit-text-fill-color:#fff !important;
    opacity:1 !important;
}

/* Sentiment explanation card */
.sentiment-reason-card {
    background:#f8fafc;
    border:1.5px solid #e5e7eb;
    border-radius:12px;
    padding:.7rem .85rem;
    margin:.3rem 0 .55rem;
}
.sentiment-reason-title {
    font-size:.82rem;
    font-weight:800;
    color:#111;
    margin:0 0 .35rem;
}
.sentiment-reason-chip {
    display:inline-block;
    font-size:.72rem;
    font-weight:700;
    border-radius:999px;
    padding:.2rem .55rem;
    background:#e5e7eb;
    color:#1f2937;
    margin-bottom:.45rem;
}
.sentiment-reason-line {
    font-size:.82rem;
    color:#374151;
    line-height:1.45;
    margin:.12rem 0;
}
.sentiment-score-wrap p {
    margin-top:0;
    margin-bottom:.45rem;
}
.sentiment-left-head {
    margin:0 0 .2rem;
}
.sentiment-right-wrap {
    margin-top:-.15rem;
}
</style>
"""

_POSITIVE_KEYWORDS = {
    "deal", "slashed", "cut", "reduced", "reduction", "growth", "record", "rally",
    "surge", "jumped", "up", "profit", "beat", "boost", "improve", "improved",
    "good", "wins", "launch", "launched", "signed", "achievement", "exemption",
    "jobs", "capacity", "milestone", "opened", "support", "success", "successful",
    "faster", "ahead", "renewable"
}
_NEGATIVE_KEYWORDS = {
    "kills", "killed", "dead", "death", "injured", "collapse", "trapped", "violence",
    "crash", "malfunction", "grounded", "flood", "floods", "delayed", "disrupted",
    "toxic", "arrested", "damage", "loss", "decline", "fall", "suspended", "curfew",
    "outbreak", "risk", "warning", "trouble", "failure"
}


def _split_sentences(text: str):
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p and len(p.strip()) > 20]


def _extract_key_points(text: str, max_points: int = 3):
    sentences = _split_sentences(text)
    if not sentences:
        return []
    ranked = sorted(
        sentences,
        key=lambda x: (
            bool(re.search(r"\d", x)),
            any(k in x.lower() for k in ("because", "after", "following", "due to", "led", "will", "would")),
            len(x)
        ),
        reverse=True
    )
    points = []
    for sent in ranked:
        clean = sent.strip().rstrip(".")
        if clean and clean not in points:
            points.append(clean)
        if len(points) >= max_points:
            break
    return points


def _build_summary_display(article: dict):
    base_summary = (article.get("summary") or "").strip()
    full_text = (article.get("text") or "").strip()

    if not base_summary and not full_text:
        return None, []
    if not base_summary:
        base_summary = _split_sentences(full_text)[0] if _split_sentences(full_text) else "No summary available."

    key_points = _extract_key_points(full_text, max_points=3)
    key_points = [p for p in key_points if p.lower() not in base_summary.lower()]
    return base_summary, key_points


def _compute_sentiment_explanation(article: dict):
    score = float(article.get("sentiment", 0.0) or 0.0)
    label = "Positive" if score > 0.2 else ("Negative" if score < -0.2 else "Neutral")
    strength = (
        "strongly" if abs(score) >= 0.7
        else "clearly" if abs(score) >= 0.45
        else "slightly" if abs(score) >= 0.2
        else "mostly"
    )

    evidence_source = " ".join([
        str(article.get("title", "")),
        str(article.get("summary", "")),
        str(article.get("text", ""))
    ])
    text_blob = evidence_source.lower()
    tokens = set(re.findall(r"[a-zA-Z]+", text_blob))

    pos_hits = sorted([k for k in _POSITIVE_KEYWORDS if k in tokens or f" {k} " in text_blob])
    neg_hits = sorted([k for k in _NEGATIVE_KEYWORDS if k in tokens or f" {k} " in text_blob])
    evidence_points = _extract_key_points(evidence_source, max_points=2)

    if label == "Positive":
        reasons = [
            f"This story is {strength} positive because it mainly reports gains, progress, or relief."
        ]
        if evidence_points:
            reasons.append(f"What happened: {evidence_points[0]}.")
        if len(evidence_points) > 1:
            reasons.append(f"Why people may see this as good: {evidence_points[1]}.")
        reasons.append("In simple terms: this usually suggests better outcomes for people, markets, or services.")
    elif label == "Negative":
        reasons = [
            f"This story is {strength} negative because it mainly reports harm, disruption, or risk."
        ]
        if evidence_points:
            reasons.append(f"What happened: {evidence_points[0]}.")
        if len(evidence_points) > 1:
            reasons.append(f"Why people may see this as bad: {evidence_points[1]}.")
        reasons.append("In simple terms: this can mean more stress, cost, safety concerns, or uncertainty for people.")
    else:
        reasons = [
            "This story is neutral because it is mostly factual or has mixed good and bad signals."
        ]
        if evidence_points:
            reasons.append(f"What happened: {evidence_points[0]}.")
        if len(evidence_points) > 1:
            reasons.append(f"Context: {evidence_points[1]}.")
        reasons.append("In simple terms: this is informative, but not strongly good or bad overall.")

    if label == "Positive" and neg_hits:
        reasons.append("Note: there are a few caution signals too, so this is positive but not perfect.")
    if label == "Negative" and pos_hits:
        reasons.append("Note: there are a few positive points, but negatives dominate the story.")

    return label, strength, reasons


def _shorten_for_ui(text: str, limit: int = 115) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{cut}..."


def _is_valid_media_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url.lower().startswith(("http://", "https://")):
        return False
    if "spacer" in url.lower():
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def _is_valid_video_url(url: str) -> bool:
    if not _is_valid_media_url(url):
        return False
    u = url.lower()
    video_hints = (
        ".mp4", ".webm", ".ogg", ".m3u8",
        "youtube.com/watch", "youtu.be/", "vimeo.com/"
    )
    return any(h in u for h in video_hints)


def _normalize_media_url(url: str) -> str:
    if not isinstance(url, str):
        return ""
    return url.strip().rstrip("/").lower()


def _render_image_compat(url: str):
    """Render image across Streamlit versions (old/new width args)."""
    try:
        st.image(url, use_container_width=True)
    except TypeError:
        # Older Streamlit uses use_column_width
        st.image(url, use_column_width=True)


def _render_gallery_image_compat(url: str, width: int = 220):
    """Render smaller gallery thumbnail across Streamlit versions."""
    try:
        st.image(url, width=width)
    except TypeError:
        st.image(url)

def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    inject_card_css()
    inject_badge_css()
    render_header("Event Detail", "Deep-dive into a civic event — all data fields surfaced", "🔍")

    client   = get_client()
    articles = client.get_endpoint_articles("search_news", limit=80)
    if not articles:
        articles = _dummy.get_articles(limit=80)

    art_options = {a.get("title","Untitled")[:80]: a for a in articles}
    titles      = list(art_options.keys())

    preset_id    = st.session_state.get("selected_article_id")
    preset_title = None
    if preset_id:
        for a in articles:
            if str(a.get("id")) == str(preset_id):
                preset_title = a.get("title","")[:80]
                break

    # ── Picker ────────────────────────────────────────────────────────────────
    st.markdown('<div class="pick-container"><p class="pick-label">Select Article</p>', unsafe_allow_html=True)
    col_sel, col_rand = st.columns([4, 1])
    with col_sel:
        default_idx    = titles.index(preset_title) if preset_title in titles else 0
        selected_title = st.selectbox("Article", titles, index=default_idx, label_visibility="collapsed")
    with col_rand:
        import random
        if st.button("🎲 Random", use_container_width=True, type="primary", key="random_article_btn"):
            selected_title = random.choice(titles)
    st.markdown("</div>", unsafe_allow_html=True)

    article = art_options.get(selected_title, articles[0])
    s       = article.get("sentiment", 0)
    color   = get_severity_color(s)
    s_badge = sentiment_badge_html(s)
    cat     = article.get("category", "general")

    # ── Bronze layer metadata strip ───────────────────────────────────────────
    st.markdown(f"""
    <div class="bronze-strip">
      <span>🔶 <strong>Layer:</strong> Bronze (Raw)</span>
      <span>📡 <strong>Source API:</strong> World News API</span>
      <span>⚡ <strong>Pipeline Layer:</strong> Speed (Kafka → Consumer)</span>
      <span>🕐 <strong>Ingestion Time:</strong> {_dummy.METRICS_SUMMARY['last_ingestion']}</span>
      <span>🆔 <strong>Article ID:</strong> {article.get('id','N/A')}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="detail-hero">
      <div style="margin-bottom:.6rem">
        {s_badge}
        <span style="background:rgba(255,255,255,.12);color:#ccc;font-size:.7rem;font-weight:600;
          letter-spacing:.5px;text-transform:uppercase;padding:.2rem .6rem;border-radius:20px;margin-left:.3rem">
          {cat.title()}
        </span>
        <span style="background:rgba(255,255,255,.08);color:#999;font-size:.7rem;
          padding:.2rem .6rem;border-radius:20px;margin-left:.3rem">
          {article.get('language','en').upper()}
        </span>
      </div>
      <h2>{article.get('title','Untitled')}</h2>
      <div class="detail-hero-meta">
        <span>📅 <strong>{(article.get('publish_date') or '')[:10]}</strong></span>
        <span>✍️ <strong>{article.get('author','Unknown')}</strong></span>
        <span>🌐 <strong>{article.get('source_country','in').upper()}</strong></span>
        <span>💬 Sentiment <strong style="color:{color}">{s:+.3f}</strong></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])

    with col_main:
        # Summary
        summary, key_points = _build_summary_display(article)
        if summary:
            points_html = ""
            if key_points:
                points_html = "<ul style='margin:.65rem 0 0 1.1rem;padding:0;color:#333;font-size:.86rem;line-height:1.6'>"
                points_html += "".join(f"<li>{p}</li>" for p in key_points)
                points_html += "</ul>"
            st.markdown(f"""
            <div class="detail-body">
              <h4>📝 Summary</h4>
              <p style="margin:0;font-size:.9rem;line-height:1.75;color:#333">{summary}</p>
              {f"<h4 style='margin-top:.9rem'>Key Context from Article</h4>{points_html}" if points_html else ""}
            </div>
            """, unsafe_allow_html=True)

        # Image gallery (images[])
        images = [img for img in (article.get("images") or []) if _is_valid_media_url(img.get("url", ""))]
        hero_image = article.get("image")
        has_valid_hero = _is_valid_media_url(hero_image)
        hero_norm = _normalize_media_url(hero_image) if has_valid_hero else ""

        if has_valid_hero:
            render_section_title("Primary Image")
            _render_image_compat(hero_image)

        if images:
            gallery_images = []
            seen_urls = set()
            for img in images:
                raw_url = img.get("url", "")
                norm_url = _normalize_media_url(raw_url)
                if not norm_url or norm_url in seen_urls:
                    continue
                if hero_norm and norm_url == hero_norm:
                    continue
                seen_urls.add(norm_url)
                gallery_images.append(img)

            if gallery_images:
                render_section_title(f"Image Gallery ({len(gallery_images)} images)")
                gallery_images = gallery_images[:6]
                cols_per_row = min(3, len(gallery_images))
                for row_start in range(0, len(gallery_images), cols_per_row):
                    row_items = gallery_images[row_start: row_start + cols_per_row]
                    row_cols = st.columns(cols_per_row)
                    for i, img in enumerate(row_items):
                        url = img.get("url", "")
                        w = img.get("width", 400)
                        h = img.get("height", 300)
                        ttl = img.get("title", "") or ""
                        with row_cols[i]:
                            _render_gallery_image_compat(url, width=220)
                            st.caption(f"{w}×{h}px{' · ' + ttl if ttl else ''}")

        # Video field
        video = article.get("video")
        if _is_valid_video_url(video):
            render_section_title("Video")
            st.video(video)

        # Entities panel (entities[])
        entities = article.get("entities") or []
        if entities:
            render_section_title(f"Named Entities — NER ({len(entities)} detected)")
            ent_html = ""
            for e in entities:
                etype = e.get("type","ORG")
                name  = e.get("name","")
                desc  = e.get("description","")
                lat   = e.get("latitude")
                lon   = e.get("longitude")
                loc_t = e.get("location_type","")
                geo   = f" · 📍 {lat:.2f}, {lon:.2f} ({loc_t})" if lat and lon else ""
                ent_html += f"""
                <div class="entity-card">
                  <span class="entity-type-badge entity-{etype}">{etype}</span>
                  <span>
                    <span class="entity-name">{name}</span>
                    {f'<br><span class="entity-desc">{desc}{geo}</span>' if desc or geo else ''}
                  </span>
                </div>"""
            st.markdown(f'<div style="margin:.5rem 0 1.25rem">{ent_html}</div>', unsafe_allow_html=True)

            # Map entity locations if any LOC entities have coordinates
            loc_entities = [e for e in entities if e.get("type")=="LOC" and e.get("latitude")]
            if loc_entities:
                with st.expander(f"🗺️ Entity Location Map ({len(loc_entities)} locations)"):
                    import folium, io
                    import streamlit.components.v1 as sc
                    lats = [e["latitude"]  for e in loc_entities]
                    lons = [e["longitude"] for e in loc_entities]
                    m = folium.Map(location=[sum(lats)/len(lats), sum(lons)/len(lons)], zoom_start=3,
                                   tiles="CartoDB positron")
                    for e in loc_entities:
                        folium.CircleMarker(
                            location=[e["latitude"], e["longitude"]],
                            radius=8, color="#000", fill=True, fill_color="#000", fill_opacity=0.7,
                            popup=f'{e["name"]} ({e.get("location_type","LOC")})',
                            tooltip=e["name"],
                        ).add_to(m)
                    buf = io.BytesIO()
                    m.save(buf, close_file=False)
                    sc.html(buf.getvalue().decode(), height=300)

        # Full text
        full_text = article.get("text","")
        if full_text:
            with st.expander("📄 Full Article Text", expanded=False):
                st.markdown(f"""
                <div style="font-size:.875rem;line-height:1.8;color:#333;
                  max-height:500px;overflow-y:auto;padding-right:.5rem">
                  {full_text[:3000]}{'…' if len(full_text)>3000 else ''}
                </div>
                """, unsafe_allow_html=True)

        # Source link
        url = article.get("url","")
        if url:
            st.markdown(f'<a href="{url}" target="_blank" style="display:inline-block;margin:.5rem 0 1.25rem;'
                        f'background:#000;color:#fff;padding:.55rem 1.1rem;border-radius:8px;'
                        f'font-weight:600;font-size:.85rem;text-decoration:none">🔗 View Original Article</a>',
                        unsafe_allow_html=True)

        render_divider()

        # Sentiment gauge
        render_section_title("Sentiment Analysis")
        col_g, col_txt = st.columns([1.1, 1.35])
        with col_g:
            mood = "Positive 📈" if s>0.2 else ("Negative 📉" if s<-0.2 else "Neutral ◆")
            st.markdown(f"""
            <div class="sentiment-left-head">
              <p style="font-size:.82rem;color:#666;margin-bottom:.3rem">Sentiment Score</p>
              <p style="font-size:2.8rem;font-weight:900;color:{color};margin:0;line-height:1">{s:+.3f}</p>
              <p style="font-size:1rem;font-weight:700;color:#111;margin:.25rem 0 .3rem">{mood}</p>
            </div>
            """, unsafe_allow_html=True)
            fig_g = go.Figure(go.Indicator(
                mode="gauge",
                value=round(s, 3),
                domain={"x":[0,1], "y":[0,1]},
                gauge={
                    "axis":{"range":[-1,1], "tickvals":[-1,-.5,0,.5,1]},
                    "bar":{"color":color, "thickness":.2},
                    "bgcolor":"#f5f5f5", "borderwidth":0,
                    "steps":[
                        {"range":[-1,-.2], "color":"#fee2e2"},
                        {"range":[-.2,.2], "color":"#f3f4f6"},
                        {"range":[.2,1],   "color":"#dcfce7"},
                    ],
                    "threshold":{"line":{"color":color,"width":4},"thickness":.8,"value":s},
                },
            ))
            fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=250,
                                margin=dict(l=20,r=20,t=10,b=10))
            st.plotly_chart(fig_g, use_container_width=True)

        with col_txt:
            sentiment_label, sentiment_strength, sentiment_reasons = _compute_sentiment_explanation(article)
            reasons_html = "".join(
                f"<p class='sentiment-reason-line'>• {_shorten_for_ui(r)}</p>" for r in sentiment_reasons[:3]
            )
            st.markdown(f"""
            <div class="sentiment-right-wrap" style="padding:.05rem 0 0">
              <div class="sentiment-reason-card">
                <p class="sentiment-reason-title">Why this is {sentiment_label.lower()}</p>
                <span class="sentiment-reason-chip">{sentiment_strength.title()} {sentiment_label}</span>
                {reasons_html}
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        # Metadata table (all fields)
        render_section_title("Full Article Metadata")
        meta_rows = [
            ("id",             str(article.get("id","N/A"))),
            ("language",       article.get("language","en").upper()),
            ("category",       article.get("category","general").title()),
            ("source_country", article.get("source_country","in").upper()),
            ("sentiment",      f"{s:+.3f}"),
            ("publish_date",   (article.get("publish_date") or "")[:16]),
            ("layer",          "Bronze (Raw)"),
            ("source_api",     "World News API"),
            ("pipeline",       "Speed (Kafka)"),
        ]
        rows_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in meta_rows)
        st.markdown(f"""
        <div class="detail-body" style="padding:1rem 1.1rem">
          <table class="meta-table">{rows_html}</table>
        </div>
        """, unsafe_allow_html=True)

        # Authors
        authors = article.get("authors") or ([article.get("author")] if article.get("author") else ["Unknown"])
        render_section_title("Authors")
        for au in authors[:4]:
            if au:
                st.markdown(f"""
                <div style="background:#f5f5f5;border-radius:8px;padding:.5rem .75rem;
                  margin-bottom:.35rem;font-size:.83rem;font-weight:600">
                  ✍️ {au}
                </div>
                """, unsafe_allow_html=True)

        # Images metadata (images[] dimensions)
        images = article.get("images") or []
        if images:
            render_section_title(f"Images Array ({len(images)})")
            for i, img in enumerate(images[:4]):
                w = img.get("width",0)
                h = img.get("height",0)
                t = img.get("title","") or f"Image {i+1}"
                st.markdown(f"""
                <div style="background:#f9f9f9;border:1px solid #e5e5e5;border-radius:8px;
                  padding:.45rem .75rem;margin-bottom:.3rem;font-size:.75rem">
                  <strong>{t[:25]}</strong><br>
                  <span style="color:#888">{w}×{h}px</span>
                </div>
                """, unsafe_allow_html=True)

        render_divider()
        render_section_title("Related Articles")
        same_cat = [a for a in articles
                    if a.get("category")==article.get("category")
                    and a.get("id") != article.get("id")][:5]
        for a in (same_cat or articles[:5]):
            render_compact_card(a)
