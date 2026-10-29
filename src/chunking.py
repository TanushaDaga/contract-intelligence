"""Cut a contract into chunks and remember exactly where each chunk came from.

Every chunk is a dict with doc_id, start, end and text, and text == document[start:end].
That is what lets a retrieved chunk be compared directly with the ground truth character offsets.
"""
import re


def _chunk(text, doc_id, start, end):
    return {"doc_id": doc_id, "start": start, "end": end, "text": text[start:end]}


def window_chunks(text, doc_id, size, overlap):
    """Fixed size windows. Each new window starts size - overlap characters after the last one."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size")
    step = size - overlap
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if text[start:end].strip():
            chunks.append(_chunk(text, doc_id, start, end))
        if end == len(text):
            break
        start += step
    return chunks


def paragraph_spans(text):
    """Start and end of every paragraph, where paragraphs are separated by blank lines."""
    spans = []
    pos = 0
    for m in re.finditer(r"\n\s*\n", text):
        spans.append((pos, m.start()))
        pos = m.end()
    spans.append((pos, len(text)))
    return [(s, e) for s, e in spans if text[s:e].strip()]


def paragraph_chunks(text, doc_id, max_chars, overlap):
    """Join neighbouring paragraphs until max_chars is reached.

    A paragraph that is longer than max_chars on its own is cut with the window chunker.
    """
    chunks = []
    cur_start = cur_end = None

    def flush():
        nonlocal cur_start, cur_end
        if cur_start is not None:
            chunks.append(_chunk(text, doc_id, cur_start, cur_end))
        cur_start = cur_end = None

    for s, e in paragraph_spans(text):
        if e - s > max_chars:
            flush()
            for c in window_chunks(text[s:e], doc_id, max_chars, overlap):
                chunks.append(_chunk(text, doc_id, s + c["start"], s + c["end"]))
        elif cur_start is not None and e - cur_start <= max_chars:
            cur_end = e
        else:
            flush()
            cur_start, cur_end = s, e
    flush()
    return chunks


def make_chunks(text, doc_id, cfg):
    if cfg.chunk_mode == "paragraph":
        return paragraph_chunks(text, doc_id, cfg.chunk_size, cfg.overlap)
    return window_chunks(text, doc_id, cfg.chunk_size, cfg.overlap)
