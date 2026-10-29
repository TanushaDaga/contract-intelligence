"""Web app.  Run with:  streamlit run app.py"""
import html

import streamlit as st

from src.config import CONFIG_DIR, Config
from src.data import load_corpus
from src.indexer import build_index
from src.retriever import Retriever

CONTEXT = 250

st.set_page_config(page_title="Contract Clause Search", layout="wide")


@st.cache_resource
def get_resources(config_name):
    cfg = Config.load(CONFIG_DIR / config_name)
    corpus = load_corpus()
    return Retriever(build_index(corpus, cfg), cfg), cfg, corpus


def highlighted(text, start, end):
    """Show some text around the passage and mark the passage itself."""
    a, b = max(0, start - CONTEXT), min(len(text), end + CONTEXT)
    parts = [html.escape(text[a:start]), "<mark>", html.escape(text[start:end]), "</mark>", html.escape(text[end:b])]
    body = "".join(parts).replace("\n", "<br>")
    return f"<div style='font-size:0.9rem;line-height:1.5'>{body}</div>"


st.title("Contract Clause Search")
st.caption("Finds the clause that answers a question, or says that none was found.")

with st.sidebar:
    config_name = st.selectbox("Configuration", ["final_config.json", "baseline_config.json"])
    retriever, cfg, corpus = get_resources(config_name)
    query = st.text_area("Question", "Consider the Promotion Agreement between Depomed, Inc. and King Pharmaceuticals, Inc. for Glumetza; What is the governing law for this contract?", height=140)
    top_k = st.slider("Number of passages", 1, 10, 3)
    threshold = st.slider("Abstention threshold", 0.0, 1.0, float(cfg.threshold), 0.005,
                          help="If the best score is below this the system returns nothing.")
    go = st.button("Search", type="primary")

if go and query.strip():
    result = retriever.search(query, top_k=top_k, threshold=threshold)
    if result["abstained"]:
        st.error("No relevant clause found. The system abstained because the best score "
                 f"({result['top1']:.3f}) is too low.")
    else:
        for i, p in enumerate(result["passages"], start=1):
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(f"**{i}. {p['doc_id']}**  \ncharacters {p['start']}:{p['end']}")
                right.metric("Score", f"{p['score']:.3f}")
                st.markdown(highlighted(corpus[p["doc_id"]], p["start"], p["end"]), unsafe_allow_html=True)
else:
    st.info("Enter a question and press Search.")
