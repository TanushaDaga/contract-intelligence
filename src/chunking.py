"""Cut a contract into chunks and remember exactly where each chunk came from.

Every chunk is a dict with doc_id, start, end and text, and text == document[start:end].
That is what lets a retrieved chunk be compared directly with the ground truth character offsets.
"""
import re


# make one chunk, its text is always exactly the piece of the document from start to end
def _chunk(text, doc_id, start, end):
    return {"doc_id": doc_id, "start": start, "end": end, "text": text[start:end]}


def window_chunks(text, doc_id, size, overlap):
    """Fixed size windows. Each new window starts size - overlap characters after the last one."""
    # if the overlap was as big as the window we would never move forward
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size")
    # how far the window slides each time
    step = size - overlap
    chunks = []
    start = 0
    while start < len(text):
        # the window ends size characters later, or at the end of the text
        end = min(start + size, len(text))
        # skip windows that only contain spaces or blank lines
        if text[start:end].strip():
            chunks.append(_chunk(text, doc_id, start, end))
        # stop once the window has reached the end of the text
        if end == len(text):
            break
        start += step
    return chunks


def paragraph_spans(text):
    """Start and end of every paragraph, where paragraphs are separated by blank lines."""
    spans = []
    pos = 0
    # every blank line ends the paragraph that came before it
    for m in re.finditer(r"\n\s*\n", text):
        spans.append((pos, m.start()))
        pos = m.end()
    # whatever is left after the last blank line is the final paragraph
    spans.append((pos, len(text)))
    # drop paragraphs that are empty
    return [(s, e) for s, e in spans if text[s:e].strip()]


def paragraph_chunks(text, doc_id, max_chars, overlap):
    """Join neighbouring paragraphs until max_chars is reached.

    A paragraph that is longer than max_chars on its own is cut with the window chunker.
    """
    chunks = []
    # the chunk we are building right now (None means we have nothing yet)
    cur_start = cur_end = None

    # save the chunk we were building and start with an empty one
    def flush():
        nonlocal cur_start, cur_end
        if cur_start is not None:
            chunks.append(_chunk(text, doc_id, cur_start, cur_end))
        cur_start = cur_end = None

    for s, e in paragraph_spans(text):
        if e - s > max_chars:
            # this paragraph alone is too long, so save what we had and cut it with windows
            flush()
            for c in window_chunks(text[s:e], doc_id, max_chars, overlap):
                # add s so the positions count from the start of the whole document, not the paragraph
                chunks.append(_chunk(text, doc_id, s + c["start"], s + c["end"]))
        elif cur_start is not None and e - cur_start <= max_chars:
            # this paragraph still fits, so grow the current chunk to include it
            cur_end = e
        else:
            # it does not fit, so save the current chunk and start a new one with this paragraph
            flush()
            cur_start, cur_end = s, e
    # do not forget the last chunk
    flush()
    return chunks


# pick the chunking method that the settings ask for
def make_chunks(text, doc_id, cfg):
    if cfg.chunk_mode == "paragraph":
        return paragraph_chunks(text, doc_id, cfg.chunk_size, cfg.overlap)
    return window_chunks(text, doc_id, cfg.chunk_size, cfg.overlap)
