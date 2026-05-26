"""
autogen_simple.py - FIXED VERSION

SIMPLIFIED AUTOGEN IMPLEMENTATION
- Fixed synthesizer output issue
- Added proper content handling
- Better error recovery
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import our agents
from agents.llm_adapter import LLMAdapter
from agents.retriever_agent import RetrieverAgent
from agents.analyst_agent import AnalystAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.synthesizer_agent import SynthesizerAgent
from agents.query_router import QueryRouter

# Import memory and logging
from memory.memory_manager import MemoryManager
from monitoring.logger import SystemLogger


class SimpleAutoGenOrchestrator:
    """Multi-agent orchestration system"""

    def __init__(
        self,
        db_path: str = "knowledge_base.db",
        documents_path: str = "./data/documents",
        config_path: str = "config.json"
    ):
        """Initialize the orchestrator"""

        print("=" * 70)
        print("🤖 INITIALIZING AUTOGEN-STYLE MULTI-AGENT SYSTEM")
        print("=" * 70)

        self.db_path = db_path
        self.documents_path = documents_path
        self.config_path = config_path

        # Load config
        self.config = self._load_config(config_path)

        # Initialize memory and logging
        self.memory = MemoryManager()
        self.logger = SystemLogger()

        # Initialize LLM
        self.llm = LLMAdapter()
        print(f"\n✅ LLM Ready")
        print(f"   Provider: {self.llm.provider}")
        print(f"   Model: {self.llm.model}")

        # Initialize agents
        print("\n📦 Initializing agents...")
        self.retriever = RetrieverAgent(db_path, documents_path)
        self.analyst = AnalystAgent()
        self.fact_checker = FactCheckerAgent()
        self.synthesizer = SynthesizerAgent()
        self.query_router = QueryRouter()
        print("   ✅ All agents initialized")

        # Session management
        self.session_id = "autogen_" + datetime.now().strftime("%Y%m%d_%H%M%S")

        print("\n" + "=" * 70)
        print("✅ AUTOGEN ORCHESTRATOR READY")
        print("=" * 70)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def process_query_autogen(self, query: str) -> Dict[str, Any]:
        """Process query through multi-agent pipeline"""

        print("\n" + "=" * 70)
        print("🔍 AUTOGEN MULTI-AGENT PROCESSING")
        print("=" * 70)
        print(f"Query: {query}\n")

        result = {
            "query": query,
            "stages": {},
            "final_answer": ""
        }

        # STAGE 1: QUERY ROUTING
        print("📍 STAGE 1: Query Router")
        print("-" * 70)
        try:
            route = self.query_router.route_query(query)
            print(f"✅ Route: {route.query_type}\n")
            result["stages"]["routing"] = {
                "status": "success",
                "type": route.query_type,
                "confidence": route.confidence
            }
        except Exception as e:
            print(f"❌ Routing error: {e}\n")
            result["stages"]["routing"] = {"status": "error"}
            return result

        # STAGE 2: RETRIEVER AGENT
        print("📍 STAGE 2: Retriever Agent")
        print("-" * 70)
        try:
            retrieval = self.retriever.retrieve(query, retrieval_type="hybrid")
            retrieved_content = retrieval.content if hasattr(retrieval, 'content') else str(retrieval)
            print(f"✅ Retrieved content (confidence: {retrieval.confidence:.0%})\n")
            result["stages"]["retrieval"] = {
                "status": "success",
                "confidence": retrieval.confidence,
                "content": retrieved_content[:200]
            }
        except Exception as e:
            print(f"⚠️  Retrieval error: {e}\n")
            result["stages"]["retrieval"] = {"status": "error"}
            retrieval = None
            retrieved_content = ""

        # STAGE 3: ANALYST AGENT
        print("📍 STAGE 3: Analyst Agent")
        print("-" * 70)
        try:
            retrieved_data = retrieved_content if 'retrieved_content' in locals() else ""
            analysis = self.analyst.analyze_data(query, retrieved_data)
            analysis_text = analysis.analysis if hasattr(analysis, 'analysis') else str(analysis)
            print(f"✅ Analysis complete (confidence: {analysis.confidence if hasattr(analysis, 'confidence') else 'unknown'})\n")
            result["stages"]["analysis"] = {
                "status": "success",
                "findings": len(analysis.key_findings) if hasattr(analysis, 'key_findings') else 0
            }
        except Exception as e:
            print(f"⚠️  Analysis error: {e}\n")
            result["stages"]["analysis"] = {"status": "error"}
            analysis = None
            analysis_text = ""

        # STAGE 4: FACT CHECKER AGENT
        print("📍 STAGE 4: Fact Checker Agent")
        print("-" * 70)
        try:
            analysis_text = analysis_text if 'analysis_text' in locals() else ""
            retrieved_text = retrieved_content if 'retrieved_content' in locals() else ""
            
            verification = self.fact_checker.validate_analysis(
                analysis_text,
                retrieved_text,
                query
            )
            confidence = verification.overall_confidence if hasattr(verification, 'overall_confidence') else 0.5
            print(f"✅ Verification complete (confidence: {confidence:.0%})\n")
            result["stages"]["verification"] = {
                "status": "success",
                "confidence": confidence
            }
        except Exception as e:
            print(f"⚠️  Verification error: {e}\n")
            result["stages"]["verification"] = {"status": "error"}
            verification = None
            confidence = 0.5

        # STAGE 5: SYNTHESIZER AGENT
        print("📍 STAGE 5: Synthesizer Agent (Final Response)")
        print("-" * 70)
        try:
            analyst_findings = analysis_text if 'analysis_text' in locals() else ""
            fact_check_report = str(verification) if verification else ""
            source_citations = [query]  # Use query as citation if no real sources
            
            synthesis = self.synthesizer.synthesize_answer(
                query,
                analyst_findings,
                fact_check_report,
                source_citations,
                confidence
            )
            
            # Format the response
            if hasattr(synthesis, 'executive_summary'):
                final_response = self.synthesizer.format_for_presentation(synthesis)
            else:
                final_response = str(synthesis)
            
            print(f"✅ Response synthesized\n")
            result["stages"]["synthesis"] = {"status": "success"}
            result["final_answer"] = final_response
            
        except Exception as e:
            print(f"❌ Synthesis error: {e}\n")
            result["stages"]["synthesis"] = {"status": "error"}
            result["final_answer"] = f"Error: {str(e)}"

        print("=" * 70)
        print("✅ AUTOGEN PROCESSING COMPLETE")
        print("=" * 70)

        return result

    def display_result(self, result: Dict[str, Any]):
        """Display the processing result"""
        
        print("\n" + "=" * 70)
        print("📊 FINAL RESULT")
        print("=" * 70)

        print(f"\n🔍 Query: {result['query']}")
        
        print(f"\n✅ Pipeline Status:")
        stages = []
        for stage in ['routing', 'retrieval', 'analysis', 'verification', 'synthesis']:
            if stage in result['stages']:
                status = result['stages'][stage].get('status', 'unknown')
                stages.append(status[0].upper() if status else 'U')
        print(f"   {' → '.join(stages)}")

        print(f"\n" + "=" * 70)
        print("📖 FINAL ANSWER")
        print("=" * 70)
        
        answer = result.get('final_answer', 'No response generated')
        
        # Display answer (clean up formatting)
        if answer and answer != "No response generated":
            # Remove extra formatting
            answer = answer.replace('╔', '').replace('╗', '').replace('╚', '').replace('═', '─')
            answer = answer.replace('║', '│')
            print(answer)
        else:
            print("\n⚠️  No answer generated - ensure database is set up with sample data")
            print("\n💡 Fix: Run 'python setup_sample_data.py' to create sample database")
        
        print("\n" + "=" * 70 + "\n")

    def interactive_mode(self):
        """Start interactive query mode"""

        print("\n" + "=" * 70)
        print("🤖 AUTOGEN INTERACTIVE MODE")
        print("=" * 70)
        print("Ask me anything! Type 'exit' to quit.\n")

        while True:
            try:
                query = input("📝 Your Question: ").strip()

                if query.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using AutoGen! Goodbye!")
                    break

                if not query:
                    print("⚠️  Please enter a query\n")
                    continue

                # Process query
                result = self.process_query_autogen(query)
                self.display_result(result)
                print()

            except KeyboardInterrupt:
                print("\n\n👋 Session ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Create orchestrator
    print("\n🚀 Starting AutoGen Multi-Agent System...\n")
    orchestrator = SimpleAutoGenOrchestrator()

    # Test queries
    test_queries = [
        "What is machine learning?",
        "Explain artificial intelligence",
    ]

    print("\n" + "=" * 70)
    print("🧪 RUNNING TEST QUERIES")
    print("=" * 70)

    for query in test_queries:
        result = orchestrator.process_query_autogen(query)
        orchestrator.display_result(result)
        print("\n" + "-" * 70)

    # Start interactive mode
    print("\n\nStarting interactive mode...")
    orchestrator.interactive_mode()