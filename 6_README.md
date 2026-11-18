# GS 2026.2 - CitizenTech Mobilidade

Projeto da turma **2CCPY-2026**, modalidade trio. Integrantes: **Henrique Boscoli - RM 563651**, **Joao Henrique - RM 563578** e **Tomazzo Canterucci - RM 565566**.

## Índice

1. [Visão de produto](1_visao_produto.md)
2. [Contrato OpenAPI](2_contrato_api.yaml)
3. [Arquitetura e ADRs](3_arquitetura.md)
4. [Evals e guardrails](5_evals_de_ia.md)
5. Slice executável: `4_slice/`

## Rastreabilidade dos testes

| Requisito | Evidência no slice |
|---|---|
| RF-02: consultar ponto | `test_get_existing_point_returns_contract_shape` |
| RF-01: listagem paginada | `test_list_points_honors_pagination` |
| RF-05: ponto inexistente | `test_missing_point_returns_404_error_shape` |
| RF-04: orientação com fatos conhecidos | `test_ask_returns_only_known_facts` |
| Pergunta acima de 300 caracteres | `test_question_longer_than_contract_limit_is_rejected` |
| Falha do assistente | `test_ask_uses_fake_unavailable_adapter_without_real_llm` |

Os dados do repositório são fictícios. Latência, disponibilidade, cobertura e alertas são metas de produção, não medições já comprovadas. O adaptador atual é determinístico e não chama um modelo de IA real.

## Executar e testar

Pré-requisito: Python 3.11+.

```powershell
cd 4_slice
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m src.api.app
```

Em outro terminal, uma requisição real:

```powershell
Invoke-RestMethod http://localhost:8000/points/P001
```

Resposta esperada: o ponto `P001`, com `status` `AVAILABLE` e linhas `101` e `205`.

## Validar o contrato

```powershell
python -m pip install openapi-spec-validator
python -m openapi_spec_validator ..\2_contrato_api.yaml
```

O OpenAPI foi escrito antes do slice. O endpoint implementado `GET /points/{pointId}` respeita o schema `Point`, e os testes verificam o formato completo da resposta e o erro 404.

## CI e evidência

O workflow em `.github/workflows/ci.yml` instala as dependências, executa o lint e os testes. A cópia em `4_slice/.github/workflows/ci.yml` compõe o entregável. Publiquem a pasta do projeto como raiz do repositório e insiram abaixo uma captura verdadeira da execução verde e o link do repositório.

> PENDENTE: adicionar print real do GitHub Actions verde; não fabricar essa evidência.

## Vídeo (até 3 minutos)

1. Cada integrante se apresenta; 2. mostrar a visão/contrato; 3. executar `pytest -q`; 4. chamar `GET /points/P001`; 5. explicar a porta `CitizenAssistant` e o fake de teste.
