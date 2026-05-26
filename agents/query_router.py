"""
US-07: HYBRID SQL + RAG QUERY ROUTER
Build query router for structured and unstructured data
Automatic query type detection and routing
"""

import json
from typing import Dict, Tuple, List, Any
from dataclasses import dataclass
from datetime import datetime
from monitoring.agent_conversations import AgentConversationLogger

@dataclass
class QueryAnalysis:
    """Structure for query routing analysis"""
    original_query: str
    query_type: str  # "sql", "rag", "hybrid"
    confidence: float  # 0.0 to 1.0
    sql_confidence: float
    rag_confidence: float
    keywords: List[str]
    detected_entities: List[str]
    recommendation: str
    routing_parameters: Dict[str, Any]
    timestamp: str


class QueryRouter:
    """
    US-07: Query Router
    Routes queries to appropriate retrieval method (SQL, RAG, or Hybrid)
    Implements automatic query type detection
    """
    
    def __init__(self):
        """Initialize the Query Router"""
        self.routing_history = []
        self.keyword_mappings = self._load_keyword_mappings()
        print("✓ Query Router initialized")
    
    def _load_keyword_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Load keywords for query classification"""
        return {
            "sql_keywords": {
                "structured": [
                    "table", "database", "row", "column", "data",
                    "record", "count", "sum", "total", "employee",
                    "customer", "product", "sales", "revenue", "filter",
                    "where", "group", "order", "aggregate"
                ],
                "temporal": [
                    "year", "quarter", "month", "week", "day",
                    "date", "time", "period", "fiscal", "q1", "q2", "q3", "q4"
                ],
                "numerical": [
                    "number", "amount", "price", "cost", "value",
                    "percentage", "rate", "average", "median", "total"
                ]
            },
            "rag_keywords": {
                "document": [
                    "document", "file", "policy", "procedure", "guideline",
                    "manual", "handbook", "instruction", "article", "report",
                    "email", "memo", "note", "page", "section", "chapter"
                ],
                "semantic": [
                    "explain", "describe", "understand", "what", "how",
                    "why", "when", "where", "reason", "cause", "effect",
                    "context", "background", "summary", "overview"
                ],
                "unstructured": [
                    "text", "content", "information", "knowledge",
                    "reference", "definition", "concept", "idea", "detail"
                ]
            }
        }
    
    def route_query(self, query: str) -> QueryAnalysis:
        """
        Main routing method - analyzes and routes query
        
        Args:
            query: User's query string
        
        Returns:
            QueryAnalysis with routing decision
        """
        print(f"\n🔀 Query Router - Analyzing query")
        print(f"   Query: {query[:100]}...")
        
        # Extract keywords
        keywords = self._extract_keywords(query)
        
        # Calculate SQL confidence
        sql_confidence = self._calculate_sql_confidence(query, keywords)
        
        # Calculate RAG confidence
        rag_confidence = self._calculate_rag_confidence(query, keywords)
        
        # Determine query type
        query_type = self._determine_query_type(sql_confidence, rag_confidence)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Generate recommendation
        recommendation = self._generate_routing_recommendation(
            query_type,
            sql_confidence,
            rag_confidence
        )
        
        # Set routing parameters
        routing_parameters = self._set_routing_parameters(
            query_type,
            sql_confidence,
            rag_confidence,
            entities
        )
        
        # Calculate overall confidence
        overall_confidence = max(sql_confidence, rag_confidence)
        if query_type == "hybrid":
            overall_confidence = (sql_confidence + rag_confidence) / 2
        
        analysis = QueryAnalysis(
            original_query=query,
            query_type=query_type,
            confidence=overall_confidence,
            sql_confidence=sql_confidence,
            rag_confidence=rag_confidence,
            keywords=keywords,
            detected_entities=entities,
            recommendation=recommendation,
            routing_parameters=routing_parameters,
            timestamp=datetime.now().isoformat()
        )
        
        # Log routing
        self.routing_history.append({
            "query": query[:100],
            "routed_to": query_type,
            "confidence": overall_confidence,
            "timestamp": analysis.timestamp
        })
        
        print(f"   ✓ Routed to: {query_type.upper()} ({overall_confidence:.1%} confidence)")
        AgentConversationLogger.log(
        "Query Router",
        f"""
        Query classified as {query_type.upper()}

        SQL Confidence:
        {sql_confidence:.1%}

        RAG Confidence:
        {rag_confidence:.1%}

        Final Routing Confidence:
        {overall_confidence:.1%}
        """
        )
        
        return analysis
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        query_lower = query.lower()
        keywords = []
        
        # Extract all keywords from mappings
        for keyword_type, categories in self.keyword_mappings.items():
            for category, words in categories.items():
                for word in words:
                    if word in query_lower:
                        keywords.append(word)
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_sql_confidence(self, query: str, keywords: List[str]) -> float:
        """Calculate confidence for SQL query type"""
        confidence = 0.3  # Base confidence
        query_lower = query.lower()
        
        # Check for structured/SQL keywords
        sql_keywords = self.keyword_mappings["sql_keywords"]
        sql_keyword_count = sum(
            1 for word in keywords 
            if word in sql_keywords["structured"] or 
               word in sql_keywords["temporal"] or
               word in sql_keywords["numerical"]
        )
        
        confidence += sql_keyword_count * 0.1
        
        # Check for query patterns suggesting SQL
        if any(char in query for char in ["*", "<", ">", "=", "!"]):
            confidence += 0.15  # Comparison operators suggest SQL
        
        if any(word in query_lower for word in ["group by", "order by", "where", "filter", "aggregate"]):
            confidence += 0.2
        
        # Check for temporal/numerical patterns
        import re
        if re.search(r'\d{4}|q[1-4]|january|february|march', query_lower):
            confidence += 0.1  # Date patterns
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def _calculate_rag_confidence(self, query: str, keywords: List[str]) -> float:
        """Calculate confidence for RAG query type"""
        confidence = 0.2  # Base confidence
        query_lower = query.lower()
        
        # Check for document/semantic keywords
        rag_keywords = self.keyword_mappings["rag_keywords"]
        rag_keyword_count = sum(
            1 for word in keywords 
            if word in rag_keywords["document"] or 
               word in rag_keywords["semantic"] or
               word in rag_keywords["unstructured"]
        )
        
        confidence += rag_keyword_count * 0.15
        
        # Check for semantic question patterns
        question_words = ["what", "how", "why", "when", "where", "who"]
        question_count = sum(1 for word in question_words if word in query_lower)
        confidence += question_count * 0.12
        
        # Check for explanation/understanding indicators
        if any(word in query_lower for word in ["explain", "describe", "understand", "summarize"]):
            confidence += 0.2
        
        # Check for reference/policy indicators
        if any(word in query_lower for word in ["policy", "procedure", "guideline", "process"]):
            confidence += 0.15
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def _determine_query_type(self, 
                             sql_confidence: float,
                             rag_confidence: float) -> str:
        """Determine the query type based on confidence scores"""
        confidence_diff = abs(sql_confidence - rag_confidence)
        
        # If confidence scores are very close, use hybrid
        if confidence_diff < 0.15:
            return "hybrid"
        
        # Otherwise use the higher confidence type
        if sql_confidence > rag_confidence:
            return "sql"
        else:
            return "rag"
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract business entities from query"""
        entities = []
        query_lower = query.lower()
        
        # Common business entities
        entity_keywords = {
            "department": ["engineering", "sales", "support", "hr", "marketing", "operations"],
            "time_period": ["q1", "q2", "q3", "q4", "january", "february", "march", "quarter", "year"],
            "metric": ["revenue", "profit", "cost", "salary", "count", "growth", "percentage"],
            "object": ["employee", "customer", "product", "department", "project", "team"]
        }
        
        for entity_type, keywords in entity_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    entities.append(f"{entity_type}:{keyword}")
        
        return list(set(entities))  # Remove duplicates
    
    def _generate_routing_recommendation(self,
                                        query_type: str,
                                        sql_confidence: float,
                                        rag_confidence: float) -> str:
        """Generate routing recommendation and instructions"""
        recommendation = f"Route to {query_type.upper()} retrieval.\n"
        
        if query_type == "sql":
            recommendation += f"SQL Confidence: {sql_confidence:.1%}\n"
            recommendation += "Execute structured database query.\n"
            recommendation += "Use SQL Agent for table queries."
        
        elif query_type == "rag":
            recommendation += f"RAG Confidence: {rag_confidence:.1%}\n"
            recommendation += "Perform semantic document search.\n"
            recommendation += "Search documents using embeddings."
        
        else:  # hybrid
            recommendation += f"Hybrid Query (SQL: {sql_confidence:.1%}, RAG: {rag_confidence:.1%})\n"
            recommendation += "Execute BOTH SQL and RAG searches.\n"
            recommendation += "Combine results from both sources."
        
        return recommendation
    
    def _set_routing_parameters(self,
                               query_type: str,
                               sql_confidence: float,
                               rag_confidence: float,
                               entities: List[str]) -> Dict[str, Any]:
        """Set specific parameters for query routing"""
        parameters = {
            "retrieval_type": query_type,
            "sql_enabled": query_type in ["sql", "hybrid"],
            "rag_enabled": query_type in ["rag", "hybrid"],
            "sql_confidence": sql_confidence,
            "rag_confidence": rag_confidence,
            "entities": entities,
            "use_caching": True,
            "timeout_seconds": 30,
        }
        
        # Adjust parameters based on query type
        if query_type == "sql":
            parameters["max_sql_results"] = 1000
            parameters["rag_threshold"] = 0.0  # Disable RAG
        elif query_type == "rag":
            parameters["max_documents"] = 10
            parameters["rag_threshold"] = 0.6
            parameters["sql_enabled"] = False
        else:  # hybrid
            parameters["max_sql_results"] = 500
            parameters["max_documents"] = 5
            parameters["rag_threshold"] = 0.5
            parameters["combine_results"] = True
        
        return parameters
    
    def classify_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Simplified interface - just returns query type and parameters
        
        Args:
            query: User query
        
        Returns:
            Tuple of (query_type, routing_parameters)
        """
        analysis = self.route_query(query)
        return analysis.query_type, analysis.routing_parameters
    
    def get_router_system_message(self) -> str:
        """Return system message for router"""
        return """You are a Query Router responsible for classifying user queries.

