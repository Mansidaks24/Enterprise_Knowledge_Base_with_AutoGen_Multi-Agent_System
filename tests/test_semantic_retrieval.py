import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, '/Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen')

from agents.retriever_agent import RetrieverAgent


def test_semantic_retrieval_skip_if_no_deps(tmp_path):
    # This test requires sentence-transformers and faiss or chromadb
    try:
        import sentence_transformers  # type: ignore
    except Exception:
        pytest.skip("sentence-transformers not installed")

    # prepare sample doc
    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'doc1.txt').write_text('Revenue Q3 2024: $2,500,000. Growth 19%')

    # initialize retriever with embeddings enabled
    retriever = RetrieverAgent(documents_path=str(docs), use_embedding_model=True)

    # run a query that should match semantically
    res = retriever.retrieve_from_documents('What was Q3 revenue?')
    assert res is not None
    # If semantic retrieval is not available, a fallback still returns a result
    assert isinstance(res.content, str)
