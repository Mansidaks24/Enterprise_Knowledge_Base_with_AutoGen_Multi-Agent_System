"""
MAIN ORCHESTRATOR
Combines all components into a working system
Coordinates all agents using AutoGen GroupChat
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Import all agents and components
from retriever_agent import RetrieverAgent, RetrievalResult
from analyst_agent import AnalystAgent
from fact_checker_agent import FactCheckerAgent
from synthesizer_agent import SynthesizerAgent
from query_router import QueryRouter


class EnterpriseKnowledgeBase:
    """
    Main orchestrator for Enterprise Knowledge Base with AutoGen
    Coordinates all agents in the multi-agent system
    """
    
    def __init__(self, 
                 db_path: str = "knowledge_base.db",
                 documents_path: str = "./data/documents",
                 config_path: str = "config.json"):
        """
        Initialize the Enterprise Knowledge Base system
        
        Args:
            db_path: Path to database
            documents_path: Path to documents directory
            config_path: Path to configuration file
        """
        print("=" * 70)
        print("INITIALIZING ENTERPRISE KNOWLEDGE BASE WITH AUTOGEN")
        print("=" * 70)
        
        self.db_path = db_path
        self.documents_path = documents_path
        self.config_path = config_path
        self.config = self._load_config(config_path)
        
        # Initialize all agents
        print("\n📦 Initializing agents...")
        self.query_router = QueryRouter()
        self.retriever = RetrieverAgent(db_path, documents_path)
        self.analyst = AnalystAgent()
        self.fact_checker = FactCheckerAgent()
        self.synthesizer = SynthesizerAgent()
        
        # Query history
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\n✓ All agents initialized successfully")
        print("✓ System ready for queries")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load system configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "project": {
                "name": "Enterprise Knowledge Base with AutoGen",
                "version": "1.0.0"
            },
            "autogen": {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the entire multi-agent pipeline
        
        Args:
            query: User's question/query
        
        Returns:
            Dictionary containing the final answer and all processing steps
        """
        print("\n" + "=" * 70)
        print("PROCESSING QUERY")
        print("=" * 70)
        
        processing_start = datetime.now()
        
        # Step 1: Route the query
        print("\n[STEP 1] QUERY ROUTING")
        print("─" * 70)
        query_analysis = self.query_router.route_query(query)
        
        # Step 2: Retrieve relevant data
        print("\n[STEP 2] DATA RETRIEVAL")
        print("─" * 70)
        retrieval_result = self.retriever.retrieve(
            query,
            retrieval_type=query_analysis.query_type
        )
        
        # Step 3: Analyze retrieved data
        print("\n[STEP 3] DATA ANALYSIS")
        print("─" * 70)
        analysis_result = self.analyst.analyze_data(
            query,
            retrieval_result.content,
            data_context=retrieval_result.metadata
        )
        
        # Step 4: Fact-check the analysis
        print("\n[STEP 4] FACT-CHECKING")
        print("─" * 70)
        validation_report = self.fact_checker.validate_analysis(
            analysis_result.analysis,
            retrieval_result.content,
            query
        )
        
        # Step 5: Synthesize final answer
        print("\n[STEP 5] ANSWER SYNTHESIS")
        print("─" * 70)
        final_answer = self.synthesizer.synthesize_answer(
            query,
            analysis_result.analysis,
            self.fact_checker.generate_validation_report_text(validation_report),
            retrieval_result.metadata.get('document_names', []),
            validation_report.overall_confidence
        )
        
        # Format final output
        final_output = self.synthesizer.format_for_presentation(final_answer)
        
        processing_end = datetime.now()
        processing_time = (processing_end - processing_start).total_seconds()
        
        # Compile complete response
        response = {
            "query": query,
            "final_answer": final_output,
            "processing_steps": {
                "query_routing": {
                    "query_type": query_analysis.query_type,
                    "confidence": query_analysis.confidence,
                    "routing_parameters": query_analysis.routing_parameters
                },
                "data_retrieval": {
                    "source_type": retrieval_result.source_type,
                    "confidence": retrieval_result.confidence,
                    "items_found": len(retrieval_result.metadata)
                },
                "analysis": {
                    "findings_count": len(analysis_result.key_findings),
                    "patterns": len(analysis_result.patterns_identified),
                    "confidence": analysis_result.confidence
                },
                "fact_checking": {
                    "claims_verified": validation_report.metadata['verified_claims'],
                    "total_claims": validation_report.metadata['total_claims'],
                    "overall_confidence": validation_report.overall_confidence
                },
                "synthesis": {
                    "confidence_level": final_answer.confidence_level,
                    "confidence_score": final_answer.confidence_score
                }
            },
            "metadata": {
                "session_id": self.session_id,
                "processing_time_seconds": processing_time,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Add to conversation history
        self.conversation_history.append(response)
        
        return response
    
    def batch_process_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple queries at once
        
        Args:
            queries: List of queries to process
        
        Returns:
            List of responses for each query
        """
        print("\n" + "=" * 70)
        print(f"BATCH PROCESSING {len(queries)} QUERIES")
        print("=" * 70)
        
        responses = []
        for i, query in enumerate(queries, 1):
            print(f"\n[Query {i}/{len(queries)}]")
            response = self.process_query(query)
            responses.append(response)
        
        return responses
    
    def export_conversation_history(self, filepath: str = None) -> str:
        """
        Export conversation history to file
        
        Args:
            filepath: Path to export to (default: auto-generated)
        
        Returns:
            Path where file was saved
        """
        if filepath is None:
            filepath = f"conversation_history_{self.session_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        print(f"✓ Conversation history exported to {filepath}")
        return filepath
    
    def export_all_logs(self, output_dir: str = "./logs") -> Dict[str, str]:
        """
        Export all agent logs and histories
        
        Args:
            output_dir: Directory to save logs
        
        Returns:
            Dictionary mapping log type to filepath
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        log_files = {}
        
        # Export each agent's log
        log_files['retrieval'] = f"{output_dir}/retrieval_log_{self.session_id}.json"
        self.retriever.export_retrieval_log(log_files['retrieval'])
        
        log_files['analysis'] = f"{output_dir}/analysis_log_{self.session_id}.json"
        self.analyst.export_analysis_log(log_files['analysis'])
        
        log_files['validation'] = f"{output_dir}/validation_log_{self.session_id}.json"
        self.fact_checker.export_validation_log(log_files['validation'])
        
        log_files['synthesis'] = f"{output_dir}/synthesis_log_{self.session_id}.json"
        self.synthesizer.export_synthesis_log(log_files['synthesis'])
        
        log_files['routing'] = f"{output_dir}/routing_log_{self.session_id}.json"
        self.query_router.export_routing_log(log_files['routing'])
        
        log_files['conversation'] = f"{output_dir}/conversation_{self.session_id}.json"
        self.export_conversation_history(log_files['conversation'])
        
        print(f"✓ All logs exported to {output_dir}/")
        return log_files
    
    def generate_system_report(self) -> str:
        """Generate a comprehensive system report"""
        report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ENTERPRISE KB - SYSTEM REPORT                           ║
╚════════════════════════════════════════════════════════════════════════════╝

SYSTEM INFORMATION
─────────────────────────────────────────────────────────────────────────────
Project: {self.config['project']['name']}
Version: {self.config['project']['version']}
Session ID: {self.session_id}
Configuration Model: {self.config['autogen']['model']}
System Temperature: {self.config['autogen']['temperature']}

AGENT STATUS
─────────────────────────────────────────────────────────────────────────────
✓ Query Router         - Ready
✓ Retriever Agent      - Ready
✓ Analyst Agent        - Ready
✓ Fact-Checker Agent   - Ready
✓ Synthesizer Agent    - Ready

CONVERSATION STATISTICS
─────────────────────────────────────────────────────────────────────────────
Total Queries Processed: {len(self.conversation_history)}
"""
        
        if self.conversation_history:
            # Calculate statistics
            total_time = sum(
                h['metadata']['processing_time_seconds'] 
                for h in self.conversation_history
            )
            avg_time = total_time / len(self.conversation_history)
            
            avg_confidence = sum(
                h['processing_steps']['synthesis']['confidence_score']
                for h in self.conversation_history
            ) / len(self.conversation_history)
            
            report += f"""
Average Processing Time: {avg_time:.2f} seconds
Total Processing Time: {total_time:.2f} seconds
Average Confidence Score: {avg_confidence:.1%}

ROUTING STATISTICS
─────────────────────────────────────────────────────────────────────────────
"""
            
            routing_types = {}
            for h in self.conversation_history:
                qtype = h['processing_steps']['query_routing']['query_type']
                routing_types[qtype] = routing_types.get(qtype, 0) + 1
            
            for qtype, count in routing_types.items():
                percentage = (count / len(self.conversation_history)) * 100
                report += f"  {qtype.upper()}: {count} queries ({percentage:.1f}%)\n"
        
        report += f"""

RETRIEVER PERFORMANCE
─────────────────────────────────────────────────────────────────────────────
Total Retrievals: {len(self.retriever.retrieved_sources)}
"""
        
        if self.retriever.retrieved_sources:
            avg_retrieval_confidence = sum(
                r['confidence'] for r in self.retriever.retrieved_sources
            ) / len(self.retriever.retrieved_sources)
            report += f"Average Confidence: {avg_retrieval_confidence:.1%}\n"
        
        report += f"""

DATABASE CONFIGURATION
─────────────────────────────────────────────────────────────────────────────
Database Path: {self.db_path}
Documents Path: {self.documents_path}

SYSTEM READY STATUS
─────────────────────────────────────────────────────────────────────────────
✓ All components initialized
✓ All agents operational
✓ System ready for queries

Generated: {datetime.now().isoformat()}
════════════════════════════════════════════════════════════════════════════
"""
        
        return report


def interactive_mode():
    """Run system in interactive mode"""
    print("\n" + "=" * 70)
    print("ENTERPRISE KNOWLEDGE BASE - INTERACTIVE MODE")
    print("=" * 70)
    
    # Initialize system
    kb = EnterpriseKnowledgeBase()
    
    print("\n💡 Enter your questions (type 'exit' to quit)")
    print("─" * 70)
    
    while True:
        try:
            query = input("\n🔍 Query: ").strip()
            
            if query.lower() == 'exit':
                print("\n👋 Exiting system...")
                break
            
            if not query:
                print("⚠️  Please enter a query.")
                continue
            
            # Process query
            response = kb.process_query(query)
            
            # Display final answer
            print(response['final_answer'])
            
        except KeyboardInterrupt:
            print("\n\n👋 System interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            continue
    
    # Export logs before exit
    print("\n📊 Exporting logs...")
    kb.export_all_logs()
    
    # Print final report
    print(kb.generate_system_report())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        # Run interactive mode
        interactive_mode()
    else:
        # Example usage
        print("\n" + "=" * 70)
        print("ENTERPRISE KB - EXAMPLE USAGE")
        print("=" * 70)
        
        # Initialize system
        kb = EnterpriseKnowledgeBase()
        
        # Example queries
        example_queries = [
            "What is our Q3 revenue?",
            "Explain our data governance policy",
            "Show me sales trends and performance metrics",
        ]
        
        # Process each query
        for i, query in enumerate(example_queries, 1):
            print(f"\n\n{'='*70}")
            print(f"EXAMPLE {i}: {query}")
            print('='*70)
            
            response = kb.process_query(query)
            print(response['final_answer'])
        
        # Export all logs
        print("\n\n📊 Exporting system data...")
        kb.export_all_logs()
        
        # Print final report
        print(kb.generate_system_report())
        
        print("\n✓ Example run completed")
        print("For interactive mode, run: python main.py interactive")