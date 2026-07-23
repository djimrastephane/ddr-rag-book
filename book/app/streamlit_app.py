"""Ask the Reports — the book's final payoff, in one small screen.

Ask an engineering question against the sample Daily Drilling Report
archive and see the whole idea end to end: retrieval → local-model answer
→ citations → the original evidence. Evidence first, answer second.

Run it with:
    streamlit run book/app/streamlit_app.py

The retrieval and generation are the book's own code (Chapters 4, 5, 9),
imported, not reimplemented. This file is only the screen around them.
"""

import html

import streamlit as st

import helpers
from helpers import run_query

APP_TITLE = "Ask the Reports"

SAMPLE_QUESTIONS = [
    {"label": "🎣 Fishing operation", "question": "What led to the fishing operation on report #50?"},
    {"label": "🔧 Stuck pipe event", "question": "What happened around the stuck pipe event?"},
    {"label": "🌡️ High torque", "question": "Which reports mention high torque?"},
    {"label": "⚠️ Tight hole", "question": "Which reports mention tight hole?"},
    {"label": "🔩 Packer setting failure", "question": "What operational issue followed the packer setting failure?"},
]

# ------------------------------------------------------------------
# Styling — a calmer, less system-like look than Streamlit's defaults.
# Injected once via unsafe_allow_html, the same approach the pipeline
# banner already used before this redesign.
# ------------------------------------------------------------------
CUSTOM_CSS = """
<style>
.stApp { background-color: #14181f; }
section[data-testid="stSidebar"] { background-color: #10141a; }

/* Softer primary buttons: a calm teal instead of Streamlit's default red */
.stButton > button[kind="primary"] {
    background-color: #2f9e8f;
    border-color: #2f9e8f;
    color: #ffffff;
}
.stButton > button[kind="primary"]:hover {
    background-color: #3bb5a3;
    border-color: #3bb5a3;
}
.stButton > button[kind="secondary"] {
    border-color: #2d333b;
}

/* Bordered containers (evidence cards) get softer, rounder borders */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #2d333b !important;
    border-radius: 12px !important;
}

/* Breathing room between major sections */
div[data-testid="stVerticalBlock"] > div { margin-bottom: 0.15rem; }
h2, h3 { margin-top: 1.4rem; }

/* Evidence card internals */
.ev-badges { margin-bottom: 0.5rem; line-height: 2.1; }
.badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    margin: 0 0.3rem 0.3rem 0;
    border-radius: 999px;
    font-size: 0.78rem;
    background-color: rgba(255,255,255,0.07);
    color: #c9d1d9;
    white-space: nowrap;
}
.badge--best { background-color: #2f9e8f; color: #ffffff; font-weight: 600; }
.badge--term { border: 1px solid #3a4048; background-color: transparent; }
.ev-why {
    color: #9aa4af;
    font-size: 0.88rem;
    margin-bottom: 0.5rem;
    overflow-wrap: break-word;
}
.ev-passage-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6e7681;
    margin-bottom: 0.15rem;
}
.ev-passage {
    color: #e6edf3;
    line-height: 1.5;
    overflow-wrap: break-word;
    word-wrap: break-word;
}
.ev-meta {
    color: #6e7681;
    font-size: 0.8rem;
    margin-top: 0.6rem;
}
/* Answer card: a calmer, research-report look instead of a green "success" box */
.answer-card {
    background-color: #182a28;
    border: 1px solid #2f4a45;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    overflow-wrap: break-word;
}
.answer-card p { margin-bottom: 0.6rem; }
.caution-line {
    background-color: #2a2410;
    border: 1px solid #4a3f16;
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    color: #e0c268;
    font-size: 0.88rem;
    margin-top: 0.6rem;
}

/* Keep long tokens (filenames, prompts) from overflowing on narrow screens.
   st.code renders <pre> with white-space:pre, which disables wrapping
   entirely -- overflow-wrap alone has no effect on it, so wrapping has to
   be turned back on explicitly for these blocks (e.g. long local paths
   inside a popover, which has no horizontal scrollbar of its own). */
code, .stMarkdown code { overflow-wrap: break-word; word-break: break-word; }
.stCode pre, .stCode pre code {
    white-space: pre-wrap !important;
    word-break: break-all !important;
    overflow-wrap: break-word !important;
}
</style>
"""


