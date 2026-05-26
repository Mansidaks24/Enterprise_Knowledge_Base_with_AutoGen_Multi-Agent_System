"""
US-05: FACT-CHECKER AGENT
Build fact-checking agent to validate responses
Validates responses against source documents and flags low-confidence claims
"""

import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from monitoring.logger import SystemLogger

@dataclass
class FactCheckResult:
    """Structure for fact-checking results"""
    claim: str
    is_verified: bool
    confidence_level: str  # HIGH, MEDIUM, LOW
    confidence_score: float  # 0.0 to 1.0
    supporting_evidence: str
    sources: List[str]
    corrections_needed: str
    timestamp: str


@dataclass
class ValidationReport:
    """Structure for complete validation report"""
    original_analysis: str
    verification_results: List[FactCheckResult]
    overall_confidence: float  # 0.0 to 1.0
    issues_found: List[str]
    corrections_suggested: List[str]
    overall_confidence_level: str  # HIGH, MEDIUM, LOW
    timestamp: str
    metadata: Dict[str, Any]


class FactCheckerAgent:
    """
    US-05: Fact-Checker Agent
    Validates claims and responses against source documents
    """
    
    def __init__(self):
        """Initialize the Fact-Checker Agent"""
        self.fact_check_history = []
        self.known_facts = {}  # Store verified facts
        print("✓ Fact-Checker Agent initialized")
    
    def validate_analysis(self,
                         analysis_text: str,
                         source_documents: str,
                         original_query: str = "") -> ValidationReport:
        """
        Validate analysis against source documents
        
        Args:
            analysis_text: Analysis to validate
            source_documents: Original source documents for fact-checking
            original_query: Original user query for context
        
        Returns:
            ValidationReport with findings
        """
        SystemLogger.info(
            "Fact-checking analysis"
        )
        print(f"\n✓ Fact-Checker Agent - Validating analysis")
        print(f"   Analyzing: {analysis_text[:100]}...")
        
        # Extract claims from analysis
        claims = self._extract_claims(analysis_text)
        
        # Fact-check each claim
        verification_results = []
        for claim in claims:
            result = self._fact_check_claim(claim, source_documents)
            verification_results.append(result)
        
        # Identify issues
        issues = self._identify_issues(verification_results)
        
        # Generate corrections
        corrections = self._generate_corrections(verification_results, issues)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(verification_results)
        overall_level = self._get_confidence_level(overall_confidence)
        
        report = ValidationReport(
            original_analysis=analysis_text,
            verification_results=verification_results,
            overall_confidence=overall_confidence,
            issues_found=issues,
            corrections_suggested=corrections,
            overall_confidence_level=overall_level,
            timestamp=datetime.now().isoformat(),
            metadata={
                "total_claims": len(claims),
                "verified_claims": sum(1 for r in verification_results if r.is_verified),
                "unverified_claims": sum(1 for r in verification_results if not r.is_verified),
                "original_query": original_query
            }
        )
        
        # Log validation
        self.fact_check_history.append({
            "timestamp": report.timestamp,
            "claims_checked": len(claims),
            "overall_confidence": overall_confidence,
            "issues_found": len(issues)
        })
        
        print(f"   ✓ Validation complete - {overall_level} confidence")
        
        return report
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from analysis text"""
        claims = []
        
        # Split text into sentences
        sentences = text.replace('.', '.\n').split('\n')
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Filter for statements that contain facts (not questions or instructions)
            if (sentence and 
                len(sentence) > 10 and 
                not sentence.endswith('?') and
                not any(word in sentence.lower() for word in ['please', 'should', 'could', 'might'])):
                
                claims.append(sentence)
        
        return claims[:10]  # Limit to 10 claims for validation
    
    def _fact_check_claim(self,
                         claim: str,
                         source_documents: str) -> FactCheckResult:
        """
        Fact-check a single claim
        
        Args:
            claim: Claim to check
            source_documents: Source documents for verification
        
        Returns:
            FactCheckResult for the claim
        """
        # Check if claim exists in sources
        claim_lower = claim.lower()
        source_lower = source_documents.lower()
        
        # Simple text matching
        is_directly_stated = claim_lower in source_lower or \
                            any(word in source_lower for word in claim_lower.split()[1:4])
        
        # Determine confidence
        if is_directly_stated:
            confidence_score = 0.95
            confidence_level = "HIGH"
            supporting_evidence = "Directly stated in source documents"
        else:
            # Check for partial matches
            matching_words = sum(1 for word in claim_lower.split() 
                               if word in source_lower and len(word) > 3)
            total_words = len([w for w in claim_lower.split() if len(w) > 3])
            
            if total_words > 0:
                match_ratio = matching_words / total_words
                
                if match_ratio > 0.7:
                    confidence_score = 0.75
                    confidence_level = "MEDIUM"
                    supporting_evidence = "Inferred from source documents"
                elif match_ratio > 0.4:
                    confidence_score = 0.5
                    confidence_level = "LOW"
                    supporting_evidence = "Partially supported by sources"
                else:
                    confidence_score = 0.2
                    confidence_level = "LOW"
                    supporting_evidence = "Not well supported by sources"
            else:
                confidence_score = 0.3
                confidence_level = "LOW"
                supporting_evidence = "Cannot verify from available sources"
        
        # Identify corrections if needed
        corrections = ""
        if confidence_score < 0.7:
            corrections = f"Consider verifying or modifying claim: '{claim}'"
        
        result = FactCheckResult(
            claim=claim,
            is_verified=(confidence_score >= 0.7),
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            supporting_evidence=supporting_evidence,
            sources=["Source Document"] if confidence_score > 0 else [],
            corrections_needed=corrections,
            timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def _identify_issues(self, 
                        verification_results: List[FactCheckResult]) -> List[str]:
        """Identify accuracy issues from verification results"""
        issues = []
        
        # Check for unverified claims
        unverified = [r for r in verification_results if not r.is_verified]
        if unverified:
            issues.append(f"⚠️  {len(unverified)} claims could not be fully verified")
        
        # Check for low confidence claims
        low_confidence = [r for r in verification_results 
                         if r.confidence_score < 0.7]
        if low_confidence:
            issues.append(f"⚠️  {len(low_confidence)} claims have low confidence scores")
        
        # Check if any claims have zero confidence
        unsupported = [r for r in verification_results 
                      if r.confidence_score < 0.3]
        if unsupported:
            issues.append(f"🚨 {len(unsupported)} claims lack supporting evidence")
        
        return issues
    
    def _generate_corrections(self,
                             verification_results: List[FactCheckResult],
                             issues: List[str]) -> List[str]:
        """Generate correction suggestions"""
        corrections = []
        
        # Collect correction suggestions from individual claims
        for result in verification_results:
            if result.corrections_needed:
                corrections.append(result.corrections_needed)
        
        # Add general corrections based on issues
        if len([r for r in verification_results if not r.is_verified]) > 3:
            corrections.append("Consider requesting additional source documents for verification")
        
        # Limit to top 5 corrections
        return corrections[:5]
    
    def _calculate_overall_confidence(self,
                                     verification_results: List[FactCheckResult]) -> float:
        """Calculate overall confidence score"""
        if not verification_results:
            return 0.0
        
        avg_confidence = sum(r.confidence_score for r in verification_results) / len(verification_results)
        
        return avg_confidence
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 0.8:
            return "HIGH"
        elif confidence_score >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_validation_report_text(self, 
                                       report: ValidationReport) -> str:
        """Generate human-readable validation report"""
        report_text = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      FACT-CHECK VALIDATION REPORT                          ║
╚════════════════════════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY
─────────────────────────────────────────────────────────────────────────────
Overall Confidence Level: {report.overall_confidence_level}
Overall Confidence Score: {report.overall_confidence:.1%}
Total Claims Checked: {report.metadata['total_claims']}
Verified Claims: {report.metadata['verified_claims']} ✓
Unverified Claims: {report.metadata['unverified_claims']} ⚠️

VERIFICATION RESULTS
─────────────────────────────────────────────────────────────────────────────
"""
        
        for i, result in enumerate(report.verification_results, 1):
            status = "✓ VERIFIED" if result.is_verified else "⚠️  UNVERIFIED"
            report_text += f"""
Claim #{i}: {status}
  Statement: "{result.claim}"
  Confidence: {result.confidence_level} ({result.confidence_score:.1%})
  Evidence: {result.supporting_evidence}
"""
            if result.corrections_needed:
                report_text += f"  ⚠️  Note: {result.corrections_needed}\n"
        
        # Issues section
        if report.issues_found:
            report_text += f"""
ISSUES IDENTIFIED
─────────────────────────────────────────────────────────────────────────────
"""
            for issue in report.issues_found:
                report_text += f"• {issue}\n"
        
        # Corrections section
        if report.corrections_suggested:
            report_text += f"""
RECOMMENDED CORRECTIONS
─────────────────────────────────────────────────────────────────────────────
"""
            for i, correction in enumerate(report.corrections_suggested, 1):
                report_text += f"{i}. {correction}\n"
        
        # Conclusion
        report_text += f"""
CONCLUSION
─────────────────────────────────────────────────────────────────────────────
The analysis has a {report.overall_confidence_level} confidence level.
"""
        
        if report.overall_confidence >= 0.8:
            report_text += "✓ This analysis is suitable for decision-making.\n"
        elif report.overall_confidence >= 0.6:
            report_text += "⚠️  This analysis should be reviewed with caution.\n"
        else:
            report_text += "🚨 This analysis requires verification before use.\n"
        
        report_text += f"\nValidation Time: {report.timestamp}\n"
        
        return report_text
    
    def flag_low_confidence_answers(self,
                                    answers: List[str],
                                    confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Flag answers with confidence below threshold"""
        flagged = []
        
        for answer in answers:
            # Simulate confidence scoring
            confidence = 0.8  # Default confidence
            
            if "uncertain" in answer.lower() or "unclear" in answer.lower():
                confidence = 0.5
            
            if confidence < confidence_threshold:
                flagged.append({
                    "answer": answer,
                    "confidence": confidence,
                    "reason": "Low confidence due to unclear sources"
                })
        
        return {
            "flagged_count": len(flagged),
            "threshold": confidence_threshold,
            "flagged_answers": flagged
        }
    
    def get_agent_system_message(self) -> str:
        """Return system message for AutoGen"""
        return """You are a Fact-Checker Agent specialized in validating claims and responses.

Your responsibilities:
1. Review analysis provided by the Analyst Agent
2. Cross-check claims against source documents
3. Verify numerical data and calculations
4. Flag unsupported or low-confidence statements
5. Identify potential errors or hallucinations
6. Assign confidence levels (HIGH/MEDIUM/LOW)

When responding, include:
- Verification status for each major claim
- Confidence levels with justification
- Any discrepancies found
- Suggested corrections if needed
- Overall confidence assessment

Be rigorous and highlight any issues that could affect decision-making."""
    
    def export_validation_log(self, filepath: str = "validation_log.json"):
        """Export fact-checking history"""
        with open(filepath, 'w') as f:
            json.dump(self.fact_check_history, f, indent=2)
        print(f"✓ Validation log exported to {filepath}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("US-05: FACT-CHECKER AGENT - TESTING")
    print("=" * 70)
    
    # Initialize agent
    fact_checker = FactCheckerAgent()
    
    # Sample analysis and sources
    sample_analysis = """
    Q3 Revenue reached $2,500,000, representing a 19% increase from Q2.
    Sales by department: Engineering $1,200,000, Sales $900,000, Support $400,000.
    This indicates strong growth in the Engineering division.
    The average salary in Engineering is approximately $95,000 per employee.
    """
    
    sample_sources = """
    Q3 Financial Report:
    Total Revenue: $2,500,000
    Q2 Revenue: $2,100,000
    Department Revenue:
    - Engineering: $1,200,000
    - Sales: $900,000
    - Support: $400,000
    Engineering Department has shown consistent growth over three quarters.
    """
    
    print("\nRunning fact-check tests...\n")
    
    # Validate analysis
    report = fact_checker.validate_analysis(
        analysis_text=sample_analysis,
        source_documents=sample_sources,
        original_query="What is our Q3 revenue?"
    )
    
    # Print validation report
    report_text = fact_checker.generate_validation_report_text(report)
    print(report_text)
    
    # Flag low confidence answers
    answers = [
        "The company grew by approximately 19% in Q3",
        "Engineering division is uncertain about future growth",
    ]
    
    flagged = fact_checker.flag_low_confidence_answers(answers, threshold=0.7)
    print("\nLow Confidence Answers Flagged:")
    print(json.dumps(flagged, indent=2))
    
    # Export log
    fact_checker.export_validation_log()
    
    print("\n✓ Fact-Checker Agent testing completed")