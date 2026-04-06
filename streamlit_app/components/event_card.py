import streamlit as st
import html
from components.severity_badge import sentiment_badge_html, category_badge_html

_CARD_CSS = """
<style>
.ev-card {
    background:#fff; border:1.5px solid #e5e5e5;
    border-radius:12px; padding:1.1rem 1.3rem;
    margin-bottom:.9rem; transition:all .2s ease;
    box-shadow:0 1px 4px rgba(0,0,0,.05);
    position:relative; overflow:hidden;
}
.ev-card::before {
    content:''; position:absolute; top:0; left:0;
    width:3px; height:100%; background:#000;
    border-radius:12px 0 0 12px;
}
.ev-card:hover {
    box-shadow:0 6px 20px rgba(0,0,0,.1);
    transform:translateY(-2px); border-color:#ccc;
}
.ev-card.ev-neg::before { background:#dc2626; }
.ev-card.ev-pos::before { background:#16a34a; }
.ev-card.ev-neu::before { background:#9ca3af; }

.ev-inner { display:flex; gap:1rem; align-items:flex-start; }
.ev-thumb {
    width:96px; height:68px; border-radius:8px;
    object-fit:cover; flex-shrink:0;
    border:1px solid #eee;
    background:#f5f5f5;
}
.ev-thumb-placeholder {
    width:96px; height:68px; border-radius:8px;
    background:#f0f0f0; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    font-size:1.4rem; border:1px solid #eee;
}
.ev-body { flex:1; min-width:0; }
.ev-badges { display:flex; gap:.35rem; margin-bottom:.4rem; flex-wrap:wrap; }
.ev-title {
    font-size:.95rem; font-weight:700; color:#111;
    margin:0 0 .35rem; line-height:1.4;
}
.ev-title a { color:inherit; text-decoration:none; }
.ev-title a:hover { text-decoration:underline; }
.ev-summary {
    font-size:.8rem; color:#555; margin:0 0 .5rem;
    line-height:1.55; display:-webkit-box;
    -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
}
.ev-meta {
    display:flex; flex-wrap:wrap; gap:.5rem;
    align-items:center; font-size:.72rem; color:#888;
}
.ev-meta span { display:flex; align-items:center; gap:.15rem; }
.ev-action {
    display:inline-block; margin-top:.55rem;
    background:#000; color:#fff; font-size:.72rem; font-weight:700;
    padding:.25rem .7rem; border-radius:6px; text-decoration:none;
    letter-spacing:.3px;
}
.ev-action:hover { background:#333; }
.sentiment-bar-wrap { height:3px; background:#f0f0f0; border-radius:2px; margin:.6rem 0 0; }
.sentiment-bar { height:3px; border-radius:2px; }

/* Compact card */
.ev-compact {
    background:#fff; border:1px solid #ebebeb; border-radius:9px;
    padding:.7rem .9rem; margin-bottom:.5rem;
    transition:border-color .15s;
}
.ev-compact:hover { border-color:#000; }
.ev-compact-title {
    font-size:.82rem; font-weight:700; color:#111; line-height:1.4;
    margin:0 0 .2rem;
}
.ev-compact-title a { color:inherit; text-decoration:none; }
.ev-compact-title a:hover { text-decoration:underline; }
.ev-compact-meta { font-size:.7rem; color:#888; display:flex; gap:.5rem; flex-wrap:wrap; }
</style>
"""

_ICON_MAP = {
    "politics":"🏛️","business":"💼","technology":"💻","general":"📰",
    "health":"🏥","sports":"🏏","entertainment":"🎬","lifestyle":"✨","default":"📰"
}

def inject_card_css():
    st.markdown(_CARD_CSS, unsafe_allow_html=True)

