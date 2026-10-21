# Technical Trial Test: AI/ML Engineer (~2h30m)

## What this test checks

You will build a small system that uses a language model as a working component: retrieval that respects document permissions, real prompt construction, tool calls through the model's own function-calling interface, and an honest record of what the model actually did, including its mistakes. You will also make the service safe to run on a single private machine.

Using an AI coding assistant to write your solution is fine and not graded. Apple Silicon / MLX deployment is out of scope, since it depends on hardware you may not have.

## Setup (10 min)

- `documents/`: eight short text files. `documents/acl.yaml` lists the groups allowed to read each file. A file can allow more than one group. A file allowed for `everyone` is readable by any signed-in user, whatever their groups.
- `data/properties.csv`: income and operating costs per property. `data/loans.csv`: loans per property, with annual debt service. Used in Task 2.
- `eval/questions.yaml`: six test questions, each with the user who asks it. Used in Task 3.
- `app/`: a starter package with function signatures and docstrings for what you implement (`search.py`, `tools.py`, `pipeline.py`, `accounts.py`), plus a provided `server.py`: a minimal FastAPI UI wired to your `answer()` so you can test in a browser once Tasks 1 and 2 work.
- `tests/test_access.py`: skeleton assertions for Task 3.
- `Dockerfile`, `docker-compose.yml`, `Makefile`: they run, so you can start Tasks 1–3 right away. Task 4 asks you to review them.

**The only local requirement is Docker.** `make up` builds and starts the app at http://localhost:8000. `make test` runs pytest inside the container. `make reindex` rebuilds the search index. Your working directory is mounted into the container, so code edits apply without a rebuild. Add any packages you need to `requirements.txt`.

**A working language model with real tool/function calling, your choice.** Task 2 requires the model's native function-calling interface: a hosted API (OpenAI- or Anthropic-style tool schemas both work) or a local model via Ollama that supports tools (e.g. `qwen3`, `qwen2.5`, `llama3.1`). `make` copies `.env.example` to `.env` on first run; put your settings and any hosted API key there. Running Ollama on your own machine? From inside the container, reach it at `http://host.docker.internal:11434`, not `localhost:11434`.

Which model you use, and where it runs, is not graded. The real project treats the model as swappable behind an internal API. What is graded is whether retrieval, generation and tool calling work against a real model's real behavior.

**Test users** (`app/accounts.py`):

| User | Groups |
| --- | --- |
| `analyst_1` | `finance`, `legal` |
| `leasing_1` | `leasing` |
| `staff_1` | none (`everyone` only) |

## Task 1: Permission-aware RAG with real generation (40 min)

Implement `search()` in `app/search.py` and the document-answering path of `answer()` in `app/pipeline.py`, so a user's question is answered by a real model using only evidence that user is allowed to read.

- Split the eight documents into chunks, embed each chunk with a real embedding model, and store each chunk's allowed groups with it when you build the index.
- `search(query, user_id, k)` looks up the user's groups itself and returns only chunks those groups allow (or chunks allowed for `everyone`), ranked by embedding similarity. The filter must run inside `search()`. Do not return extra results and filter them afterwards.
- Build a prompt from the retrieved chunks and the question, and get a real answer from your model, not a stub string. The answer must cite the chunk ids it relies on.
- If nothing retrieved answers the question, the answer must say so rather than guess.
- Implement `check_grounding()`. It returns a pass/fail plus reasons. It must flag (a) a cited chunk id that was not among the retrieved chunks, and (b) a key claim, such as a number, date or name, that does not appear in the chunks it cites.

Retrieval quality and grounding are graded together: did search find the right chunk, and is the answer honestly based on it?

## Task 2: Debt-service tool through native function calling (30 min)

In the real project, the model must never do financial math itself. Deterministic tools calculate, and the model only explains the result. Implement this with your model's actual tool-calling / function-calling API, not a keyword check that routes around the model.

- `calculate_dscr(property_id)` in `app/tools.py` computes the debt service coverage ratio from the data files: NOI ÷ total annual debt service, where NOI = gross income − vacancy loss − operating expenses. Some properties have more than one loan. A provider-neutral schema is sketched as `DSCR_TOOL_SCHEMA`; adapt it to your provider's format.
- Send the question to the model with the tool available. When the model requests the tool, run `calculate_dscr()` in code, return the result to the model, and let it write the final answer.
- If the property doesn't exist, or the DSCR can't be computed, the tool returns a clear error. The model must pass that on to the user and must not invent a number.
- The model must never answer with a DSCR or NOI figure it computed itself. If it tries, that is the failure this task is meant to catch.

