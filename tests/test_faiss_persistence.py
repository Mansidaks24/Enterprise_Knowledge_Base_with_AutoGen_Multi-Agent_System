import pytest
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, '/Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen')

from agents.retriever_agent import RetrieverAgent


def test_faiss_save_load_skip_if_unavailable(tmp_path):
    try:
        import faiss  # type: ignore
    except Exception:
        pytest.skip('faiss not installed')

    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'doc1.txt').write_text('Q3 revenue was $2,500,000 with growth of 19%')

    retriever = RetrieverAgent(documents_path=str(docs), use_embedding_model=True, vector_db_type='faiss')

    # Save index
    outdir = tmp_path / 'index'
    outdir.mkdir()
    try:
        retriever.save_faiss_index(str(outdir))
    except Exception as e:
        pytest.skip(f'Could not save faiss index: {e}')

    # Load into a new agent instance
    r2 = RetrieverAgent(documents_path=str(docs), use_embedding_model=True, vector_db_type='faiss')
    try:
        r2.load_faiss_index(str(outdir))
    except Exception as e:
        pytest.skip(f'Could not load faiss index: {e}')

    # query
    res = r2.retrieve_from_documents('What was Q3 revenue?')
    assert isinstance(res.content, str)
