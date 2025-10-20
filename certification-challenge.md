# 🚨 Traceback  
**Instant triage across docs, code & lineage.**

---

## 🧩 Problem Statement

On-call data engineers can’t quickly determine **business impact** or **blast radius** during production pipeline incidents because requirements live in **Confluence or Google Docs** and pipeline code is buried in **Git repos** and column-level lineage is trapped in **catalogs or graph UIs** and these sources are fragmented and **not built for fast triage**.

### ❗ Why Is This a Problem?

When a pipeline breaks, engineers spend the first **30–60 minutes** just chasing answers:

> “What dashboards went stale?”  
> “Which tables and columns are wrong?”  
> “Who else is affected?”  
> “Do we roll back or hotfix?”

The current state causes:

- 🔁 **Inflated MTTR**  
- ⏱️ **SLA breaches**  
- 📣 **Unclear updates to leadership**  
- 🛑 **Paused reports and broken trust**  
- ⚠️ **Risky hotfixes shipped without context**

A focused triaging that understands **docs**, **code**, and **lineage** can:

- Reduce triage time  
- Improve fix decisions (rollback vs patch)  
- Standardize incident communication

### 🎯 Audience

- **Primary:** On-call Data Engineers & Data Platform SREs  
- **Secondary:** Analytics Leads, Product Managers needing fast confirmation of data trust

---

## ✅ Solution: What is Traceback?

**Traceback** is a small, focused, agentic RAG app that unifies three fragmented sources to power fast, context-rich incident response:

- 📄 **Requirements docs** (PDF/MD)  
- 🧾 **Pipeline code snippets** (SQL/Py)  
- 🧬 **Column-level lineage graph** (JSON)

It answers natural-language questions like:

> “Job `curated.sales_orders` failed — who's impacted?”

And returns a structured incident brief:

- 📊 **Impact Summary**  
- 💥 **Blast Radius**  
- ❓ **Likely Causes**  
- 🛠️ **Safe Actions / Backfill Order** (with citations)



### ⚙️ Setup & Flow

For the challenge:

- All inputs are local:
  - `docs/` — PDFs, markdown  
  - `repo/` — SQL, Python, configs  
  - `lineage.json` — exported lightweight lineage graph
- System runs locally:
  - `FastAPI` endpoint  
  - Simple CLI
- Supports full end-to-end triage demo


### 🧰 Stack

| Component       | Tool                      | Why? |
|----------------|---------------------------|------|
| **LLM**         | OpenAI GPT-4.1-mini / GPT-4o-mini | Low latency, high reasoning |
| **Embeddings**  | `text-embedding-3-small`  | Cheap, accurate |
| **Orchestration** | LangGraph              | Agent loops, tool routing |
| **Vector Store**| Qdrant                    | Portable, zero-infra, fast |
| **Monitoring**  | LangSmith / JSON Logs     | Logs, traces, prompt captures |
| **Evaluation**  | RAGAS                     | Precision, recall, relevancy |
| **Interface**   | FastAPI + CLI + Swagger   | Fastest path to usable demo |


### 🧠 How Agentic Reasoning Works

- 🔁 Supervisor Agent (LangGraph)
    - Interprets user question
    - Routes to appropriate tools
    - Stops when it gets:
        - ✅ Impact Summary
        - ✅ Blast Radius
        - ✅ Suggested Actions

- 🛠️ Impact Assessor Agent
    - RAG over requirements/runbooks
    - Queries `lineage.json` graph
    - Code search over `repo/` (BM25)

- ✍️ Writer Agent
    - Crafts incident brief
    - Adds citations
    - Suggests rollback or backfill steps

### 🤖 Why Agentic?

- Breaks complex questions into subgoals  
- Chooses and sequences tools  
- Cross-validates retrieved context  
- Knows when enough evidence is gathered

---

## 🗂️ Dealing with Data

### Data sources
- 📄 Requirements & Runbooks

    - Location: `data/docs/*.pdf|md`  
    - Use: definitions, SLAs, ownership, incident protocols  
    - Examples:  
        - `Data Quality Playbook.md`  
        - `Sales Orders Domain Spec.pdf`

- 🧾 Pipeline Code & Configs

    - Location: `data/repo/**/*.(sql|py|yaml)`  
    - Use: table transforms, job owners, PR hints  
    - Ingestion: parse as raw text, capture file paths

- 🧬 Column Lineage Graph

    - Location: `data/lineage.json`  
    - Use: compute blast radius (table/column level)  
    - Format: simple directed graph

        ```json
        {
        "nodes":[
            {"id":"raw.sales_orders","type":"table","owners":["data-sales"]},
            {"id":"curated.sales_orders","type":"table"},
            {"id":"curated.sales_orders.net_sales","type":"column"}
        ],
        "edges":[
            {"from":"raw.sales_orders","to":"curated.sales_orders","op":"clean+join"},
            {"from":"curated.sales_orders.gross_sales","to":"curated.sales_orders.net_sales","op":"subtract_refunds"}
        ],
        "dashboards":[
            {"id":"bi.rev_daily","tables":["curated.sales_orders"],"teams":["Merch","Finance"]}
        ]
        }

        ```
- External API (single, lightweight):

    - Tavily Search (or SERP API)

    - Purpose: optional fresh lookups for error messages/root causes or library changes; enrich responses with a link or two.

- Why these sources?

    They map 1:1 to the triage questions: 
    - docs = “what is correct?”
    - code = “what changed?”
    - lineage = “who’s impacted?”
    - A single web search tool to add reference links for library upgrades or any changes.

### Default Chunking Strategy
- Docs (PDF/MD): semantic sections ~350–600 tokens, 10–15% overlap.

    - Why: preserves meaning across headings/paragraphs; overlap helps recall for boundary Qs.

- Code (SQL/Python/YAML):

    - SQL: split by top-level statement (CTE/CREATE/INSERT); cap at 400–700 tokens.

- Python/YAML: split by function/class or top-level key blocks; cap at 400–700 tokens.

    - Why: code answers hinge on local scope; function/statement boundaries improve precision.

- Lineage: no vector chunking; kept in memory/JSON and queried via a graph tool. We still index small textual notes (node/edge annotations) into Qdrant with payload {"kind":"lineage_note"} to make them retrievable when helpful.

- Why not bigger/smaller chunks ? Smaller chunks increase recall but hurt faithfulness; larger chunks increase context precision but waste tokens. The selected window (350–700 tokens) is a practical sweet spot for RAG over mixed docs+code.
---


