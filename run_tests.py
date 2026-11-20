import sys
import unittest
from tests.test_guardrails import (
    test_crisis_detection,
    test_jailbreak_detection,
    test_medical_advice_detection,
    test_pii_sanitization,
    test_benign_support_prompt
)
from tests.test_database import test_database_crud
from tests.test_rag import test_rag_retrieval_grounding, test_rag_retrieval_cbt
from tests.test_api import test_health_endpoint, test_session_lifecycle

class SystemVerificationTests(unittest.TestCase):
    def test_01_guardrails_crisis(self):
        test_crisis_detection()

    def test_02_guardrails_jailbreak(self):
        test_jailbreak_detection()

    def test_03_guardrails_medical(self):
        test_medical_advice_detection()

    def test_04_guardrails_pii(self):
        test_pii_sanitization()

    def test_05_guardrails_benign(self):
        test_benign_support_prompt()

    def test_06_database_crud(self):
        test_database_crud()

    def test_07_rag_grounding(self):
        test_rag_retrieval_grounding()

    def test_08_rag_cbt(self):
        test_rag_retrieval_cbt()

    def test_09_api_health(self):
        test_health_endpoint()

    def test_10_api_session_lifecycle(self):
        test_session_lifecycle()

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(SystemVerificationTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
