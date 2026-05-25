import os
import sys
import sqlite3
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from retriever_agent import RetrieverAgent, RetrievalResult
from analyst_agent import AnalystAgent
from fact_checker_agent import FactCheckerAgent
from synthesizer_agent import SynthesizerAgent
from query_router import QueryRouter


def setup_sample_db(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary INTEGER)")
    cur.execute("DELETE FROM employees")
    cur.executemany("INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)", [
        ("Alice", "engineering", 120000),
        ("Bob", "sales", 90000),
        ("Carol", "support", 70000),
    ])
    conn.commit()
    conn.close()


def test_pipeline_happy_path(tmp_path):
    # Create a temp sqlite db
    db_path = tmp_path / "test_kb.db"
    setup_sample_db(str(db_path))

    # Create sample document directory
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    doc_file = docs_dir / "policy.txt"
    doc_file.write_text("Company policy: All employees must submit expense reports monthly.")

    # Initialize components
    router = QueryRouter()
    retriever = RetrieverAgent(db_path=str(db_path), documents_path=str(docs_dir), use_embedding_model=False)
    analyst = AnalystAgent()
    fact_checker = FactCheckerAgent()
    synthesizer = SynthesizerAgent()

    # Run a sample query expected to hit both DB and docs
    query = "What is the salary of employees and company expense policy?"

    # Route query
    analysis = router.route_query(query)
    assert analysis.query_type in ("hybrid", "sql", "rag")

    # Retrieve
    retrieval = retriever.retrieve(query, retrieval_type=analysis.query_type)
    assert isinstance(retrieval, RetrievalResult)

    # Analyze
    analysis_result = analyst.analyze_data(query, retrieval.content, data_context=retrieval.metadata)
    assert analysis_result.confidence >= 0.0

    # Fact-check
    validation = fact_checker.validate_analysis(analysis_result.analysis, retrieval.content, original_query=query)
    assert validation.overall_confidence >= 0.0

    # Synthesize
    final_answer = synthesizer.synthesize_answer(query, analysis_result.analysis, fact_checker.generate_validation_report_text(validation), retrieval.metadata.get('document_names', []), validation.overall_confidence)
    formatted = synthesizer.format_for_presentation(final_answer)
    assert "FINAL ANSWER REPORT" in formatted or "EXECUTIVE SUMMARY" in formatted
