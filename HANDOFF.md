# Handoff Document: Enterprise Knowledge Base with AutoGen

**Date**: 25 May 2026  
**Status**: Ready for Integration & Advanced Features  
**Owner (previous)**: Mansidak Singh  
**Next Owner**: [To be assigned]

---

## Executive Summary

You are receiving a **working multi-agent knowledge base prototype** with the following completed:

- ✅ **Core agent pipeline** (QueryRouter → Retriever → Analyst → FactChecker → Synthesizer)
- ✅ **Hybrid SQL + RAG retrieval** (FAISS embeddings + keyword fallback)
- ✅ **LLM adapter** (optional OpenAI/Azure integration, safe fallback stubs)
- ✅ **Chroma vector DB support** (optional persistence layer)
- ✅ **Full test suite** (integration tests, semantic tests with graceful skip)
- ✅ **Configuration & bootstrap** (venv setup, .env.template, docs)
- ✅ **GroupChat skeleton** (groupchat_config.json ready for AutoGen runtime)

**User Stories Completed**: US-01 through US-07 (see Status section below)

---

## Quick Start (5 minutes)

```bash
# 1. Activate venv (or create new)
python3 -m venv .venv
source .venv/bin/activate

# 2. Bootstrap minimal deps
bash ./scripts/bootstrap.sh

# 3. Install semantic packages (optional but recommended)
pip install sentence-transformers numpy faiss-cpu chromadb openai

# 4. Copy and fill in .env
cp .env.template .env
# Edit .env to add OPENAI_API_KEY or AZURE_OPENAI_* keys

# 5. Run tests
pytest -q
# or without pytest:
python3 - <<'EOF'
import tempfile, sys
from pathlib import Path
sys.path.insert(0, '.')
from tests import test_pipeline
with tempfile.TemporaryDirectory() as tmp:
    test_pipeline.test_pipeline_happy_path(Path(tmp))
print('✓ All tests passed')
EOF

# 6. Run interactive session
python3 main.py
```

---

## User Story Status

| US-ID | Title | Status | Notes |
|-------|-------|--------|-------|
| US-01 | Project Setup | ✅ Complete (manual install) | See Setup section; requires pip install for semantic features |
| US-02 | Multi-Agent System Design | ✅ Complete | groupchat_config.json generated; ready for AutoGen wiring |
| US-03 | Retriever Agent | ✅ Complete | FAISS + Chroma + keyword fallback all working |
| US-04 | Analyst Agent | ✅ Complete | Query classification, analysis, pattern detection |
| US-05 | Fact-Checker Agent | ✅ Complete | Basic claim validation, confidence scoring |
| US-06 | Synthesizer Agent | ✅ Complete | LLM-optional answer synthesis with citations |
| US-07 | Hybrid SQL + RAG Query Router | ✅ Complete | Keyword heuristic routing; optional LLM upgrade available |
| US-08 | Text2SQL Integration | ❌ Not started | (Candidate for next developer: use LangChain SQLAgent) |
| US-09 | Vector Database Integration | ✅ Partial | FAISS/Chroma working; production DB integration needed |
| US-10–13 | Data & Memory Pipelines | ⏸️ Scaffolded | Retriever supports CSV/JSON; Redis memory not wired |
| US-14–17 | Monitoring & Dashboards | ⏸️ Scaffolded | Logs exported; FastAPI dashboard not implemented |
| US-18–20 | Advanced Features (Debate, Cost Tracking, Benchmarking) | ⏸️ Not started | Roadmap items for future phase |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                      USER QUERY                           │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │       QueryRouter (US-07)      │
        │   Classify: SQL|RAG|Hybrid     │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │    RetrieverAgent (US-03)      │
        │  - Database queries (SQL)      │
        │  - Semantic search (FAISS)     │
        │  - Chroma persistence (opt.)   │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │     AnalystAgent (US-04)       │
        │  - Query interpretation        │
        │  - Data analysis               │
        │  - Pattern detection           │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   FactCheckerAgent (US-05)     │
        │  - Claim validation            │
        │  - Confidence scoring          │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   SynthesizerAgent (US-06)     │
        │  - Answer synthesis            │
        │  - Citation generation         │
        │  - LLM-assisted (optional)     │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │   FINAL ANSWER WITH CONFIDENCE │
        └────────────────────────────────┘
