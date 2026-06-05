---
description: Correção de redação, a partir do documento de texto e temas
---

# Workflow Agentic: Corretor de Redação (Executor YAML)

**Você (o Agente)** atua como o orquestrador principal deste fluxo. O professor determinou que a lógica de negócio principal e as etapas estão declaradas no arquivo estruturado do projeto (`workflow.yaml`).

## Regra de Orquestração
Quando o usuário invocar o comando `/corretor` seguido do caminho da redação e do tema:
1. **LEIA O MAPA:** Sua primeira ação OBRIGATÓRIA é usar a ferramenta `view_file` para ler o conteúdo de `docs/workflow.yaml`.
2. **SIGA OS STEPS:** Compreenda os `steps` (do step_1 ao step_5) definidos no YAML e execute cada um deles em ordem estrita.
3. **USE AS TOOLS DESIGNADAS:** Se um passo exigir que você utilize uma `tool` específica (ex: `llm_avaliador.py` para a IA, ou `calculadora_notas.py` para validação matemática), use a ferramenta `run_command` com código Python ou Bash para acionar essas ferramentas locais e coletar os `outputs` exigidos.
4. **PASSE O BASTÃO:** Garanta que a saída (`output`) de um passo seja o insumo primário (`input`) do próximo passo.

Dessa forma, o workflow fica dinâmico e 100% atrelado ao que está documentado no `.yaml`, que é a arquitetura desejada! Ao final da execução de todos os passos, forneça ao usuário o link para o relatório gerado.