def render_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading the embedding model (first run only)…")
def load_model():
    """Load Chapter 4's embedding model once and reuse it across queries.
    device='cpu' is pinned to match the book's documented numbers."""
    from semantic_search import MODEL_NAME
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME, device="cpu")


@st.cache_data(show_spinner="Preparing the sample archive (first run only)…")
def prepare_archive():
    """Make sure the extracted-text folder exists (rebuild it from the
    committed sample PDFs on a fresh clone). Runs once, then cached."""
    helpers.ensure_text_dir()
    return True


def render_how_this_works():
    with st.expander("ℹ️ How this works"):
        st.markdown(
            "<div style='text-align:center;padding:6px 0 2px;color:#9aa4af;font-size:0.92rem'>"
            "📄 DDR PDFs &nbsp;→&nbsp; 📝 Text &nbsp;→&nbsp; 🔎 Retriever "
            "&nbsp;→&nbsp; 🧠 Local model &nbsp;→&nbsp; ✅ Answer + Evidence"
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Every report is searched by meaning and by exact wording, the best "
            "matches are handed to a local language model, and the model is told "
            "to answer only from that evidence — never from what it already knew."
        )


def citation_for(card: dict) -> str:
    """A short, human-readable citation string for a card -- shown in a
    code block so the reader gets a free copy-to-clipboard button."""
    bits = [card["filename"]]
    if card["report_number"]:
        bits.append(f"Report #{card['report_number']}")
    if card["date"]:
        bits.append(card["date"])
    return " — ".join(bits)


def render_answer(result: dict):
    st.subheader("Answer")

    if result["generated"]:
        answer_html = html.escape(result["answer"]).replace("\n", "<br>")
        st.markdown(
            f"<div class='answer-card'><p>{answer_html}</p></div>",
            unsafe_allow_html=True,
        )
        st.caption("Generated from the supporting reports below. Check it against the source reports.")

        top = result["cards"][0] if result["cards"] else None
        if top and not top["terms"]:
            st.markdown(
                "<div class='caution-line'>⚠️ This answer draws on the closest "
                "reports by meaning, but none of them contain an exact word "
                "from your question — double-check it against the original "
                "reports below before relying on it.</div>",
                unsafe_allow_html=True,
            )
    elif result["ollama_message"]:
        st.warning(result["ollama_message"])
    else:
        st.caption("Retrieval only — turn on “Generate answer” in the sidebar for a written answer.")


def render_evidence_card(card: dict, is_best: bool):
    with st.container(border=True):
        badges = []
        if is_best:
            badges.append('<span class="badge badge--best">✓ Best match</span>')
        if card["report_number"]:
            badges.append(f'<span class="badge">Report #{html.escape(card["report_number"])}</span>')
        if card["date"]:
            badges.append(f'<span class="badge">{html.escape(card["date"])}</span>')
        for term in card["terms"][:4]:
            badges.append(f'<span class="badge badge--term">{html.escape(term)}</span>')

        st.markdown(f'<div class="ev-badges">{"".join(badges)}</div>', unsafe_allow_html=True)

        if card["why"]:
            st.markdown(f'<div class="ev-why">💡 {html.escape(card["why"])}</div>', unsafe_allow_html=True)

        st.markdown('<div class="ev-passage-label">Relevant passage</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ev-passage">“{html.escape(card["snippet"])}”</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="ev-meta">Match strength: {card["score"]:.3f} &nbsp;·&nbsp; '
            f'{html.escape(card["filename"])}</div>',
            unsafe_allow_html=True,
        )

        key_base = card["filename"]
        cols = st.columns(3)
        with cols[0]:
            with st.popover("📄 Open source", use_container_width=True, key=f"open-{key_base}"):
                st.caption("Local file path — open it in your file browser or PDF viewer:")
                pdf_path = helpers.SAMPLE_DDRS / (card["filename"].removesuffix(".txt") + ".pdf")
                st.code(str(pdf_path), language=None)
        with cols[1]:
            with st.popover("📋 Copy citation", use_container_width=True, key=f"cite-{key_base}"):
                st.code(citation_for(card), language=None)
        with cols[2]:
            with st.popover("🔎 Show full passage", use_container_width=True, key=f"full-{key_base}"):
                st.text(card["full_text"])


def render_evidence(result: dict):
    st.subheader("Supporting reports")
    st.caption("The reports that matched your question, best first.")
    for i, card in enumerate(result["cards"]):
        render_evidence_card(card, is_best=(i == 0))


