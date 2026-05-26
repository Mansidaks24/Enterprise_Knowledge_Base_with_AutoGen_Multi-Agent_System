"""
US-03: RETRIEVER AGENT
Build retriever agent for document and database retrieval
Handles both SQL queries (structured data) and RAG searches (unstructured documents)
"""

import os
import json
from typing import Dict, List, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from agents.text2sql_agent import Text2SQLAgent
from monitoring.logger import SystemLogger
from sentence_transformers import SentenceTransformer

try:
    from langchain_community.sql_database import SQLDatabase
    from langchain_community.utilities import SQLDatabaseChain
    from langchain.agents import Tool
except ImportError:
    print("Warning: Some dependencies not installed. Install with: pip install -r requirements.txt")

try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False


try:
    import chromadb
    CHROMA_AVAILABLE = True
except Exception:
    chromadb = None
    CHROMA_AVAILABLE = False


@dataclass
class RetrievalResult:
    """Structure for retrieval results"""
    source_type: str  # "database", "document", "hybrid"
    content: str
    source_reference: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    timestamp: str


class RetrieverAgent:
    """
    US-03: Retriever Agent
    Retrieves relevant information from databases and documents
    """
    
    def __init__(self, 
                 db_path: str = None,
                 documents_path: str = None,
                 use_embedding_model: bool = True,
                 vector_index_path: str = None,
                 vector_db_type: str = None):
        """
        Initialize the Retriever Agent
        
        Args:
            db_path: Path to SQLite database
            documents_path: Path to documents directory
            use_embedding_model: Whether to use sentence transformers for embeddings
        """
        self.db_path = db_path or "knowledge_base.db"
        self.documents_path = documents_path or "./data/documents"
        self.retrieved_sources = []
        self.text2sql_agent = Text2SQLAgent(
            self.db_path
        )
        
        # Initialize embedding model if available and FAISS enabled
        self.embedding_model = None
        if use_embedding_model and FAISS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Note: Embedding model not available: {e}. Using keyword search.")
        elif use_embedding_model and not FAISS_AVAILABLE:
            print("Note: FAISS not available in environment; semantic search disabled.")
        
        # Initialize document index
        self.document_index = self._build_document_index()

        # Vector DB type: 'faiss' or 'chroma'
        self.vector_db_type = (vector_db_type or os.environ.get('VECTOR_DB_TYPE', 'faiss')).lower()
        self.vector_index = None
        self.vector_docs = None
        self.chroma_collection = None

        # Initialize FAISS if available
        if self.vector_db_type == 'faiss' and FAISS_AVAILABLE and self.embedding_model:
            try:
                self.vector_index, self.vector_docs = self._build_faiss_index()
            except Exception as e:
                print(f"Warning: Failed to build FAISS index: {e}")

        # Initialize Chroma if requested
        if self.vector_db_type == 'chroma' and CHROMA_AVAILABLE and self.embedding_model:
            try:
                # attempt to index documents into chroma collection
                self._index_documents_chroma()
            except Exception as e:
                print(f"Warning: Failed to initialize Chroma index: {e}")

        print("✓ Retriever Agent initialized")
    
    def _build_document_index(self) -> Dict[str, str]:
        """Build an index of documents for faster retrieval"""
        index = {}
        documents_dir = Path(self.documents_path)
        
        if documents_dir.exists():
            for doc_file in documents_dir.glob("*.*"):
                try:
                    if doc_file.suffix.lower() == ".txt":
                        with open(doc_file, 'r') as f:
                            index[doc_file.name] = f.read()
                    elif doc_file.suffix.lower() == ".json":
                        with open(doc_file, 'r') as f:
                            index[doc_file.name] = json.dumps(json.load(f), indent=2)
                except Exception as e:
                    print(f"Error indexing {doc_file}: {e}")
        
        return index

    def _build_faiss_index(self):
        """Build a simple FAISS index from document index. Returns (index, docs_list).

        docs_list is a list of tuples (doc_name, excerpt)
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")

        docs = []
        embeddings = []
        for name, content in self.document_index.items():
            for para in content.split('\n\n'):
                para = para.strip()
                if not para:
                    continue
                docs.append((name, para[:1000]))
                emb = self.embedding_model.encode(para)
                embeddings.append(emb)

        import numpy as np
        if not embeddings:
            raise RuntimeError("No document embeddings created")

        emb_matrix = np.vstack(embeddings).astype('float32')
        d = emb_matrix.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(emb_matrix)

        return index, docs

    def save_faiss_index(self, path: str):
        """Save FAISS index and metadata to the given path"""
        if not FAISS_AVAILABLE or not hasattr(self, 'vector_index') or self.vector_index is None:
            raise RuntimeError("FAISS index not available to save")
        import os
        os.makedirs(path, exist_ok=True)
        # save index
        faiss.write_index(self.vector_index, f"{path}/index.faiss")
        # save docs
        import json
        with open(f"{path}/docs.json", 'w') as f:
            json.dump(self.vector_docs, f)

    def load_faiss_index(self, path: str):
        """Load FAISS index and metadata from the given path"""
        import os, json
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not installed")
        idx_file = f"{path}/index.faiss"
        docs_file = f"{path}/docs.json"
        if not os.path.exists(idx_file) or not os.path.exists(docs_file):
            raise FileNotFoundError("Index or docs not found")
        index = faiss.read_index(idx_file)
        with open(docs_file, 'r') as f:
            docs = json.load(f)
        self.vector_index = index
        self.vector_docs = docs


    def _index_documents_chroma(self):
        """Index documents into a Chroma collection (local persistence)."""
        if not CHROMA_AVAILABLE or not self.embedding_model:
            raise RuntimeError("Chroma or embedding model not available")

        # Prepare small items
        ids = []
        metadatas = []
        documents = []
        for i, (name, content) in enumerate(self.document_index.items()):
            ids.append(str(i))
            metadatas.append({"doc": name})
            documents.append(content)

        try:
            from chromadb.utils import embedding_functions
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            # Create or get collection
            client = chromadb.Client()
            try:
                collection = client.get_collection(name="enterprise_kb")
            except Exception:
                collection = client.create_collection(name="enterprise_kb", embedding_function=ef)

            # upsert docs
            collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            self.chroma_collection = collection
        except Exception as e:
            print(f"Chroma indexing failed: {e}")
    
    def retrieve_from_database(self, query: str) -> RetrievalResult:
        """
        Execute SQL query on the knowledge base
        
        Args:
            query: SQL query or natural language query to execute
        
        Returns:
            RetrievalResult with database data
        """
        try:
            conn = sqlite3.connect(self.db_path)

            cursor = conn.cursor()

            # -----------------------------------
            # Detect Raw SQL vs Natural Language
            # -----------------------------------

            sql_keywords = [
                "select",
                "insert",
                "update",
                "delete",
                "create",
                "drop"
            ]

            is_raw_sql = any(
                query.lower().strip().startswith(keyword)
                for keyword in sql_keywords
            )

            # -----------------------------------
            # RAW SQL QUERY
            # -----------------------------------

            if is_raw_sql:

                sql_query = query

            # -----------------------------------
            # NATURAL LANGUAGE → SQL
            # -----------------------------------

            else:

                print(" Generating SQL from natural language...")

                generated = self.text2sql_agent.process_query(
                    query
                )

                sql_query = generated["generated_sql"]

                print(f"   ✓ Generated SQL: {sql_query}")

            # -----------------------------------
            # EXECUTE SQL
            # -----------------------------------

            cursor.execute(sql_query)

            columns = [
                description[0]
                for description in cursor.description
            ]

            rows = cursor.fetchall()

            if rows:

                result_text = "Retrieved from database:\n\n"

                for row in rows:

                    result_text += (
                        str(dict(zip(columns, row)))
                        + "\n"
                    )
                conn.close()
                return RetrievalResult(

                    source_type="database",

                    content=result_text,

                    source_reference=sql_query,

                    confidence=0.95,

                    metadata={
                        "rows": len(rows),
                        "columns": columns,
                        "generated_sql": sql_query
                    },

                    timestamp=datetime.now().isoformat()
                )

            else:

                return RetrievalResult(

                    source_type="database",

                    content="No data found for query",

                    source_reference=sql_query,

                    confidence=0.5,

                    metadata={
                        "rows": 0,
                        "generated_sql": sql_query
                    },

                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:

            print(f"Database retrieval error: {e}")

            return RetrievalResult(

                source_type="database",

                content=f"Error retrieving from database: {str(e)}",

                source_reference="Database Error",

                confidence=0.0,

                metadata={"error": str(e)},

                timestamp=datetime.now().isoformat()
            )
    
    def _keyword_search_database(self, query: str) -> RetrievalResult:
        """Keyword-based database search as fallback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            results = []
            query_lower = query.lower()
            
            for table_name in tables:
                table = table_name[0]
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Simple keyword matching
                for row in rows:
                    if any(query_lower in str(cell).lower() for cell in row):
                        results.append(dict(zip([desc[0] for desc in cursor.description], row)))
            
            conn.close()
            
            if results:
                return RetrievalResult(
                    source_type="database",
                    content=json.dumps(results, indent=2),
                    source_reference=f"Keyword search: {query}",
                    confidence=0.7,
                    metadata={"results": len(results)},
                    timestamp=datetime.now().isoformat()
                )
            else:
                return RetrievalResult(
                    source_type="database",
                    content="No matching data found",
                    source_reference=f"Keyword search: {query}",
                    confidence=0.3,
                    metadata={"results": 0},
                    timestamp=datetime.now().isoformat()
                )
        
        except Exception as e:
            print(f"Keyword search error: {e}")
            return RetrievalResult(
                source_type="database",
                content="Database search failed",
                source_reference="Database Error",
                confidence=0.0,
                metadata={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    def retrieve_from_documents(self, query: str) -> RetrievalResult:
        """
        Search unstructured documents using RAG approach
        
        Args:
            query: Query string to search documents
        
        Returns:
            RetrievalResult with document excerpts
        """
        if not self.document_index:
            return RetrievalResult(
                source_type="document",
                content="No documents available",
                source_reference="Document Search",
                confidence=0.0,
                metadata={"documents": 0},
                timestamp=datetime.now().isoformat()
            )
        
        # If FAISS is available and index can be built, attempt semantic search
        matching_docs = []
        # First, if Chroma is requested and available, use it
        if getattr(self, 'vector_db_type', 'faiss') == 'chroma' and getattr(self, 'chroma_collection', None) is not None:
            try:
                # Chroma collections typically accept query_texts and return documents/metadatas
                results = self.chroma_collection.query(query_texts=[query], n_results=5, include=['documents', 'metadatas', 'distances'])
                # results format may vary by chromadb version
                docs = results.get('documents', []) if isinstance(results, dict) else None
                if docs:
                    for docs_for_q in docs:
                        for doc_text in docs_for_q:
                            matching_docs.append({"document": "chroma_result", "excerpts": [doc_text]})
            except Exception as e:
                print(f"Chroma query failed: {e}. Falling back to other retrieval methods.")

        if not matching_docs and FAISS_AVAILABLE and self.embedding_model:
            try:
                # build index lazily
                if not hasattr(self, 'vector_index') or self.vector_index is None:
                    try:
                        self.vector_index, self.vector_docs = self._build_faiss_index()
                    except Exception as e:
                        print(f"Could not build FAISS index: {e}")

                if hasattr(self, 'vector_index') and self.vector_index is not None:
                    q_emb = self.embedding_model.encode([query]).astype('float32')
                    D, I = self.vector_index.search(q_emb, 5)
                    for idx_list in I:
                        for i in idx_list:
                            if i < len(self.vector_docs):
                                doc_name, excerpt = self.vector_docs[i]
                                matching_docs.append({"document": doc_name, "excerpts": [excerpt]})
            except Exception as e:
                print(f"FAISS semantic search failed: {e}. Falling back to keyword search.")

        # Fallback simple text matching approach
        if not matching_docs:
            query_lower = query.lower()
            for doc_name, doc_content in self.document_index.items():
                # Check if query terms appear in document
                if any(term in doc_content.lower() for term in query_lower.split()):
                    # Extract relevant excerpts
                    lines = doc_content.split('\n')
                    relevant_lines = [
                        line for line in lines 
                        if any(term in line.lower() for term in query_lower.split())
                    ]
                    
                    if relevant_lines:
                        matching_docs.append({
                            "document": doc_name,
                            "excerpts": relevant_lines[:3]  # Top 3 matching excerpts
                        })
        
        if matching_docs:
            result_text = "Retrieved from documents:\n"
            for match in matching_docs:
                result_text += f"\n📄 {match['document']}:\n"
                for excerpt in match['excerpts']:
                    result_text += f"  - {excerpt[:100]}...\n"
            
            return RetrievalResult(
                source_type="document",
                content=result_text,
                source_reference=f"Document search: {query}",
                confidence=0.8,
                metadata={
                    "documents_found": len(matching_docs),
                    "document_names": [d['document'] for d in matching_docs]
                },
                timestamp=datetime.now().isoformat()
            )
        
        return RetrievalResult(
            source_type="document",
            content="No relevant documents found",
            source_reference=f"Document search: {query}",
            confidence=0.4,
            metadata={"documents_found": 0},
            timestamp=datetime.now().isoformat()
        )
    
    def retrieve_hybrid(self, query: str) -> RetrievalResult:
        """
        Perform hybrid retrieval (both SQL + RAG)
        
        Args:
            query: Query to search across all sources
        
        Returns:
            Combined RetrievalResult from both sources
        """
        # Get both database and document results
        db_result = self.retrieve_from_database(query)
        doc_result = self.retrieve_from_documents(query)
        
        # Combine results
        combined_content = f"""
HYBRID RETRIEVAL RESULTS
════════════════════════════════════════════════════════════════

DATABASE RESULTS:
─────────────────
{db_result.content}

DOCUMENT RESULTS:
─────────────────
{doc_result.content}

RETRIEVAL SUMMARY:
─────────────────
Database Confidence: {db_result.confidence}
Document Confidence: {doc_result.confidence}
Average Confidence: {(db_result.confidence + doc_result.confidence) / 2:.2f}
"""
        
        return RetrievalResult(
            source_type="hybrid",
            content=combined_content,
            source_reference=f"Hybrid search: Database + Documents",
            confidence=(db_result.confidence + doc_result.confidence) / 2,
            metadata={
                "db_confidence": db_result.confidence,
                "doc_confidence": doc_result.confidence,
                "db_results": db_result.metadata,
                "doc_results": doc_result.metadata
            },
            timestamp=datetime.now().isoformat()
        )
    
    def retrieve(self, 
                 query: str, 
                 retrieval_type: str = "hybrid") -> RetrievalResult:
        """
        Main retrieval method - unified interface
        
        Args:
            query: Query string
            retrieval_type: "database", "document", or "hybrid"
        
        Returns:
            RetrievalResult object
        """
        print(f"\n🔍 Retriever Agent - Searching {retrieval_type}")
        SystemLogger.info(
            f"Retriever searching: {query}"
        )
        print(f"   Query: {query[:100]}...")
        
        if retrieval_type == "database":
            result = self.retrieve_from_database(query)
        elif retrieval_type == "document":
            result = self.retrieve_from_documents(query)
        else:  # hybrid
            result = self.retrieve_hybrid(query)
        
        # Log retrieval
        self.retrieved_sources.append({
            "query": query,
            "type": retrieval_type,
            "result_type": result.source_type,
            "confidence": result.confidence,
            "timestamp": result.timestamp
        })
        
        print(f"   ✓ Retrieved {result.source_type} ({result.confidence:.1%} confidence)")
        
        return result
    
    def get_agent_system_message(self) -> str:
        """Return the system message for this agent in AutoGen"""
        return """You are a Retriever Agent specialized in finding information from databases and documents.

Your responsibilities:
1. Parse queries to understand information needs
2. Search both structured databases (SQL) and unstructured documents (RAG)
3. Return relevant data with proper citations
4. Always specify source and confidence level

When responding, format as:
- Source Type: [Database/Document/Hybrid]
- Content: [Retrieved data]
- Reference: [Where it came from]
- Confidence: [High/Medium/Low]"""
    
    def export_retrieval_log(self, filepath: str = "retrieval_log.json"):
        """Export retrieval history for monitoring"""
        with open(filepath, 'w') as f:
            json.dump(self.retrieved_sources, f, indent=2)
        print(f"✓ Retrieval log exported to {filepath}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("US-03: RETRIEVER AGENT - TESTING")
    print("=" * 70)
    
    # Initialize agent
    retriever = RetrieverAgent(
        db_path="knowledge_base.db",
        documents_path="./data/documents"
    )
    
    # Test queries
    test_queries = [
        ("SELECT * FROM employees LIMIT 5", "database"),
        ("What are the company policies?", "document"),
        ("Show me sales data and revenue trends", "hybrid"),
    ]
    
    print("\nRunning retrieval tests...\n")
    
    for query, retrieval_type in test_queries:
        result = retriever.retrieve(query, retrieval_type)
        
        print(f"\nQuery: {query}")
        print(f"Type: {result.source_type}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Content preview: {result.content[:200]}...")
        print("-" * 70)
    
    # Export log
    retriever.export_retrieval_log()
    
    print("\n✓ Retriever Agent testing completed")