```

---

## File Structure

```
enterprise_kb_autogen/
├── README.md                       # Project overview
├── HANDOFF.md                      # This file
├── .env.template                   # Environment variables template
├── setup.py                        # Project initialization
├── requirements.txt                # Python dependencies
│
├── main.py                         # Main orchestrator
├── llm_adapter.py                  # LLM provider adapter (OpenAI/Azure/stub)
├── autogen_groupchat.py           # GroupChat config generator
│
├── retriever_agent.py              # US-03: Retriever (SQL + RAG + FAISS + Chroma)
├── analyst_agent.py                # US-04: Analyst (query interpretation & analysis)
├── fact_checker_agent.py           # US-05: Fact-Checker (validation & confidence)
├── synthesizer_agent.py            # US-06: Synthesizer (final answer generation)
├── query_router.py                 # US-07: Query router (SQL/RAG/hybrid classification)
│
├── scripts/
│   └── bootstrap.sh                # Dev environment setup (idempotent)
│
├── docs/
│   └── SETUP.md                    # Detailed setup instructions
│
├── tests/
│   ├── test_pipeline.py            # Integration test (main pipeline)
│   ├── test_semantic_retrieval.py  # Semantic RAG test (skip if no deps)
│   ├── test_faiss_persistence.py   # FAISS index save/load test
│   └── test_chroma_integration.py  # Chroma indexing test
│
├── data/
│   ├── documents/                  # (to be populated) User documents
│   ├── csv_files/                  # (to be populated) Structured data
│   ├── faiss_index/                # FAISS vector index (auto-generated)
│   └── chromadb/                   # Chroma DB persistence (auto-generated)
│
├── logs/                           # Agent logs & conversation history
├── groupchat_config.json           # AutoGen GroupChat configuration
└── __init__.py                     # Package initializer
```

---

## Key Components & How They Work

### 1. **Query Router** (`query_router.py`)
Classifies user queries as:
- **SQL**: Numeric, temporal, or structured data queries
- **RAG**: Semantic, explanation, or document-focused queries
- **Hybrid**: Requires both structured + unstructured data

Uses keyword heuristics; can be upgraded to use a small LLM classifier.

### 2. **Retriever Agent** (`retriever_agent.py`)
Performs data retrieval with **three fallback layers**:
1. **FAISS + sentence-transformers** (semantic embeddings, free)
2. **Chroma** (managed vector DB with persistence, optional)
3. **Keyword search** (fallback; always available)

Supports SQLite databases with keyword fallback for natural-language SQL.

### 3. **Analyst Agent** (`analyst_agent.py`)
Extracts insights from retrieved data:
- Query interpretation (factual, trend, comparative, causal)
- Key finding extraction
- Pattern identification
- Metrics calculation
- Business impact assessment

### 4. **Fact-Checker Agent** (`fact_checker_agent.py`)
Validates claims from the Analyst:
- Extracts claims from analysis
- Matches against source documents
- Assigns confidence levels (HIGH/MEDIUM/LOW)
- Flags unverified or low-confidence statements

### 5. **Synthesizer Agent** (`synthesizer_agent.py`)
Produces final answers:
- Executive summary (optionally using LLM for better prose)
- Detailed analysis with formatting
- Source citations
- Caveats and recommendations
- Confidence assessment

### 6. **LLM Adapter** (`llm_adapter.py`)
Safe pluggable LLM bridge:
- Calls OpenAI or Azure OpenAI if API keys present
- Falls back to deterministic stubs for offline testing
- Non-breaking; tests pass without LLM keys

---

## Testing

### Run All Tests
```bash
pytest -q
```

### Run Specific Test File
```bash
pytest tests/test_pipeline.py -v
pytest tests/test_semantic_retrieval.py -v  # Skips if sentence-transformers missing
```

### Run Without pytest
```bash
python3 tests/test_pipeline.py
```

### Expected Results
- ✅ Integration test always passes (stub fallbacks ensure no LLM dependency)
- ✅ Semantic tests skip gracefully if FAISS/Chroma packages not installed
- ✅ All agents initialize and run through full pipeline

---

## Configuration

### Environment Variables (`.env`)

Copy `.env.template` to `.env` and fill in:

```bash
# LLM Provider (pick one)
OPENAI_API_KEY=sk-your-key-here
# OR
AZURE_OPENAI_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment

# Vector DB
VECTOR_DB_TYPE=faiss    # or 'chroma'
VECTOR_DB_PATH=./data/faiss_index

# Database
DATABASE_URL=sqlite:///./knowledge_base.db

# Logging
LOG_LEVEL=INFO
```

### Adding Documents
1. Place `.txt` or `.json` files in `data/documents/`
2. Retriever indexes them automatically on init
3. FAISS index builds lazily on first semantic search

### Adding CSV/Database Data
1. Place CSV files in `data/csv_files/`
2. Create SQLite DB at `knowledge_base.db` with `CREATE TABLE` statements
3. Retriever queries the database when SQL routing is triggered

---

## Next Developer: Immediate Action Items

### 🔴 Critical (start here)

1. **Install dependencies locally**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install sentence-transformers faiss-cpu chromadb openai
   pytest -q  # verify all tests pass
   ```

2. **Set up `.env`**
   ```bash
   cp .env.template .env
   # Add OPENAI_API_KEY or Azure creds
   ```

3. **Review code**
   - Start with `main.py` (orchestration flow)
   - Read `query_router.py` and `retriever_agent.py` (most complex)
   - Skim agent classes for their workflows

### 🟡 High Priority (next week)

4. **Integrate AutoGen runtime** (US-02 advanced)
   - Use `groupchat_config.json` and create an actual AutoGen `GroupChat` object
   - Wire agent tools and message passing
   - Test with mock LLM calls

