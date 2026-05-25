Setup and Quickstart

1) Create and activate venv

   python3 -m venv .venv
   source .venv/bin/activate

2) Bootstrap (minimal dev deps)

   bash ./scripts/bootstrap.sh

3) Install semantic and vector packages (optional but recommended)

   pip install sentence-transformers numpy faiss-cpu

4) Install chromadb (optional persistence)

   pip install chromadb

5) Optional: install OpenAI SDK to enable real LLM calls

   pip install openai

6) Run tests

   pytest -q

Notes:
- On Apple Silicon (M1/M2) you may need conda/miniforge to install faiss-cpu.