Your job:
1. Analyze the user's query
2. Determine if it requires:
   - SQL query (structured data from databases)
   - RAG search (semantic search on documents)
   - HYBRID (both SQL and RAG)
3. Route to appropriate retrieval method

Consider:
- Keywords (database, policy, document, etc.)
- Question type (what, how, why)
- Time/numerical requirements
- Entity types mentioned

Output routing decision and parameters."""
    
    def export_routing_log(self, filepath: str = "routing_log.json"):
        """Export routing history for monitoring"""
        with open(filepath, 'w') as f:
            json.dump(self.routing_history, f, indent=2)
        print(f"✓ Routing log exported to {filepath}")
    
    def generate_routing_report(self, analysis: QueryAnalysis) -> str:
        """Generate human-readable routing report"""
        report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                          QUERY ROUTING ANALYSIS                            ║
╚════════════════════════════════════════════════════════════════════════════╝

QUERY
─────────────────────────────────────────────────────────────────────────────
{analysis.original_query}

ROUTING DECISION
─────────────────────────────────────────────────────────────────────────────
Query Type: {analysis.query_type.upper()}
Overall Confidence: {analysis.confidence:.1%}

Confidence Breakdown:
  • SQL Query: {analysis.sql_confidence:.1%}
  • RAG Search: {analysis.rag_confidence:.1%}

DETECTED KEYWORDS ({len(analysis.keywords)})
─────────────────────────────────────────────────────────────────────────────
{', '.join(analysis.keywords[:10])}

DETECTED ENTITIES ({len(analysis.detected_entities)})
─────────────────────────────────────────────────────────────────────────────
{', '.join(analysis.detected_entities) if analysis.detected_entities else 'None'}

ROUTING RECOMMENDATION
─────────────────────────────────────────────────────────────────────────────
{analysis.recommendation}

ROUTING PARAMETERS
─────────────────────────────────────────────────────────────────────────────
"""
        for param, value in analysis.routing_parameters.items():
            if isinstance(value, bool):
                value = "✓" if value else "✗"
            report += f"  {param}: {value}\n"
        
        report += f"\nAnalysis Time: {analysis.timestamp}\n"
        
        return report


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("US-07: QUERY ROUTER - TESTING")
    print("=" * 70)
    
    # Initialize router
    router = QueryRouter()
    
    # Test queries
    test_queries = [
        "What is the total revenue for Q3?",  # SQL
        "Explain our company's remote work policy",  # RAG
        "Show me Q3 revenue and describe growth trends",  # Hybrid
        "List top 5 employees by salary",  # SQL
        "What are the requirements for vendor onboarding?",  # RAG
        "Compare Q3 and Q4 sales by department",  # Hybrid
    ]
    
    print("\nTesting query routing...\n")
    
    for query in test_queries:
        analysis = router.route_query(query)
        
        # Print routing report
        report = router.generate_routing_report(analysis)
        print(report)
        print("-" * 70)
    
    # Export routing log
    router.export_routing_log()
    
    print("\n✓ Query Router testing completed")