# Visão do Produto - CitizenTech Mobilidade

> Substitua os campos entre colchetes pelos dados reais do grupo antes da entrega.

## Persona e problema

**Persona primária:** Marina, 32 anos, passageira de ônibus que trabalha em turnos e depende de transporte público para chegar ao trabalho. Ela precisa saber se há serviço no ponto consultado e qual linha pode usar, sem precisar instalar aplicativos ou interpretar dados técnicos. Marina não é gestora de tráfego e não usa este serviço para rastreamento em tempo real de veículos.

**Problema:** Passageiros perdem tempo e se expõem a deslocamentos desnecessários quando não conseguem consultar, de modo confiável, a situação de um ponto e suas linhas.

## Requisitos funcionais

- **RF-01:** listar pontos de parada com paginação `limit` e `offset`.
- **RF-02:** consultar um ponto pelo seu identificador e informar nome, endereço, status e linhas atendidas.
- **RF-03:** listar as linhas que atendem um ponto disponível.
- **RF-04:** responder uma pergunta curta sobre um ponto por meio de um assistente, somente usando os dados retornados pelo domínio.
- **RF-05:** informar erro padronizado quando o ponto não existir ou a consulta for inválida.

## Requisitos não funcionais mensuráveis

- **RNF-01 - Desempenho:** 95% das consultas de ponto devem terminar em menos de 500 ms, medido por log de latência no ambiente de homologação.
- **RNF-02 - Qualidade:** a cobertura de linhas do módulo `src/` deve ser de no mínimo 70%, verificada no CI.
- **RNF-03 - Disponibilidade:** o serviço deve alcançar 99% de disponibilidade mensal entre 6h e 22h, medida pelo monitoramento de health check.
- **RNF-04 - Segurança:** 0 chaves, tokens ou arquivos `.env` reais podem estar versionados, verificado na revisão do repositório antes da entrega.

## Critérios de aceite

1. **Dado** um ponto cadastrado e disponível, **quando** o cidadão consultar `GET /points/P001`, **então** receberá HTTP 200 com o status e as linhas do ponto.
2. **Dado** um identificador inexistente, **quando** o cidadão consultar `GET /points/XYZ`, **então** receberá HTTP 404 e o corpo `ErrorResponse`.
3. **Dado** pontos cadastrados, **quando** o cidadão chamar `GET /points?limit=1&offset=0`, **então** receberá no máximo um item e os campos de paginação.
4. **Dado** uma pergunta válida sobre um ponto existente, **quando** o cidadão enviar `POST /ask`, **então** receberá HTTP 200 e uma resposta baseada exclusivamente no status e nas linhas conhecidas.
5. **Dado** um corpo sem `pointId` ou com pergunta vazia, **quando** o cidadão enviar `POST /ask`, **então** receberá HTTP 422 e `ErrorResponse`.
6. **Dado** indisponibilidade do provedor de IA, **quando** uma pergunta válida for processada, **então** o serviço responderá HTTP 503 sem inventar dados.

## Fora de escopo

- Rastreamento GPS em tempo real, previsão de chegada ou compra de passagem.
- Cadastro, autenticação de usuários e alteração de dados de linhas/pontos.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| O modelo inventa uma linha ou horário | O adaptador atual gera texto fixo a partir dos dados do ponto; um futuro LLM precisará de validação de saída e retorno seguro em caso de falha. |
| Base de dados desatualizada | Registrar fonte e atualização; exibir apenas o status armazenado e abrir alerta se a atualização tiver mais de 24 h. |
| Pico de consultas degrada a resposta | Métrica p95 e alerta ao exceder 500 ms por 5 minutos; paginação nas listagens. |