def render_event_card(
    article: dict,
    show_bar: bool = True,
    key_prefix: str = "ec",
    show_inspect: bool = True
):
    inject_card_css()
    s     = article.get("sentiment", 0)
    cls   = "ev-pos" if s > 0.2 else ("ev-neg" if s < -0.2 else "ev-neu")
    barcol= "#16a34a" if s > 0.2 else ("#dc2626" if s < -0.2 else "#9ca3af")
    bar_w = int(abs(s) * 100)

    title   = article.get("title","Untitled")
    url     = article.get("url","#") or "#"
    raw_summary = article.get("summary") or article.get("text","") or ""
    # Normalize noisy payload text and keep card excerpt compact.
    raw_summary = " ".join(str(raw_summary).split())
    summary = (raw_summary[:260] + "…") if len(raw_summary) > 260 else raw_summary
    date    = (article.get("publish_date") or "")[:10]
    author  = (article.get("author") or
               ", ".join(article.get("authors",[]) or []) or "Unknown")
    cat     = article.get("category","general")
    img_url = article.get("image","")
    art_id  = article.get("id","")
    icon    = _ICON_MAP.get(cat, _ICON_MAP["default"])

    s_badge = sentiment_badge_html(s)
    c_badge = category_badge_html(cat)

    # Escape dynamic text so embedded HTML in payload can't break card rendering.
    title_safe = html.escape(str(title))
    summary_safe = html.escape(str(summary))
    author_safe = html.escape(str(author[:28]))

    # Thumbnail HTML
    if img_url and img_url.startswith("http") and "spacer" not in img_url:
        thumb = f'<img class="ev-thumb" src="{img_url}" alt="{cat}" onerror="this.style.display=\'none\'">'
    else:
        thumb = f'<div class="ev-thumb-placeholder">{icon}</div>'

    # Avoid leading indentation here; markdown can render indented HTML as code block.
    bar_html = (
        f'<div class="sentiment-bar-wrap"><div class="sentiment-bar" '
        f'style="width:{bar_w}%;background:{barcol}"></div></div>'
    ) if show_bar else ""

    view_link = f'<a class="ev-action" href="{url}" target="_blank">Read Article ↗</a>'

    card_html = (
        f'<div class="ev-card {cls}">'
        f'  <div class="ev-inner">'
        f'    {thumb}'
        f'    <div class="ev-body">'
        f'      <div class="ev-badges">{s_badge}{c_badge}</div>'
        f'      <p class="ev-title"><a href="{url}" target="_blank">{title_safe}</a></p>'
        f'      <p class="ev-summary">{summary_safe}</p>'
        f'      <div class="ev-meta">'
        f'        <span>📅 {date}</span>'
        f'        <span>✍️ {author_safe}</span>'
        f'        <span>💬 {s:+.2f}</span>'
        f'      </div>'
        f'      {view_link}'
        f'    </div>'
        f'  </div>'
        f'  {bar_html}'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # "View Detail" session-state button
    btn_key = f"{key_prefix}_{art_id}_{title[:10]}"
    if show_inspect and art_id:
        if st.button("🔍 Inspect Event", key=btn_key, help="Open full detail view"):
            st.session_state["selected_article_id"] = str(art_id)
            st.session_state["_nav_to_detail"] = True
            st.rerun()

def render_compact_card(article: dict):
    inject_card_css()
    s     = article.get("sentiment", 0)
    color = "#16a34a" if s > 0.2 else ("#dc2626" if s < -0.2 else "#888")
    title = article.get("title","Untitled")
    url   = article.get("url","#") or "#"
    date  = (article.get("publish_date") or "")[:10]
    cat   = article.get("category","general")
    icon  = _ICON_MAP.get(cat, "📰")
    title_safe = html.escape(str(title))
    st.markdown(f"""
    <div class="ev-compact">
      <p class="ev-compact-title">
        {icon} <a href="{url}" target="_blank">{title_safe[:70]}{'…' if len(title_safe)>70 else ''}</a>
      </p>
      <div class="ev-compact-meta">
        <span style="color:{color};font-weight:700">{s:+.2f}</span>
        <span>📅 {date}</span>
        <span>{cat.title()}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
