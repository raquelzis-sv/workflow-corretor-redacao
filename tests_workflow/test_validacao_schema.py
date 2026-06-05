import os
import unittest

try:
    from scripts.validacao_schema import validar_pontos_interesse
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from scripts.validacao_schema import validar_pontos_interesse


class TestValidacaoSchema(unittest.TestCase):
    def test_payload_valido(self):
        data = {
            "redacao_id": "teste",
            "pontos_interesse": [
                {
                    "tipo": "desvio_ortografico",
                    "trecho": "exemplo",
                    "comentario": "comentário",
                    "gravidade": "leve",
                }
            ],
        }
        ok, erros = validar_pontos_interesse(data)
        self.assertTrue(ok, erros)

    def test_payload_invalido(self):
        data = {"pontos_interesse": "nao_e_lista"}
        ok, erros = validar_pontos_interesse(data)
        self.assertFalse(ok)
        self.assertGreater(len(erros), 0)


if __name__ == "__main__":
    unittest.main()
