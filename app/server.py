"""Provided: a minimal UI for trying your pipeline in a browser.

You may change this file (Task 4 asks you to look at it).
"""
from __future__ import annotations

import html

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

from app.accounts import USERS
from app.pipeline import answer

app = FastAPI(title="Trial test v2")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    print(f"[request] {request.method} {request.url.path} body={body.decode(errors='replace')}")
    return await call_next(request)


def _page(content: str = "", question: str = "", user: str = "analyst_1") -> str:
    options = "".join(
        f'<option value="{u}" {"selected" if u == user else ""}>{u} ({", ".join(g) or "everyone only"})</option>'
        for u, g in USERS.items()
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Trial test v2</title>
<style>body{{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.5}}
textarea{{width:100%;height:5rem}} pre{{background:#f4f4f4;padding:.75rem;overflow:auto;white-space:pre-wrap}}
.box{{border:1px solid #ddd;border-radius:6px;padding:1rem;margin-top:1rem}}</style></head><body>
<h1>Ask the assistant</h1>
<form method="post" action="/ask">
<label>User <select name="user_id">{options}</select></label>
<p><textarea name="question" required>{html.escape(question)}</textarea></p>
<button type="submit">Ask</button></form>{content}</body></html>"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _page()


@app.post("/ask", response_class=HTMLResponse)
def ask(question: str = Form(...), user_id: str = Form(...)) -> str:
    try:
        a = answer(question, user_id)
    except NotImplementedError:
        return _page('<div class="box">Not implemented yet: finish Tasks 1 and 2.</div>', question, user_id)
    retrieved = "".join(
        f"<li><code>{html.escape(c.chunk_id)}</code> ({c.score:.3f}): {html.escape(c.text[:160])}</li>" for c in a.retrieved
    )
    tools = "".join(
        f"<li><code>{html.escape(t.name)}({html.escape(str(t.arguments))})</code> → <code>{html.escape(str(t.result))}</code></li>"
        for t in a.tool_calls
    ) or "<li>none</li>"
    grounding = "n/a" if a.grounded is None else ("pass" if a.grounded else "FAIL: " + "; ".join(a.grounding_reasons))
    content = f"""<div class="box"><h2>Answer</h2><pre>{html.escape(a.text)}</pre>
<p><b>Model:</b> {html.escape(a.model)} · <b>Cited:</b> {html.escape(", ".join(a.cited_chunk_ids) or "none")} · <b>Grounding:</b> {html.escape(grounding)}</p>
<h3>Retrieved chunks</h3><ul>{retrieved or "<li>none</li>"}</ul>
<h3>Tool calls</h3><ul>{tools}</ul></div>"""
    return _page(content, question, user_id)
