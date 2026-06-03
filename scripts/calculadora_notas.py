import json

def calcular_nota_final(notas: dict, motivo_anulacao: str = None) -> str:
    """
    Script atuando como ferramenta (Tool) para a IA validar e calcular a nota final.
    
    :param notas: Dicionário contendo as notas das 5 competências (ex: {"C1": 160, "C2": 120, ...})
    :param motivo_anulacao: String contendo o motivo da anulação, se houver (ex: "Fuga ao tema")
    :return: JSON formatado em string com o resultado final validado.
    """
    
    competencias_esperadas = ["C1", "C2", "C3", "C4", "C5"]
    notas_validas = [0, 40, 80, 120, 160, 200]
    
    resposta = {
        "status": "sucesso",
        "nota_final": 0,
        "detalhes": {},
        "mensagens": []
    }
    
    # 1. Regra de Anulação Total
    if motivo_anulacao:
        resposta["status"] = "anulada"
        resposta["mensagens"].append(f"Redação zerada por: {motivo_anulacao}")
        # Retorna imediatamente todas zeradas
        resposta["detalhes"] = {c: 0 for c in competencias_esperadas}
        return json.dumps(resposta, indent=2)

    # 2. Validação da estrutura das notas
    for comp in competencias_esperadas:
        if comp not in notas:
            return json.dumps({"status": "erro", "mensagens": [f"Competência faltante: {comp}"]})
        
        nota_atual = notas[comp]
        
        # 3. Validação dos valores permitidos no contrato
        if nota_atual not in notas_validas:
            return json.dumps({
                "status": "erro", 
                "mensagens": [f"Nota inválida para {comp}: {nota_atual}. Deve ser múltiplo de 40."]
            })
            
        resposta["detalhes"][comp] = nota_atual
    
    # 4. Cálculo Aritmético Garantido
    nota_total = sum(resposta["detalhes"].values())
    resposta["nota_final"] = nota_total
    
    return json.dumps(resposta, indent=2)

# Exemplo de teste local:
if __name__ == "__main__":
    exemplo_notas = {"C1": 160, "C2": 120, "C3": 120, "C4": 160, "C5": 200}
    resultado = calcular_nota_final(exemplo_notas)
    print("Resultado da Simulação:")
    print(resultado)
