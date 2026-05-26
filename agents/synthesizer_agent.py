"""
US-06: SYNTHESIZER AGENT
Build synthesizer agent for final answer generation
Generates final polished answers with citations and confidence scores
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from agents.llm_adapter import LLMAdapter
from monitoring.logger import SystemLogger

@dataclass
class SynthesizedAnswer:
    """Structure for final synthesized answer"""
    original_query: str
    executive_summary: str
    detailed_analysis: str
    supporting_data: Dict[str, Any]
    sources_cited: List[str]
    confidence_score: float  # 0.0 to 1.0
    confidence_level: str  # HIGH, MEDIUM, LOW
    caveats_and_limitations: List[str]
    recommended_actions: List[str]
    timestamp: str


class SynthesizerAgent:
    """
    US-06: Synthesizer Agent
    Generates final polished answers with proper formatting and citations
    """
    
    def __init__(self):
        """Initialize the Synthesizer Agent"""
        self.synthesis_history = []
        self.formatting_rules = self._load_formatting_rules()
        # LLM adapter (optional)
        self.llm = LLMAdapter()
        print("✓ Synthesizer Agent initialized")
    
    def _load_formatting_rules(self) -> Dict[str, Any]:
        """Load professional formatting rules"""
        return {
            "max_summary_length": 200,
            "max_sections": 5,
            "include_executive_summary": True,
            "include_recommendations": True,
            "include_caveats": True,
            "cite_sources": True,
        }
    
    def synthesize_answer(self,
                         query: str,
                         analyst_findings: str,
                         fact_check_report: str,
                         source_citations: List[str],
                         confidence_score: float) -> SynthesizedAnswer:
        """
        Synthesize final answer from all agent outputs
        
        Args:
            query: Original user query
            analyst_findings: Analysis from Analyst Agent
            fact_check_report: Validation report from Fact-Checker Agent
            source_citations: List of sources used
            confidence_score: Overall confidence from Fact-Checker
        
        Returns:
            SynthesizedAnswer with final polished response
        """
        SystemLogger.info(
            "Synthesizing final answer"
        )
        print(f"\n📝 Synthesizer Agent - Generating final answer")
        print(f"   Query: {query[:100]}...")
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            query,
            analyst_findings,
            confidence_score
        )
        
        # Generate detailed analysis section
        detailed_analysis = self._format_detailed_analysis(analyst_findings)
        
        # Extract supporting data
        supporting_data = self._extract_supporting_data(analyst_findings)
        
        # Prepare source citations
        formatted_citations = self._format_citations(source_citations)
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(confidence_score)
        
        # Extract caveats from fact-check
        caveats = self._extract_caveats(fact_check_report, analyst_findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            analyst_findings,
            caveats,
            confidence_level
        )
        
        answer = SynthesizedAnswer(
            original_query=query,
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            supporting_data=supporting_data,
            sources_cited=formatted_citations,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            caveats_and_limitations=caveats,
            recommended_actions=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        # Log synthesis
        self.synthesis_history.append({
            "query": query,
            "confidence": confidence_score,
            "has_caveats": len(caveats) > 0,
            "timestamp": answer.timestamp
        })
        
        print(f"   ✓ Answer generated ({confidence_level} confidence)")
        
        return answer
    
    def _generate_executive_summary(self,
                                   query: str,
                                   findings: str,
                                   confidence: float) -> str:
        """Generate concise executive summary"""
        summary = "EXECUTIVE SUMMARY\n"
        summary += "─" * 50 + "\n\n"
        
        # Extract key insight from findings
        finding_lines = findings.split('\n')
        key_insight = next(
            (line.strip() for line in finding_lines 
             if line.strip() and len(line.strip()) > 20),
            "Analysis complete"
        )
        
        summary += f"To your question: \"{query}\"\n\n"
        summary += f"Key Finding: {key_insight[:150]}\n\n"
        summary += f"Confidence Level: {self._get_confidence_level(confidence)} "
        summary += f"({confidence:.0%} confidence)\n"

        # Optionally use LLM to rephrase the executive summary for readability
        if self.llm.is_configured():
            prompt = f"Write a concise executive summary for the following query and findings:\nQuery: {query}\nFindings:\n{findings}\nConfidence: {confidence:.2f}\n"
            resp = self.llm.generate(prompt, max_tokens=150)
            if resp and resp.get("text"):
                # Prefer LLM text but keep original context
                summary = resp["text"] + "\n\n" + summary
        
        return summary
    
    def _format_detailed_analysis(self, findings: str) -> str:
        """Format detailed analysis in professional structure"""
        analysis = "DETAILED ANALYSIS\n"
        analysis += "─" * 50 + "\n\n"
        
        # Structure the findings
        finding_lines = [line.strip() for line in findings.split('\n') if line.strip()]
        
        for i, line in enumerate(finding_lines[:5], 1):
            analysis += f"{i}. {line}\n"
        
        analysis += "\nKey Metrics:\n"
        
        # Extract any metrics mentioned
        import re
        numbers = re.findall(r'(\d+\.?\d*)\s*(%|K|M|B)?', findings)
        if numbers:
            for i, (num, unit) in enumerate(numbers[:3], 1):
                analysis += f"  • Metric {i}: {num}{unit or ''}\n"
        else:
            analysis += "  • See supporting data section\n"
        
        return analysis
    
    def _extract_supporting_data(self, findings: str) -> Dict[str, Any]:
        """Extract structured data for supporting section"""
        data = {
            "data_points": len(findings.split('\n')),
            "sections": self._count_sections(findings),
            "metrics": self._extract_metrics(findings),
        }
        
        return data
    
    def _count_sections(self, text: str) -> int:
        """Count logical sections in text"""
        sections = 0
        lines = text.split('\n')
        
        for line in lines:
            if line.strip() and line.strip()[0].isupper() and len(line.strip()) > 20:
                sections += 1
        
        return max(sections, 1)
    
    def _extract_metrics(self, text: str) -> Dict[str, str]:
        """Extract key metrics from text"""
        import re
        metrics = {}
        
        # Look for metric patterns
        patterns = {
            "growth": r'growth[:\s]+(\d+\.?\d*)\s*(%)?',
            "revenue": r'revenue[:\s]+(\$[\d,]+)',
            "percentage": r'(\d+\.?\d*)\s*%',
        }
        
        for metric_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics[metric_name] = match.group(1)
        
        return metrics
    
    def _format_citations(self, sources: List[str]) -> List[str]:
        """Format source citations in professional style"""
        citations = []
        
        for i, source in enumerate(sources, 1):
            citation = f"[{i}] {source}"
            citations.append(citation)
        
        return citations
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 0.8:
            return "HIGH"
        elif confidence_score >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_caveats(self, fact_check: str, findings: str) -> List[str]:
        """Extract limitations and caveats"""
        caveats = []
        
        # Check for uncertainty markers
        uncertainty_markers = [
            "uncertain",
            "unclear",
            "approximate",
            "estimated",
            "may indicate",
            "suggests",
            "likely"
        ]
        
        combined_text = f"{fact_check}\n{findings}".lower()
        
        for marker in uncertainty_markers:
            if marker in combined_text:
                caveats.append(f"Some findings are based on {marker} data")
                break
        
        # Add general caveats
        if not caveats:
            caveats.append("Analysis based on available data as of report generation date")
        
        caveats.append("Recommendations should be reviewed with domain experts")
        caveats.append("External factors not captured in data may impact outcomes")
        
        return caveats[:3]  # Limit to 3 caveats
    
    def _generate_recommendations(self,
                                 findings: str,
                                 caveats: List[str],
                                 confidence_level: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Base recommendations on confidence level
        if confidence_level == "HIGH":
            recommendations.append("Act on these findings with confidence")
            recommendations.append("Monitor progress against key metrics")
            recommendations.append("Document decisions for future reference")
        elif confidence_level == "MEDIUM":
            recommendations.append("Consider these findings alongside other data")
            recommendations.append("Validate with domain experts before decisions")
            recommendations.append("Plan additional research if needed")
        else:  # LOW
            recommendations.append("Request additional data for verification")
            recommendations.append("Consult with subject matter experts")
            recommendations.append("Avoid critical decisions based solely on this analysis")
        
        # Add general recommendations
        if "uncertain" in str(caveats).lower():
            recommendations.append("Clarify uncertain data before proceeding")
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def format_for_presentation(self, answer: SynthesizedAnswer) -> str:
        """Format final answer for professional presentation"""
        output = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                          FINAL ANSWER REPORT                               ║
╚════════════════════════════════════════════════════════════════════════════╝

{answer.executive_summary}

{answer.detailed_analysis}

SUPPORTING DATA
─────────────────────────────────────────────────────────────────────────────
Data Points Analyzed: {answer.supporting_data.get('data_points', 'N/A')}
Sections Covered: {answer.supporting_data.get('sections', 'N/A')}
Key Metrics: {json.dumps(answer.supporting_data.get('metrics', {}), indent=2)}

SOURCES & CITATIONS
─────────────────────────────────────────────────────────────────────────────
"""
        
        for citation in answer.sources_cited:
            output += f"{citation}\n"
        
        output += f"""

CONFIDENCE ASSESSMENT
─────────────────────────────────────────────────────────────────────────────
Overall Confidence: {answer.confidence_level} ({answer.confidence_score:.0%})
"""
        
        if answer.caveats_and_limitations:
            output += f"""

CAVEATS & LIMITATIONS
─────────────────────────────────────────────────────────────────────────────
"""
            for caveat in answer.caveats_and_limitations:
                output += f"⚠️  {caveat}\n"
        
        if answer.recommended_actions:
            output += f"""

RECOMMENDED ACTIONS
─────────────────────────────────────────────────────────────────────────────
"""
            for i, action in enumerate(answer.recommended_actions, 1):
                output += f"{i}. {action}\n"
        
        output += f"""

Report Generated: {answer.timestamp}
═════════════════════════════════════════════════════════════════════════════
"""
        
        return output
    
    def get_agent_system_message(self) -> str:
        """Return system message for AutoGen"""
        return """You are a Synthesizer Agent responsible for generating final answers.

Your responsibilities:
1. Combine insights from Analyst and Fact-Checker agents
2. Create professional, well-structured responses
3. Format with clear sections and formatting
4. Include citations to source documents
5. Provide confidence assessments
6. Add appropriate caveats and recommendations

When responding, structure as:
- Executive Summary (2-3 sentences)
- Detailed Analysis (key findings and insights)
- Supporting Data (metrics and evidence)
- Citations (source references)
- Confidence Assessment
- Caveats/Limitations
- Recommended Actions

Make responses clear, professional, and actionable for business stakeholders."""
    
    def export_synthesis_log(self, filepath: str = "synthesis_log.json"):
        """Export synthesis history"""
        with open(filepath, 'w') as f:
            json.dump(self.synthesis_history, f, indent=2)
        print(f"✓ Synthesis log exported to {filepath}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("US-06: SYNTHESIZER AGENT - TESTING")
    print("=" * 70)
    
    # Initialize agent
    synthesizer = SynthesizerAgent()
    
    # Sample inputs
    sample_query = "What is our Q3 revenue and growth trajectory?"
    sample_findings = """
    Q3 Revenue: $2,500,000
    Q2 Revenue: $2,100,000
    Growth Rate: 19%
    Engineering Revenue: $1,200,000 (48% of total)
    Sales Revenue: $900,000 (36% of total)
    Support Revenue: $400,000 (16% of total)
    
    The data shows strong growth in Q3, with Engineering division leading.
    All departments contributed to revenue growth compared to Q2.
    Growth rate of 19% exceeds quarterly targets.
    """
    
    sample_fact_check = """
    All claims verified at HIGH confidence
    Revenue figures confirmed from Q3 financial statements
    Growth calculations accurate
    """
    
    sample_sources = [
        "Q3 Financial Report",
        "Revenue Database",
        "Departmental Performance Records"
    ]
    
    print("\nGenerating synthesized answer...\n")
    
    # Synthesize answer
    answer = synthesizer.synthesize_answer(
        query=sample_query,
        analyst_findings=sample_findings,
        fact_check_report=sample_fact_check,
        source_citations=sample_sources,
        confidence_score=0.92
    )
    
    # Format for presentation
    output = synthesizer.format_for_presentation(answer)
    print(output)
    
    # Export log
    synthesizer.export_synthesis_log()
    
    print("\n✓ Synthesizer Agent testing completed")