def render_transparency(result: dict):
    with st.expander("Why this answer?"):
        st.markdown("The transparency panel: everything behind the answer above.")
        st.markdown("**Your question**")
        st.code(result["query"], language=None)

        st.markdown("**Retrieved reports (ranked)**")
        for card in result["cards"]:
            st.markdown(f"- `{card['filename']}` — match strength {card['score']:.3f}")

        st.markdown("**Answer source**")
        st.write(
            "Generated by the local model from the evidence above."
            if result["generated"]
            else "Retrieval only — no answer was generated."
        )

        if result["prompt"]:
            st.markdown("**Prompt sent to the local model**")
            prompt = result["prompt"]
            shown = prompt[:4000] + ("\n\n… (truncated for display)" if len(prompt) > 4000 else "")
            st.code(shown, language=None)


def render_result(result: dict):
    st.subheader("Question")
    st.write(result["query"])
    render_answer(result)
    render_evidence(result)
    render_transparency(result)


def render_limitations():
    st.divider()
    st.caption(
        "This app is for learning. It runs on a small public sample archive. "
        "Always verify answers against the original report before using them for "
        "engineering decisions — the engineer remains responsible for the call."
    )


def render_sidebar() -> tuple[str, int, bool, str, bool]:
    st.sidebar.header("Ask a question")

    if "question" not in st.session_state:
        st.session_state["question"] = SAMPLE_QUESTIONS[0]["question"]
    if "recent_questions" not in st.session_state:
        st.session_state["recent_questions"] = []

    # A suggestion/recent-question button can't set st.session_state["question"]
    # directly -- the text_area below is already bound to that key, and
    # Streamlit forbids reassigning a widget's key once it's been instantiated
    # in the same run. So a click stashes the new value here, and it's applied
    # *before* the text_area is created on the rerun that follows.
    pending = st.session_state.pop("pending_question", None)
    if pending is not None:
        st.session_state["question"] = pending

    question = st.sidebar.text_area(
        "Your question", key="question", height=80,
        help="Type your own question, or pick a suggestion below.",
    )

    st.sidebar.markdown("**Suggested questions**")
    sugg_cols = st.sidebar.columns(1)
    for item in SAMPLE_QUESTIONS:
        if sugg_cols[0].button(item["label"], use_container_width=True, key=f"sugg-{item['label']}"):
            st.session_state["pending_question"] = item["question"]
            st.rerun()

    if st.session_state["recent_questions"]:
        st.sidebar.markdown("**Recent questions**")
        for q in st.session_state["recent_questions"][:5]:
            short = q if len(q) <= 46 else q[:43] + "…"
            if st.sidebar.button(short, use_container_width=True, key=f"recent-{q}"):
                st.session_state["pending_question"] = q
                st.rerun()

    st.sidebar.divider()
    generate = st.sidebar.checkbox("Generate answer", value=True,
                                    help="Uses a local Ollama model. Retrieval works either way.")
    top_k = st.sidebar.slider("Number of evidence matches", 1, 10, 3)

    with st.sidebar.expander("⚙️ Advanced settings"):
        model_name = st.text_input(
            "Ollama model", helpers.DEFAULT_MODEL,
            help="Any model you've already pulled with `ollama pull` works here.",
        )

    asked = st.sidebar.button("Ask", type="primary", use_container_width=True)
    return question.strip(), top_k, generate, model_name, asked


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛢️", layout="centered")
    render_css()

    st.title(APP_TITLE)
    st.caption("Ask a question. See the evidence. Check the source.")
    render_how_this_works()

    question, top_k, generate, model_name, asked = render_sidebar()

    if asked and question:
        recents = st.session_state["recent_questions"]
        st.session_state["recent_questions"] = [question] + [q for q in recents if q != question]

        prepare_archive()
        model = load_model()
        spinner = "Retrieving evidence" + ("… and generating an answer" if generate else "") + "…"
        with st.spinner(spinner):
            st.session_state["result"] = run_query(
                question, model,
                top_k=top_k, generate=generate, model_name=model_name,
            )

    result = st.session_state.get("result")
    if result:
        render_result(result)
    else:
        st.info("Pick a question in the sidebar and press **Ask**.")

    render_limitations()


if __name__ == "__main__":
    main()
