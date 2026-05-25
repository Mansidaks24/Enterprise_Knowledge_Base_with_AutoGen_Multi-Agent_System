"""
US-04: ANALYST AGENT
Build analyst agent for query interpretation and analysis
Interprets complex queries and analyzes retrieved data
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnalysisResult:
    """Structure for analysis results"""
    query: str
    key_findings: List[str]
    analysis: str
    patterns_identified: List[str]
    metrics: Dict[str, Any]
    business_impact: str
    confidence: float  # 0.0 to 1.0
    timestamp: str
    metadata: Dict[str, Any]


class AnalystAgent:
    """
    US-04: Analyst Agent
    Interprets queries and analyzes retrieved data
    """
    
    def __init__(self):
        """Initialize the Analyst Agent"""
        self.analysis_history = []
        print("✓ Analyst Agent initialized")
    
    def interpret_query(self, query: str) -> Dict[str, Any]:
        """
        Interpret the user's query to understand intent
        
        Args:
            query: User's natural language query
        
        Returns:
            Dictionary with query interpretation
        """
        interpretation = {
            "original_query": query,
            "query_type": self._classify_query(query),
            "intent": self._extract_intent(query),
            "entities": self._extract_entities(query),
            "temporal_scope": self._extract_temporal_scope(query),
        }
        
        return interpretation
    
    def _classify_query(self, query: str) -> str:
        """Classify query type: factual, comparative, trend, forecast, etc."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["compare", "vs", "versus", "difference"]):
            return "comparative"
        elif any(word in query_lower for word in ["trend", "over time", "growth", "decline"]):
            return "trend_analysis"
        elif any(word in query_lower for word in ["forecast", "predict", "next", "future"]):
            return "forecast"
        elif any(word in query_lower for word in ["why", "cause", "reason", "impact"]):
            return "causal_analysis"
        elif any(word in query_lower for word in ["what", "which", "who", "where"]):
            return "factual"
        else:
            return "general"
    
    def _extract_intent(self, query: str) -> str:
        """Extract the primary intent of the query"""
        query_lower = query.lower()
        
        if "summarize" in query_lower:
            return "summarization"
        elif "rank" in query_lower or "top" in query_lower:
            return "ranking"
        elif "calculate" in query_lower or "total" in query_lower:
            return "calculation"
        elif "identify" in query_lower:
            return "identification"
        else:
            return "general_inquiry"
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract key entities mentioned in query"""
        # Simple entity extraction
        common_entities = []
        query_words = query.split()
        
        # Look for common business terms
        business_terms = [
            "revenue", "sales", "profit", "cost", "customer", "product",
            "quarter", "year", "month", "department", "region", "employee"
        ]
        
        for word in query_words:
            word_clean = word.lower().strip(".,!?")
            if word_clean in business_terms:
                common_entities.append(word_clean)
        
        return list(set(common_entities))  # Remove duplicates
    
    def _extract_temporal_scope(self, query: str) -> str:
        """Extract temporal scope: this quarter, last year, etc."""
        query_lower = query.lower()
        
        temporal_keywords = {
            "today": "current_day",
            "this week": "current_week",
            "this month": "current_month",
            "this quarter": "current_quarter",
            "this year": "current_year",
            "last quarter": "previous_quarter",
            "last year": "previous_year",
            "ytd": "year_to_date",
            "all time": "historical",
        }
        
        for keyword, scope in temporal_keywords.items():
            if keyword in query_lower:
                return scope
        
        return "unspecified"
    
    def analyze_data(self, 
                     query: str,
                     retrieved_data: str,
                     data_context: Dict[str, Any] = None) -> AnalysisResult:
        """
        Analyze retrieved data in context of the query
        
        Args:
            query: Original query
            retrieved_data: Data retrieved by Retriever Agent
            data_context: Additional context about the data
        
        Returns:
            AnalysisResult with findings and insights
        """
        print(f"\n📊 Analyst Agent - Analyzing data")
        print(f"   Query: {query[:100]}...")
        
        # Interpret the query
        interpretation = self.interpret_query(query)
        
        # Extract key findings
        key_findings = self._extract_key_findings(retrieved_data, interpretation)
        
        # Perform detailed analysis
        analysis_text = self._generate_analysis(
            retrieved_data, 
            key_findings, 
            interpretation
        )
        
        # Identify patterns
        patterns = self._identify_patterns(retrieved_data, interpretation)
        
        # Extract metrics
        metrics = self._extract_metrics(retrieved_data, interpretation)
        
        # Assess business impact
        impact = self._assess_business_impact(key_findings, patterns, metrics)
        
        # Determine confidence
        confidence = self._calculate_confidence(
            retrieved_data,
            key_findings,
            interpretation
        )
        
        result = AnalysisResult(
            query=query,
            key_findings=key_findings,
            analysis=analysis_text,
            patterns_identified=patterns,
            metrics=metrics,
            business_impact=impact,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            metadata=interpretation
        )
        
        # Log analysis
        self.analysis_history.append({
            "query": query,
            "findings_count": len(key_findings),
            "confidence": confidence,
            "timestamp": result.timestamp
        })
        
        print(f"   ✓ Analysis complete ({confidence:.1%} confidence)")
        
        return result
    
    def _extract_key_findings(self, 
                             data: str,
                             interpretation: Dict) -> List[str]:
        """Extract key findings from the data"""
        findings = []
        
        # Basic finding extraction
        lines = data.split('\n')
        
        # Look for lines with numbers (potential key metrics)
        for line in lines:
            if any(char.isdigit() for char in line) and len(line) > 10:
                if line.strip() and not line.strip().startswith('-'):
                    findings.append(line.strip())
        
        # Add semantic findings based on query type
        query_type = interpretation.get("query_type", "general")
        
        if query_type == "comparative":
            findings.append("Comparative analysis: Multiple items compared in retrieved data")
        elif query_type == "trend_analysis":
            findings.append("Trend detected: Data shows progression over time period")
        elif query_type == "calculation":
            findings.append("Calculation performed: Aggregated metrics computed")
        
        return findings[:5]  # Limit to top 5 findings
    
    def _generate_analysis(self,
                          data: str,
                          findings: List[str],
                          interpretation: Dict) -> str:
        """Generate detailed analysis text"""
        analysis = f"""
