"""Unit tests for Deal Intelligence Agent backend.

Covers:
- LLM fallback and defensive JSON parsing
- Empty-recall handling and graceful degradation
- Zero-calls deal edge case
- CONTRACT.md shape compliance
"""

from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure backend directory is in sys.path
_backend_dir = str(Path(__file__).resolve().parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi.testclient import TestClient

from agents import brief_agent, coach_agent
from band_adapter import handle_band_message
from llm import _clean_json_text, call_llm_json
from main import app
from storage import get_deal, save_deal


class TestLLMFallback(unittest.TestCase):
    def test_clean_json_text_markdown_fence(self):
        """Verify markdown code fences are stripped cleanly."""
        raw = "```json\n{\"key\": \"value\"}\n```"
        self.assertEqual(_clean_json_text(raw), "{\"key\": \"value\"}")

        raw_extra = "Here is the result:\n```json\n{\"status\": \"ok\"}\n```\nHope that helps!"
        self.assertEqual(_clean_json_text(raw_extra), "{\"status\": \"ok\"}")

    @patch("llm._invoke_groq")
    def test_llm_json_fallback_on_failure(self, mock_invoke):
        """Verify that when primary LLM fails, fallback model or fallback_value is returned."""
        # Simulate primary model throwing an exception on every attempt
        mock_invoke.side_effect = RuntimeError("Service Unavailable")

        fallback = {"test_status": "fallback_applied"}
        result = call_llm_json("Return status", fallback_value=fallback)
        self.assertEqual(result, fallback)

    @patch("llm._invoke_groq")
    def test_llm_json_secondary_model_recovery(self, mock_invoke):
        """Verify cascade: primary model fails, secondary model succeeds."""
        # Fail first 2 attempts (primary model), succeed on 3rd attempt (fallback model)
        mock_invoke.side_effect = [
            RuntimeError("Rate limit"),
            RuntimeError("Rate limit"),
            "{\"recovered\": true}",
        ]
        result = call_llm_json("Test recovery")
        self.assertEqual(result.get("recovered"), True)


class TestEmptyRecallAndEdgeCases(unittest.TestCase):
    def setUp(self):
        # Create an empty deal with 0 calls
        save_deal("test-zero-calls", "Zero Calls Inc", 50000, calls=[])

    def test_zero_calls_deal_brief(self):
        """A deal with zero calls should return empty lists without raising an error."""
        brief = brief_agent("test-zero-calls", memory="on")
        self.assertEqual(brief["memory_used"], False)
        self.assertEqual(brief["recalled_facts"], [])
        self.assertEqual(brief["open_objections"], [])
        self.assertEqual(brief["stakeholders"], [])
        self.assertEqual(brief["promises"], [])
        self.assertIn("No call history", brief["brief"])

    @patch("agents.recall_facts")
    @patch("agents.coach_agent")
    def test_empty_recall_path(self, mock_coach, mock_recall):
        """When Hindsight recall returns nothing, brief_agent gracefully constructs a brief."""
        # Deal with 1 call
        deal_id = "test-empty-recall-deal"
        save_deal(
            deal_id,
            "Recall Edge Corp",
            75000,
            calls=[
                {
                    "call_no": 1,
                    "date": "2026-11-01",
                    "participants": ["Rep", "Buyer"],
                    "transcript": "Rep: Hello Buyer. Buyer: We are reviewing the budget.",
                }
            ],
        )

        mock_recall.return_value = []
        mock_coach.return_value = {"playbook_tips": []}

        brief = brief_agent(deal_id, memory="on")
        self.assertTrue(brief["memory_used"])
        self.assertIsInstance(brief["recalled_facts"], list)
        self.assertEqual(len(brief["recalled_facts"]), 0)
        self.assertIn("brief", brief)
        self.assertIn("open_objections", brief)
        self.assertIn("stakeholders", brief)
        self.assertIn("promises", brief)

    @patch("agents.recall_facts")
    @patch("agents.reflect_facts")
    def test_coach_agent_empty_playbook(self, mock_reflect, mock_recall):
        """When playbook bank is completely empty, coach_agent returns empty lists."""
        mock_recall.return_value = []
        mock_reflect.return_value = ""

        coach_data = coach_agent()
        self.assertEqual(coach_data["playbook_tips"], [])
        self.assertEqual(coach_data["insights"], [])
        self.assertEqual(coach_data["mental_models"], [])


class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        save_deal(
            "deal-endpoint-test",
            "Test Account",
            120000,
            calls=[
                {
                    "call_no": 1,
                    "date": "2026-11-01",
                    "participants": ["Rep", "Buyer"],
                    "transcript": "Rep: Hello. Buyer: We need a quote.",
                }
            ],
        )

    def test_health_endpoint(self):
        """GET /health must return {ok: true}."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})

    def test_deals_list_endpoint(self):
        """GET /deals must return list of deals with CONTRACT fields."""
        res = self.client.get("/deals")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        if len(data) > 0:
            deal = data[0]
            for field in ["deal_id", "company", "value", "stage", "calls_count", "outcome"]:
                self.assertIn(field, deal)

    @patch("main.ensure_bank")
    def test_create_deal_endpoint(self, mock_ensure_bank):
        """POST /deals creates a new deal and returns {deal_id}."""
        payload = {"company": "Acme Widgets", "value": 75000}
        res = self.client.post("/deals", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("deal_id", data)
        self.assertTrue(data["deal_id"].startswith("deal-"))

    @patch("agents.ensure_bank")
    @patch("agents.retain_fact")
    def test_create_call_endpoint(self, mock_retain, mock_ensure):
        """POST /deals/{id}/calls ingests a call and returns {retained: true}."""
        call_payload = {
            "call_no": 2,
            "date": "2026-11-05",
            "participants": ["Alice", "Bob"],
            "transcript": "Alice: Did you review the proposal? Bob: Yes, reviewing now.",
        }
        res = self.client.post("/deals/deal-endpoint-test/calls", json=call_payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"retained": True})

    @patch("agents.call_llm_json")
    def test_brief_memory_off(self, mock_llm_json):
        """GET /deals/{id}/brief?memory=off uses only latest call without memory."""
        mock_llm_json.return_value = {
            "brief": "Summary based only on latest call.",
            "open_objections": [{"text": "Price high", "raised_in_call": 1, "by": "Buyer"}],
            "stakeholders": [{"name": "Buyer", "role": "Buyer", "stance": "Neutral", "concerns": "Price"}],
            "promises": [{"text": "Send quote", "made_by": "Rep", "due": "Tomorrow"}],
        }
        res = self.client.get("/deals/deal-endpoint-test/brief?memory=off")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["memory_used"])
        self.assertEqual(data["recalled_facts"], [])
        self.assertIn("brief", data)
        self.assertIn("open_objections", data)
        self.assertIn("stakeholders", data)
        self.assertIn("promises", data)
        self.assertIn("playbook_tips", data)

    @patch("agents.recall_facts")
    @patch("agents.coach_agent")
    @patch("agents.call_llm_json")
    def test_brief_memory_on(self, mock_llm_json, mock_coach, mock_recall):
        """GET /deals/{id}/brief?memory=on uses memory recall and playbook tips."""
        mock_recall.return_value = [{"text": "Budget is frozen", "context": "Call 1"}]
        mock_coach.return_value = {
            "playbook_tips": [{"tip": "Propose phased pilot", "evidence": "Won 80% of deals"}]
        }
        mock_llm_json.return_value = {
            "brief": "Deep historical brief across calls.",
            "open_objections": [{"text": "Budget freeze", "raised_in_call": 1, "by": "CFO"}],
            "stakeholders": [{"name": "Sarah", "role": "CFO", "stance": "Cautious", "concerns": "Budget"}],
            "promises": [{"text": "Provide pilot terms", "made_by": "Rep", "due": "Friday"}],
        }
        res = self.client.get("/deals/deal-endpoint-test/brief?memory=on")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["memory_used"])
        self.assertIsInstance(data["recalled_facts"], list)
        self.assertIn("brief", data)
        self.assertIn("open_objections", data)
        self.assertIn("stakeholders", data)
        self.assertIn("promises", data)
        self.assertIn("playbook_tips", data)

    @patch("main.call_llm_text")
    def test_followup_endpoint(self, mock_llm_text):
        """POST /deals/{id}/followup returns {email: ...}."""
        mock_llm_text.return_value = "Dear Buyer, thank you for your time today..."
        res = self.client.post("/deals/deal-endpoint-test/followup", json={"memory": "off"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("email", data)
        self.assertEqual(data["email"], "Dear Buyer, thank you for your time today...")

    @patch("main.ensure_bank")
    @patch("main.ensure_playbook_mental_models")
    @patch("main.retain_fact")
    def test_outcome_endpoint(self, mock_retain, mock_models, mock_ensure):
        """POST /deals/{id}/outcome records result and returns {ok: true}."""
        payload = {
            "result": "won",
            "objections_handled": ["Pricing concern", "ERP sync latency"],
            "notes": "Offered 60-day phased pilot to secure contract.",
        }
        res = self.client.post("/deals/deal-endpoint-test/outcome", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})
        deal = get_deal("deal-endpoint-test")
        self.assertEqual(deal["outcome"], "won")

    @patch("main.coach_agent")
    def test_playbook_insights_endpoint(self, mock_coach):
        """GET /playbook/insights returns insights and mental models."""
        mock_coach.return_value = {
            "insights": [{"text": "Early security reviews increase win-rate by 28%", "confidence": 0.89}],
            "mental_models": [{"name": "CFO Alignment", "summary": "De-risk upfront payments"}],
        }
        res = self.client.get("/playbook/insights")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("insights", data)
        self.assertIn("mental_models", data)

    @patch("main.ingest_agent")
    def test_admin_seed_endpoint(self, mock_ingest):
        """POST /admin/seed loads deals and calls and returns counts."""
        mock_ingest.return_value = {"retained": True}
        res = self.client.post("/admin/seed")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("deals_loaded", data)
        self.assertIn("calls_retained", data)
        self.assertGreater(data["deals_loaded"], 0)


class TestBandAdapter(unittest.TestCase):
    @patch("band_adapter.ingest_agent")
    def test_band_ingest_routing(self, mock_ingest):
        mock_ingest.return_value = {"retained": True}
        msg = '{"deal_id": "deal-1", "transcript": "Client discussion"}'
        res = handle_band_message("@ingest", msg)
        self.assertIn("[@ingest]", res)

    @patch("band_adapter.brief_agent")
    def test_band_brief_routing(self, mock_brief):
        mock_brief.return_value = {
            "brief": "Test brief summary.",
            "open_objections": [],
            "stakeholders": [],
            "playbook_tips": [],
        }
        res = handle_band_message("@brief", "deal-1 memory=on")
        self.assertIn("Pre-Call Brief for deal-1", res)

    @patch("band_adapter.coach_agent")
    def test_band_coach_routing(self, mock_coach):
        mock_coach.return_value = {
            "playbook_tips": [{"tip": "Align with CFO early", "evidence": "High win rate"}],
            "insights": [{"text": "Pattern observed", "confidence": 0.9}],
            "mental_models": [{"name": "Model 1", "summary": "Summary 1"}],
        }
        res = handle_band_message("@coach", "How to close deals?")
        self.assertIn("Playbook Coach Recommendations", res)


if __name__ == "__main__":
    unittest.main()
