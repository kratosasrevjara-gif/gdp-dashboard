from __future__ import annotations

import unittest
from unittest.mock import patch

from compare_models import parse_models, render_side_by_side
from github_models_compare import CompareConfig, DEFAULT_MODELS, ModelResult, compare_models, mock_results, resolve_token


class CompareModelsTests(unittest.TestCase):
    def test_parse_models_uses_defaults(self):
        self.assertEqual(parse_models(None), DEFAULT_MODELS)

    def test_parse_models_parses_label_and_model(self):
        self.assertEqual(parse_models(["GPT=openai/gpt-4.1-mini"]), [("GPT", "openai/gpt-4.1-mini")])

    def test_mock_results_return_one_result_per_model(self):
        results = mock_results("teste curto", DEFAULT_MODELS)
        self.assertEqual(len(results), 4)
        self.assertTrue(all(item.ok for item in results))

    def test_render_side_by_side_includes_all_labels(self):
        rendered = render_side_by_side(mock_results("um prompt de teste", DEFAULT_MODELS), width=20)
        self.assertIn("GPT", rendered)
        self.assertIn("Claude", rendered)
        self.assertIn("Gemini", rendered)
        self.assertIn("DeepSeek", rendered)

    def test_resolve_token_prefers_explicit_value(self):
        with patch.dict("os.environ", {"GITHUB_TOKEN": "from_env"}, clear=True):
            self.assertEqual(resolve_token(" explicit "), "explicit")

    def test_compare_models_preserves_declared_order(self):
        config = CompareConfig(token="token", prompt="hello")
        models = [("First", "model-1"), ("Second", "model-2"), ("Third", "model-3")]

        def fake_infer(_config, model_id, label):
            return ModelResult(label=label, model_id=model_id, ok=True, content=f"{label}:{model_id}")

        with patch("github_models_compare.infer_via_github_models", side_effect=fake_infer):
            results = compare_models(config, models)

        self.assertEqual([item.label for item in results], ["First", "Second", "Third"])


if __name__ == "__main__":
    unittest.main()