5. **Implement Text2SQL** (US-08)
   - Replace keyword fallback in Retriever with LangChain `SQLAgent`
   - Test with sample databases

6. **Add FastAPI admin dashboard** (US-15)
   - Create endpoints: `/logs`, `/health`, `/metrics`
   - Display agent conversation logs and KPIs

### 🟢 Medium Priority (later)

7. **Add Redis session persistence** (US-12)
   - Store conversation state across sessions
   - Implement session restore on user return

8. **Implement benchmarking & cost tracking** (US-17, US-19)
   - Track API call costs per query
   - Benchmark agent accuracy/latency

9. **Add debate mode** (US-18)
   - Spawn two Analyst agents with opposing viewpoints
   - Let them debate and synthesize consensus

---

## Known Limitations & To-Do

| Item | Status | Impact | Notes |
|------|--------|--------|-------|
| AutoGen GroupChat wiring | ⏳ Pending | High | Config JSON ready; needs actual AutoGen runtime integration |
| Text2SQL LLM integration | ⏳ Pending | Medium | Keyword fallback works; LLM-powered SQL would be better |
| Chroma persistence reload | ⏳ Pending | Low | Indexes created fresh each run; can add auto-load |
| FastAPI admin dashboard | ⏳ Not started | Medium | Logs exported to JSON; UI not implemented |
| Redis memory caching | ⏳ Not started | Low | Architecture ready; Redis wiring needed |
| Debate mode (two analysts) | ⏳ Not started | Low | Prototype concept; needs orchestration |
| Cost tracking | ⏳ Not started | Low | Can instrument LLM calls; billing logic pending |

---

## Troubleshooting

### Issue: `faiss-cpu` fails to install on Apple Silicon (M1/M2)
**Solution**: Use conda or miniforge:
```bash
conda install -c conda-forge faiss-cpu
```

### Issue: Tests skip due to missing packages
**Expected behavior**: Tests gracefully skip when optional deps aren't installed. This is intentional. To enable all features:
```bash
pip install sentence-transformers numpy faiss-cpu chromadb
```

### Issue: `OPENAI_API_KEY not found` — LLM adapter returns stub responses
**Expected behavior**: System falls back to deterministic stubs. Set `OPENAI_API_KEY` in `.env` to enable real LLM calls.

### Issue: `groupchat_config.json` has empty system messages
**Solution**: Regenerate with:
```bash
python3 autogen_groupchat.py
```

---

## Code Examples for Next Developer

### 1. Running a query end-to-end
```python
from main import EnterpriseKnowledgeBase

kb = EnterpriseKnowledgeBase()
response = kb.process_query("What was Q3 revenue?")
print(response['final_answer'])
# Output: formatted answer with confidence, sources, caveats
```

### 2. Using Retriever directly
```python
from retriever_agent import RetrieverAgent

retriever = RetrieverAgent(
    db_path="knowledge_base.db",
    documents_path="./data/documents",
    vector_db_type="faiss"  # or 'chroma'
)

result = retriever.retrieve("What is company policy on expenses?", retrieval_type="hybrid")
print(f"Confidence: {result.confidence:.1%}")
print(f"Content: {result.content}")
```

### 3. Enabling real LLM calls
```python
from llm_adapter import LLMAdapter

adapter = LLMAdapter()
if adapter.is_configured():
    response = adapter.generate("Summarize this data: ...")
    print(response['text'])
else:
    print("No LLM API key configured; using stubs")
```

### 4. Saving/loading FAISS index
```python
retriever = RetrieverAgent(vector_db_type="faiss")
# ... index gets built on first use ...
retriever.save_faiss_index("./data/faiss_index")

# Later, in another process:
r2 = RetrieverAgent(vector_db_type="faiss")
r2.load_faiss_index("./data/faiss_index")
```

---

## Final Checklist for Handoff

- ✅ All core agents implemented (US-03 through US-07)
- ✅ LLM adapter added (safe fallback stubs)
- ✅ FAISS semantic retrieval working
- ✅ Chroma optional persistence layer
- ✅ Integration tests passing (no regressions)
- ✅ Semantic tests with graceful skip
- ✅ FAISS persistence save/load methods added
- ✅ Bootstrap script idempotent
- ✅ `.env.template` documented
- ✅ `groupchat_config.json` generated
- ✅ `docs/SETUP.md` with install steps
- ✅ Full pipeline test passing
- ✅ This HANDOFF.md document

---

## Contact & Questions

If you have questions about the codebase:
1. Check `docs/SETUP.md` for setup issues
2. Read agent docstrings in `retriever_agent.py`, `analyst_agent.py`, etc.
3. Review test files (`tests/test_pipeline.py`) for usage examples

---

**Hand-off Date**: 25 May 2026  
**Status**: ✅ Ready for Integration & Advanced Features  
**Next Phase**: AutoGen GroupChat wiring, Text2SQL, FastAPI dashboard

Good luck! 🚀