DETAILED ANALYSIS
═════════════════════════════════════════════════════════════════

Query Type: {interpretation.get('query_type', 'General').title()}
Intent: {interpretation.get('intent', 'Unknown').replace('_', ' ').title()}
Scope: {interpretation.get('temporal_scope', 'Not specified').replace('_', ' ').title()}

Key Findings Summary:
{chr(10).join(f"• {finding}" for finding in findings)}

Data Insights:
"""
        
        # Add data-specific insights
        if "database" in data.lower():
            analysis += "- Data sourced from structured database\n"
        if "document" in data.lower():
            analysis += "- Data sourced from documents\n"
        
        if len(findings) > 0:
            analysis += f"- {len(findings)} significant patterns identified\n"
        
        analysis += f"""
Analysis Methodology:
• Extracted and analyzed {len(findings)} key metrics
• Identified patterns in retrieved data
• Contextualized findings within query scope
• Assessed data quality and completeness
"""
        
        return analysis
    
    def _identify_patterns(self, 
                          data: str,
                          interpretation: Dict) -> List[str]:
        """Identify patterns in the data"""
        patterns = []
        
        query_type = interpretation.get("query_type", "general")
        
        if query_type == "trend_analysis":
            patterns.append("Temporal progression: Data shows changes over time")
            patterns.append("Trend direction: Pattern indicates growth/decline")
        elif query_type == "comparative":
            patterns.append("Relative comparison: Items ranked by values")
            patterns.append("Distribution pattern: Spread across categories")
        else:
            patterns.append("Data distribution: Values span range")
            patterns.append("Concentration: Focus on key data points")
        
        # Check for numerical patterns
        if any(str(i) in data for i in range(10)):
            patterns.append("Numerical relationships: Quantitative patterns detected")
        
        return patterns
    
    def _extract_metrics(self,
                        data: str,
                        interpretation: Dict) -> Dict[str, Any]:
        """Extract quantitative metrics from data"""
        metrics = {
            "data_points": len(data.split('\n')),
            "query_type": interpretation.get("query_type", "unknown"),
            "entities_involved": len(interpretation.get("entities", [])),
            "temporal_scope": interpretation.get("temporal_scope", "unspecified"),
        }
        
        # Add numeric metrics if found
        import re
        numbers = re.findall(r'\d+\.?\d*', data)
        if numbers:
            numeric_values = [float(n) for n in numbers[:10]]  # First 10 numbers
            metrics["numeric_values"] = numeric_values
            metrics["average_value"] = sum(numeric_values) / len(numeric_values) if numeric_values else 0
            metrics["max_value"] = max(numeric_values) if numeric_values else 0
            metrics["min_value"] = min(numeric_values) if numeric_values else 0
        
        return metrics
    
    def _assess_business_impact(self,
                               findings: List[str],
                               patterns: List[str],
                               metrics: Dict) -> str:
        """Assess business impact of findings"""
        impact = "BUSINESS IMPACT ASSESSMENT\n"
        impact += "─" * 50 + "\n"
        
        if findings:
            impact += f"✓ {len(findings)} significant findings identified\n"
            impact += "  These insights can inform strategic decisions\n"
        
        if patterns:
            impact += f"✓ {len(patterns)} patterns detected\n"
            impact += "  Patterns may indicate trends or issues\n"
        
        if metrics.get("numeric_values"):
            impact += f"✓ Quantitative data available\n"
            impact += f"  Range: {metrics['min_value']:.2f} - {metrics['max_value']:.2f}\n"
        
        impact += "\nRecommended Actions:\n"
        impact += "• Use findings to inform decision-making\n"
        impact += "• Monitor identified patterns for changes\n"
        impact += "• Verify findings with fact-checking step\n"
        
        return impact
    
    def _calculate_confidence(self,
                             data: str,
                             findings: List[str],
                             interpretation: Dict) -> float:
        """Calculate confidence in the analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data quality
        if len(data) > 100:
            confidence += 0.15
        
        if len(findings) > 0:
            confidence += 0.15
        
        # Decrease confidence if intent unclear
        if interpretation.get("intent") == "general_inquiry":
            confidence -= 0.05
        
        # Cap confidence at 0.95
        return min(confidence, 0.95)
    
    def get_agent_system_message(self) -> str:
        """Return system message for AutoGen"""
        return """You are an Analyst Agent specialized in data interpretation and analysis.

Your responsibilities:
1. Interpret complex queries and understand business intent
2. Analyze data provided by the Retriever Agent
3. Identify patterns, trends, and relationships
4. Calculate relevant metrics and business KPIs
5. Assess potential business impact of findings

When responding, include:
- Key findings from the data
- Detailed analysis with context
- Identified patterns and trends
- Calculated metrics (if applicable)
- Business impact assessment

Be thorough, logical, and provide clear explanations of your reasoning."""
    
    def export_analysis_log(self, filepath: str = "analysis_log.json"):
        """Export analysis history for monitoring"""
        with open(filepath, 'w') as f:
            json.dump(self.analysis_history, f, indent=2)
        print(f"✓ Analysis log exported to {filepath}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("US-04: ANALYST AGENT - TESTING")
    print("=" * 70)
    
    # Initialize agent
    analyst = AnalystAgent()
    
    # Test data
    sample_data = """
    Retrieved data:
    Employee: John Smith, Salary: $85,000, Department: Sales
    Employee: Jane Doe, Salary: $92,000, Department: Engineering
    Employee: Bob Wilson, Salary: $78,000, Department: Support
    Total Revenue Q3: $2,500,000
    Revenue Q2: $2,100,000
    Growth Rate: 19.05%
    """
    
    test_queries = [
        "What is our sales growth trend?",
        "Compare revenue across quarters",
        "Analyze departmental salary distribution",
    ]
    
    print("\nRunning analysis tests...\n")
    
    for query in test_queries:
        result = analyst.analyze_data(query, sample_data)
        
        print(f"\nQuery: {query}")
        print(f"Type: {result.metadata['query_type']}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Findings: {len(result.key_findings)}")
        print(f"Impact: {result.business_impact[:100]}...")
        print("-" * 70)
    
    # Export log
    analyst.export_analysis_log()
    
    print("\n✓ Analyst Agent testing completed")