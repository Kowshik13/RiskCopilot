"""
Guardrails implementation for Risk Copilot
Handles PII detection, content filtering, and safety checks
"""

import re
from typing import List, Dict, Any, Tuple
from enum import Enum
import structlog

from app.models import GuardrailViolation, RiskLevel

logger = structlog.get_logger()

class ViolationType(Enum):
    PII = "pii"
    TOXIC = "toxic"
    BANNED_TOPIC = "banned_topic"
    PROMPT_INJECTION = "prompt_injection"

class GuardrailsEngine:
    """
    Comprehensive guardrails for input/output validation
    """
    
    def __init__(self):
        """Initialize guardrails with patterns and rules"""
        
        # PII Patterns (simplified for demo - in production use presidio)
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
            'passport': r'\b[A-Z][0-9]{8}\b',
            'french_secu': r'\b[12][0-9]{2}[0-1][0-9][0-9]{8}\b'  # French social security
        }
        
        # Banned topics for financial context
        self.banned_topics = [
            'insider trading',
            'money laundering', 
            'tax evasion',
            'market manipulation',
            'ponzi scheme',
            'pyramid scheme',
            'terrorism financing'
        ]
        
        # Toxic content patterns (simplified)
        self.toxic_patterns = [
            'hate speech',
            'discrimination',
            'harassment',
            'violence',
            'self-harm'
        ]
        
        # Prompt injection patterns
        self.injection_patterns = [
            'ignore previous instructions',
            'disregard all rules',
            'pretend you are',
            'act as if',
            'bypass safety',
            'jailbreak'
        ]
        
    def check_pii(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Check for PII in text
        
        Returns:
            List of (type, matched_text, redacted_text) tuples
        """
        violations = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group()
                # Redact based on type
                if pii_type == 'email':
                    redacted = matched_text.split('@')[0][:2] + '***@***'
                elif pii_type in ['ssn', 'credit_card', 'iban']:
                    redacted = matched_text[:4] + '*' * (len(matched_text) - 4)
                else:
                    redacted = '[REDACTED]'
                
                violations.append((pii_type, matched_text, redacted))
        
        return violations
    
    def check_banned_topics(self, text: str) -> List[str]:
        """
        Check for banned topics
        
        Returns:
            List of detected banned topics
        """
        detected = []
        text_lower = text.lower()
        
        for topic in self.banned_topics:
            if topic.lower() in text_lower:
                detected.append(topic)
        
        return detected
    
    def check_toxicity(self, text: str) -> bool:
        """
        Simple toxicity check (in production, use perspective API or similar)
        
        Returns:
            True if toxic content detected
        """
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.toxic_patterns)
    
    def check_prompt_injection(self, text: str) -> bool:
        """
        Check for potential prompt injection attempts
        
        Returns:
            True if injection attempt detected
        """
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.injection_patterns)
    
    def sanitize_input(self, text: str) -> Tuple[str, List[GuardrailViolation]]:
        """
        Sanitize input text and return violations
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Tuple of (sanitized_text, violations)
        """
        violations = []
        sanitized = text
        
        # Check for PII
        pii_violations = self.check_pii(text)
        if pii_violations:
            for pii_type, matched, redacted in pii_violations:
                sanitized = sanitized.replace(matched, redacted)
                violations.append(GuardrailViolation(
                    type="pii",
                    severity=RiskLevel.HIGH,
                    description=f"Detected {pii_type.upper()} in input",
                    detected_content=redacted
                ))
        
        # Check for banned topics
        banned = self.check_banned_topics(text)
        if banned:
            violations.append(GuardrailViolation(
                type="banned_topic",
                severity=RiskLevel.MEDIUM,
                description=f"Detected banned topics: {', '.join(banned)}",
                detected_content=None
            ))
        
        # Check for toxicity
        if self.check_toxicity(text):
            violations.append(GuardrailViolation(
                type="toxic",
                severity=RiskLevel.HIGH,
                description="Potentially toxic content detected",
                detected_content=None
            ))
        
        # Check for prompt injection
        if self.check_prompt_injection(text):
            violations.append(GuardrailViolation(
                type="prompt_injection",
                severity=RiskLevel.CRITICAL,
                description="Potential prompt injection attempt",
                detected_content=None
            ))
        
        return sanitized, violations
    
    def validate_output(self, text: str) -> List[GuardrailViolation]:
        """
        Validate output before sending to user
        
        Args:
            text: Output text to validate
            
        Returns:
            List of violations found
        """
        violations = []
        
        # Check output doesn't contain PII
        pii_violations = self.check_pii(text)
        if pii_violations:
            violations.append(GuardrailViolation(
                type="pii",
                severity=RiskLevel.CRITICAL,
                description="Output contains PII - blocking response",
                detected_content="[PII DETECTED IN OUTPUT]"
            ))
        
        # Check for hallucination markers (simplified)
        hallucination_markers = [
            "as an ai language model",
            "i don't have access to",
            "i cannot provide",
            "my training data"
        ]
        
        text_lower = text.lower()
        if any(marker in text_lower for marker in hallucination_markers):
            violations.append(GuardrailViolation(
                type="hallucination",
                severity=RiskLevel.MEDIUM,
                description="Potential hallucination or inappropriate response",
                detected_content=None
            ))
        
        return violations
    
    def calculate_risk_level(self, violations: List[GuardrailViolation]) -> RiskLevel:
        """
        Calculate overall risk level from violations
        
        Args:
            violations: List of violations
            
        Returns:
            Overall risk level
        """
        if not violations:
            return RiskLevel.LOW
        
        # Get highest severity
        severities = [v.severity for v in violations]
        
        if RiskLevel.CRITICAL in severities:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in severities:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in severities:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def generate_audit_entry(
        self, 
        input_text: str,
        output_text: str,
        violations: List[GuardrailViolation],
        risk_level: RiskLevel
    ) -> Dict[str, Any]:
        """
        Generate audit log entry
        
        Returns:
            Audit log entry dict
        """
        return {
            "input_length": len(input_text),
            "output_length": len(output_text),
            "violations_count": len(violations),
            "violation_types": list(set(v.type for v in violations)),
            "risk_level": risk_level.value,
            "pii_detected": any(v.type == "pii" for v in violations),
            "injection_attempted": any(v.type == "prompt_injection" for v in violations)
        }


# Singleton instance
_guardrails_engine = None

def get_guardrails_engine() -> GuardrailsEngine:
    """Get singleton instance of guardrails engine"""
    global _guardrails_engine
    if _guardrails_engine is None:
        _guardrails_engine = GuardrailsEngine()
    return _guardrails_engine