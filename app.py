"""Web app.  Run with:  streamlit run app.py"""
import html

import streamlit as st

from src.config import CONFIG_DIR, Config
from src.data import load_corpus
from src.indexer import build_index
from src.retriever import Retriever

# how many characters of the contract to show before and after the found passage
CONTEXT = 250

# the title on the browser tab and a wide page layout
st.set_page_config(page_title="Contract Clause Search", layout="wide")


# cache_resource keeps this in memory so the index is built once and not on every click
@st.cache_resource
def get_resources(config_name):
    cfg = Config.load(CONFIG_DIR / config_name)
    corpus = load_corpus()
    return Retriever(build_index(corpus, cfg), cfg), cfg, corpus


def highlighted(text, start, end):
    """Show some text around the passage and mark the passage itself."""
    # the window to show, kept inside the contract
    a, b = max(0, start - CONTEXT), min(len(text), end + CONTEXT)
    # html.escape makes the contract text safe to put in a web page, and <mark> highlights the passage
    parts = [html.escape(text[a:start]), "<mark>", html.escape(text[start:end]), "</mark>", html.escape(text[end:b])]
    # line breaks in the contract become line breaks in the page
    body = "".join(parts).replace("\n", "<br>")
    return f"<div style='font-size:0.9rem;line-height:1.5'>{body}</div>"


st.title("Contract Clause Search")
st.caption("Finds the clause that answers a question, or says that none was found.")

# the left panel with all the inputs
with st.sidebar:
    config_name = st.selectbox("Configuration", ["final_config.json", "baseline_config.json"])
    retriever, cfg, corpus = get_resources(config_name)
    query = st.text_area("Question", "Consider the Promotion Agreement between Depomed, Inc. and King Pharmaceuticals, Inc. for Glumetza; What is the governing law for this contract?", height=140)
    top_k = st.slider("Number of passages", 1, 10, 3)
    # the slider starts at the saved threshold, and the user can move it to see the effect
    threshold = st.slider("Abstention threshold", 0.0, 1.0, float(cfg.threshold), 0.005,
                          help="If the best score is below this the system returns nothing.")
    go = st.button("Search", type="primary")

# the main area: runs only after Search is pressed with a non empty question
if go and query.strip():
    result = retriever.search(query, top_k=top_k, threshold=threshold)
    if result["abstained"]:
        # red banner when the system decides not to answer
        st.error("No relevant clause found. The system abstained because the best score "
                 f"({result['top1']:.3f}) is too low.")
    else:
        # one box per passage
        for i, p in enumerate(result["passages"], start=1):
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(f"**{i}. {p['doc_id']}**  \ncharacters {p['start']}:{p['end']}")
                right.metric("Score", f"{p['score']:.3f}")
                st.markdown(highlighted(corpus[p["doc_id"]], p["start"], p["end"]), unsafe_allow_html=True)
else:
    st.info("Enter a question and press Search.")
