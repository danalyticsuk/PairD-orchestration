import unittest
import requests
from fastapi.testclient import TestClient
from app.app import app
from app.routes.input_ingestion import InputGuardrails
from app.PIIBlocker import PIIBlocker


# Testing Classes - one per endpoint

class TestIngestQueryEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.__enter__().close()

    def test_valid_input(self):
        """
        This test ensures the user query is ingested successfully
        """
        data = {"query": "Valid user query"}
        response = self.client.post("/ingest_query", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Query ingested successfully."})

    def test_missing_query(self):
        """
        This test ensures a missing query returns the correct error message
        """
        data = {}  # Missing "query" field
        response = self.client.post("/ingest_query", json=data)
        self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity for validation error

    def test_empty_query(self):
        """
        This test ensures an empty query returns the correct error message
        """
        data = {"query": ""}
        response = self.client.post("/ingest_query", json=data)
        self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity for validation error

    # Add more test cases to cover specific guardrails

    def test_no_pii_detected(self):
        """
        This test ensures no PII is detected in input strings where none exists
        """
        input_guardrails = InputGuardrails("Input test")
        input_guardrails.pii_blocker()

        self.assertEqual(input_guardrails.blocked_user_query, "Guardrails applied to: Input test")
        self.assertEqual(input_guardrails.pii_dict, [])
        self.assertEqual(input_guardrails.pii_detected, False)

    def test_pii_detected(self):
        """
        This test ensures PII is detected & recorded correctly in strings which include PII
        """
        input_guardrails = InputGuardrails("email: firstnamesurname@email.co.uk, phone: 01234567890")
        input_guardrails.pii_blocker()
        expected_blocked_string = f"Guardrails applied to: email: {input_guardrails.pii_dict[0][1]}, phone: {input_guardrails.pii_dict[1][1]}"
        expected_pii_dict = [['firstnamesurname@email.co.uk', '[EMAIL-0]', True], ['01234567890', '[PHONE-0]', True]]

        self.assertEqual(input_guardrails.blocked_user_query, expected_blocked_string)
        self.assertEqual(input_guardrails.pii_dict, expected_pii_dict)
        self.assertEqual(input_guardrails.pii_detected, True)
    

class TestIngestPostEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.__enter__().close()

    def test_get_processed_query_found(self):
        """
        This test ensures the get request successfully returns the posted query
        """
        self.client.post("/ingest_query", json={"query": "User query is found"})
        response = self.client.get("/processed_query")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"edited_query": "Guardrails applied to: User query is found"})


class TestIngestLLMResponseEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.__enter__().close()

    def test_valid_llm_response(self):

        llm_response = {"llm_response": "email: [EMAIL-0], phone: [PHONE-0]"}
        input = "email: firstnamesurname@email.co.uk, phone: 01234567890"

        pii_blocker = PIIBlocker()
        pii_blocker.block(input)

        reapplied_response = pii_blocker.remask(llm_response["llm_response"])
        response = self.client.post("/ingest_llm_response", json=llm_response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "LLM Response ingested successfully."})
        self.assertEqual(reapplied_response, input)

    def test_missing_llm_response(self):
        data = {}  # Missing "llm_response" field
        response = self.client.post("/ingest_llm_response", json=data)
        self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity for validation error


if __name__ == '__main__':
    unittest.main()