This requires understanding your model's tool-calling protocol, including the back-and-forth message format most APIs require.

## Task 3: Run it and report what the model actually did (25 min)

Run the six questions in `eval/questions.yaml` through your pipeline, each as its listed user. You can use the UI (`make up`) or call `answer()` directly. Three are traps: one can't be answered from the documents, one asks about a document its user is not allowed to read, and one asks for the DSCR of a property that doesn't exist.

Add a table to this README with one row per question and these columns:

- **Question**: the text or its id.
- **User**: who asked it.
- **Retrieved chunks**: the chunk ids `search()` returned, plus a short quote from the top one. Specific enough for us to check.
- **Grounded?**: pass/fail from `check_grounding()`, with its reason when it fails.
- **Tool call**: for the DSCR questions, the exact call the model made (tool name, arguments) and what the tool returned. `n/a` for the others.
- **What the model actually did**: anything it got wrong (ignored an instruction, did the math itself, hinted at content from a document the user can't see, hedged when it shouldn't have). If it behaved correctly, say so explicitly.

We want the real retrieved evidence and the real tool calls, not a self-graded checklist. A model that behaves perfectly on all six is a valid result if you say so explicitly.

Also complete the assertions in `tests/test_access.py`, proving that `search()` never returns a chunk the user isn't allowed to read. Cover all three users, including `analyst_1`'s two groups and `staff_1`'s `everyone`-only access. These tests must pass without a live model or API key (Task 4 runs them in CI).

## Task 4: Make it safe to run on one private machine (35 min)

The real system runs on one company-owned machine and handles confidential financial data that must never leave the building.

**A. Review what we gave you.** The provided `Dockerfile`, `docker-compose.yml` and `Makefile` work, but they have security and reliability problems for this setting, and so does some of the provided code in `app/`. Find them, fix them, and explain each one in the table at the end of this README. We don't list the problems: finding them is part of the test.

**B. Build what's missing.**

1. **Health check.** `GET /healthz` returns 200 only when the index is loaded and the model endpoint is reachable, otherwise 503 with the reason. Wire it into Compose so a stuck container gets restarted.
2. **Request log.** One structured JSON line per question, with enough to debug and audit it: who asked, what was retrieved, which tools ran, which model, how long it took. It must never contain document text, the question or the answer.
3. **CI.** The repo has no CI. Add a GitHub Actions workflow that builds the image and runs the tests on every push, with no API key and no live model.
4. **Backup and restore.** Add `make backup` and `make restore` for the search index and any other state your app keeps. Restoring onto a fresh machine must work without re-embedding the documents.

In this README, also answer in three sentences or fewer: the machine's disk dies at 2am. What do you need to get the service back, how long does it take, and what is lost?

## Task 5: Design judgment (10 min)

Two or three sentences each, in this README:

- The real deployment runs a ~27B model on one Mac Studio shared by many employees at once, while background jobs re-index documents. What would you change in your prompt size, `k`, or request handling so live chat stays fast?
- An employee is removed from the `finance` group in the source system. In your design, how long until they stop getting finance chunks, and what would you change for production?
- Which part of your solution are you least confident is airtight, and why?

## What not to worry about

Whether you used an AI coding assistant. Which embedding model, LLM or tool-calling convention you pick. Kubernetes, cloud deployment or multiple machines. A front end beyond the provided UI. Edge cases beyond the given data. Code polish under time pressure.

## Submitting

Make exactly one commit with all your work, push it, then submit the form with your repo link before your time is up. Commits after your form submission disqualify you.

---

## Your results (fill in)

### Task 3: evaluation table

| Question | User | Retrieved chunks | Grounded? | Tool call | What the model actually did |
| --- | --- | --- | --- | --- | --- |
| q1 | analyst_1 | | | | |
| q2 | leasing_1 | | | | |
| q3 | staff_1 | | | | |
| q4 | analyst_1 | | | | |
| q5 | analyst_1 | | | | |
| q6 | analyst_1 | | | | |

### Task 4: problems found and fixes

| File | Problem | Why it matters here | Fix |
| --- | --- | --- | --- |
| | | | |

### Task 4: the disk dies at 2am


### Task 5: design answers

1.
2.
3.
