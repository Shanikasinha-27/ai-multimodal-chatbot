import re
from typing import Tuple, Dict, Any
from core.config import settings

class EmotionalGuardrails:
    """
    Guardrail and Safety Enforcement Layer for Emotional Support Chatbot.
    Enforces:
    1. Crisis & Self-Harm Intervention
    2. Medical/Psychiatric Diagnosis Deflection
    3. PII (Personally Identifiable Information) Redaction
    4. Prompt Injection & Jailbreak Defense
    """

    # Crisis trigger keywords and phrases
    CRISIS_PATTERNS = [
        r"\b(kill\s+(myself|me))\b",
        r"\b(want\s+to\s+die)\b",
        r"\b(commit\s+suicide)\b",
        r"\b(suicidal(\s+thoughts)?)\b",
        r"\b(end\s+my\s+life)\b",
        r"\b(hurt\s+(myself|me))\b",
        r"\b(self[\s-]harm)\b",
        r"\b(cut\s+myself)\b",
        r"\b(no\s+reason\s+to\s+live)\b",
        r"\b(better\s+off\s+dead)\b",
        r"\b(overdose\s+on)\b",
        r"\b(goodbye\s+cruel\s+world)\b",
        r"\b(hang\s+myself)\b"
    ]

    # Jailbreak / Injection patterns
    JAILBREAK_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"system\s*prompt\s*override",
        r"you\s+are\s+now\s+in\s+dan\s+mode",
        r"bypass\s+(all\s+)?guardrails",
        r"act\s+as\s+an\s+unrestricted\s+ai",
        r"forget\s+your\s+ethical\s+guidelines"
    ]

    # Medical diagnosis defense patterns
    DIAGNOSIS_PATTERNS = [
        r"\b(diagnose\s+me\s+with)\b",
        r"\b(what\s+prescription\s+should\s+i\s+take)\b",
        r"\b(prescribe\s+(me\s+)?(medication|drugs|antidepressants))\b",
        r"\b(what\s+dosage\s+of\s+\w+\s+should\s+i\s+take)\b"
    ]

    # PII Regex patterns
    PII_PHONE = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    PII_EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    PII_SSN = r"\b\d{3}-\d{2}-\d{4}\b"
    PII_CREDIT_CARD = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"

    @classmethod
    def check_crisis(cls, text: str) -> Tuple[bool, str]:
        """
        Scans input for self-harm or acute crisis signals.
        Returns (is_crisis, response_message).
        """
        if not text:
            return False, ""
        
        normalized = text.lower().strip()
        for pattern in cls.CRISIS_PATTERNS:
            if re.search(pattern, normalized):
                emergency_response = (
                    "💙 **I hear how much pain you are experiencing right now, and I want you to be safe.**\n\n"
                    "Because I am an AI, I cannot provide immediate emergency support, but caring and trained "
                    "professionals are available right now to help you through this:\n\n"
                    f"- 📞 **Suicide & Crisis Lifeline**: {settings.CRISIS_HELPLINE_PRIMARY}\n"
                    f"- 💬 **Crisis Text Line**: {settings.CRISIS_HELPLINE_TEXT}\n"
                    "- 🌍 **International Resources**: If you are outside the US, please visit [Befrienders Worldwide](https://www.befrienders.org/) or [Find A Helpline](https://findahelpline.com/) to find free, confidential support in your country.\n"
                    "- 🚨 **Immediate Emergency**: Please call your local emergency services (like 911, 999, or 112) or go to the nearest emergency room.\n\n"
                    "You matter, and you don't have to carry this alone. Please connect with one of these resources right away."
                )
                return True, emergency_response
        
        return False, ""

    @classmethod
    def check_jailbreak(cls, text: str) -> Tuple[bool, str]:
        """
        Detects prompt injection attempts.
        """
        if not text:
            return False, ""
        
        normalized = text.lower()
        for pattern in cls.JAILBREAK_PATTERNS:
            if re.search(pattern, normalized):
                warning = (
                    "I am dedicated to providing a safe, supportive, and compassionate space. "
                    "I cannot modify my core safety guidelines or instructions. How can I support your wellbeing today?"
                )
                return True, warning
        return False, ""

    @classmethod
    def check_medical_advice(cls, text: str) -> Tuple[bool, str]:
        """
        Catches explicit requests for clinical diagnosis or prescription recommendations.
        """
        if not text:
            return False, ""
        
        normalized = text.lower()
        for pattern in cls.DIAGNOSIS_PATTERNS:
            if re.search(pattern, normalized):
                disclaimer = (
                    "⚠️ **Important Disclaimer**: As an AI emotional support assistant, I cannot provide medical diagnoses, "
                    "clinical assessments, or prescribe medications. If you have questions about specific diagnoses or medications, "
                    "please consult with a licensed physician, psychiatrist, or qualified healthcare professional. "
                    "I am here to listen, offer emotional grounding exercises, and discuss healthy coping strategies."
                )
                return True, disclaimer
        return False, ""

    @classmethod
    def sanitize_pii(cls, text: str) -> str:
        """
        Redacts personally identifiable information (PII) before storage.
        """
        if not text:
            return text
        
        sanitized = re.sub(cls.PII_PHONE, "[REDACTED_PHONE]", text)
        sanitized = re.sub(cls.PII_EMAIL, "[REDACTED_EMAIL]", sanitized)
        sanitized = re.sub(cls.PII_SSN, "[REDACTED_SSN]", sanitized)
        sanitized = re.sub(cls.PII_CREDIT_CARD, "[REDACTED_CARD]", sanitized)
        return sanitized

    @classmethod
    def evaluate_input(cls, text: str) -> Dict[str, Any]:
        """
        Full guardrail evaluation pipeline on user input.
        Returns a decision dictionary.
        """
        # 1. Check Crisis
        is_crisis, crisis_msg = cls.check_crisis(text)
        if is_crisis:
            return {
                "blocked": True,
                "reason": "CRISIS_DETECTED",
                "response": crisis_msg,
                "sanitized_text": cls.sanitize_pii(text)
            }
        
        # 2. Check Jailbreak
        is_jailbreak, jailbreak_msg = cls.check_jailbreak(text)
        if is_jailbreak:
            return {
                "blocked": True,
                "reason": "JAILBREAK_ATTEMPT",
                "response": jailbreak_msg,
                "sanitized_text": cls.sanitize_pii(text)
            }
        
        # 3. Check Medical Advice Request
        is_med, med_msg = cls.check_medical_advice(text)
        if is_med:
            return {
                "blocked": True,
                "reason": "MEDICAL_DIAGNOSIS_REQUEST",
                "response": med_msg,
                "sanitized_text": cls.sanitize_pii(text)
            }
        
        # Safe
        return {
            "blocked": False,
            "reason": None,
            "response": None,
            "sanitized_text": cls.sanitize_pii(text)
        }
