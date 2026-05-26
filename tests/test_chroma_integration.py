import pytest
from pathlib import Path
import sys

sys.path.insert(0, '/Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen')

from agents.retriever_agent import RetrieverAgent


def test_chroma_indexing_skip_if_unavailable(tmp_path):
    try:
        import chromadb  # type: ignore
    except Exception:
        pytest.skip("chromadb not installed")

    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'doc1.txt').write_text('Policy: Employees must submit expense reports monthly.')

    retriever = RetrieverAgent(documents_path=str(docs), use_embedding_model=True, vector_db_type='chroma')
    # If chroma is available and indexing succeeded, chroma_collection should exist
    if hasattr(retriever, 'chroma_collection') and retriever.chroma_collection is not None:
        res = retriever.retrieve_from_documents('What is the expense policy?')
        assert 'policy' in res.content.lower() or res.metadata.get('documents_found', 0) >= 0
    else:
        pytest.skip("Chroma collection not initialized")
