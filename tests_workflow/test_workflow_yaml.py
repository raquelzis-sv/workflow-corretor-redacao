import os
import unittest

import yaml

WORKFLOW_PATH = os.path.join(
    os.path.dirname(__file__), "..", "workflow.yaml"
)


class TestWorkflowYaml(unittest.TestCase):
    def test_arquivo_existe_e_parseia(self):
        self.assertTrue(os.path.exists(WORKFLOW_PATH))
        with open(WORKFLOW_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["workflow"]["id"], "correcao-redacao-enem")

    def test_etapas_tem_sete_passos(self):
        with open(WORKFLOW_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        steps = data["steps"]
        ids = [s["id"] for s in steps]
        self.assertIn("extract_text", ids)
        self.assertIn("llm_extraction", ids)
        self.assertIn("score_calculation", ids)
        self.assertEqual(len(steps), 7)

    def test_pop_definido(self):
        with open(WORKFLOW_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.assertIn("processo_manual_atual", data["pop"])


if __name__ == "__main__":
    unittest.main()
