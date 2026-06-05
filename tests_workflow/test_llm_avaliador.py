import json
import os
import unittest

try:
    from scripts.llm_avaliador import (
        _parse_json_resposta,
        carregar_contrato,
        resumo_contrato_para_prompt,
        ollama_disponivel,
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from scripts.llm_avaliador import (
        _parse_json_resposta,
        carregar_contrato,
        resumo_contrato_para_prompt,
        ollama_disponivel,
    )


class TestLlmAvaliador(unittest.TestCase):
    def test_parse_json_com_fence(self):
        raw = '```json\n{"notas": {"C1": 120}}\n```'
        data = _parse_json_resposta(raw)
        self.assertEqual(data["notas"]["C1"], 120)

    def test_carregar_contrato(self):
        contrato = carregar_contrato()
        self.assertEqual(len(contrato["competencias"]), 5)
        resumo = resumo_contrato_para_prompt(contrato)
        self.assertIn("C1", resumo)

    def test_ollama_disponivel_quando_desabilitado(self):
        os.environ["OLLAMA_DISABLED"] = "1"
        try:
            self.assertFalse(ollama_disponivel())
        finally:
            del os.environ["OLLAMA_DISABLED"]


if __name__ == "__main__":
    unittest.main()
