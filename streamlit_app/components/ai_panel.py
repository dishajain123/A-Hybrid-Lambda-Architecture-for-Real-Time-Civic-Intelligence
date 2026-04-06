import streamlit as st

_AI_CSS = """
<style>
.ai-panel {
    background: linear-gradient(135deg,#000 0%,#1a1a1a 100%);
    border-radius:14px; padding:1.5rem 1.75rem;
    color:#fff; margin-top:1.5rem;
    box-shadow:0 4px 20px rgba(0,0,0,.2);
}
.ai-panel h4 { color:#fff; margin:0 0 .75rem; font-size:1rem; font-weight:700; }
.ai-insight-item {
    background:rgba(255,255,255,.06); border-radius:9px;
    padding:.75rem 1rem; margin-bottom:.6rem;
    border-left:3px solid rgba(255,255,255,.3);
    font-size:.875rem; color:#ddd; line-height:1.55;
}
.ai-chip {
    display:inline-block; background:rgba(255,255,255,.12);
    border-radius:20px; padding:.2rem .65rem;
    font-size:.72rem; font-weight:600; color:#ccc;
    margin:.2rem; letter-spacing:.3px;
}
</style>
"""

def render_ai_panel(articles: list):
    st.markdown(_AI_CSS, unsafe_allow_html=True)
    if not articles:
        return

    sentiments  = [a.get("sentiment", 0) for a in articles]
    avg_s       = sum(sentiments) / len(sentiments)
    pos_count   = sum(1 for s in sentiments if s > 0.2)
    neg_count   = sum(1 for s in sentiments if s < -0.2)
    neu_count   = len(sentiments) - pos_count - neg_count

    cats = {}
    for a in articles:
        c = a.get("category", "general")
        cats[c] = cats.get(c, 0) + 1
    top_cat = max(cats, key=cats.get) if cats else "general"

    top_pos = sorted([a for a in articles if a.get("sentiment",0) > 0.2],
                     key=lambda x: x["sentiment"], reverse=True)
    top_neg = sorted([a for a in articles if a.get("sentiment",0) < -0.2],
                     key=lambda x: x["sentiment"])

    mood = "cautiously optimistic 📈" if avg_s > 0.1 else ("concerning 📉" if avg_s < -0.1 else "balanced ◆")

    cat_chips = " ".join(f'<span class="ai-chip">{c.title()} ({n})</span>' for c, n in
                         sorted(cats.items(), key=lambda x: -x[1])[:5])

    pos_title = top_pos[0]["title"][:80] + "…" if top_pos else "N/A"
    neg_title = top_neg[0]["title"][:80] + "…" if top_neg else "N/A"

    st.markdown(f"""
    <div class="ai-panel">
      <h4>🤖 AI Intelligence Summary</h4>
      <div class="ai-insight-item">
        <strong>Overall Mood:</strong> The current news cycle is <em>{mood}</em> —
        avg sentiment <strong>{avg_s:+.3f}</strong> across {len(articles)} articles
        ({pos_count} positive, {neg_count} negative, {neu_count} neutral).
      </div>
      <div class="ai-insight-item">
        <strong>Top Category:</strong> <em>{top_cat.title()}</em> dominates with
        {cats.get(top_cat,0)} articles. Active topics: {cat_chips}
      </div>
      <div class="ai-insight-item">
        <strong>Most Positive:</strong> {pos_title}
      </div>
      <div class="ai-insight-item">
        <strong>Most Concerning:</strong> {neg_title}
      </div>
    </div>
    """, unsafe_allow_html=True)