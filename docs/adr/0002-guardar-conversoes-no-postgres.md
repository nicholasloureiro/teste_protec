# ADR 0002 — Guardar as conversões no Postgres

- **Status:** aceito
- **Data:** 2026-09-25

## Contexto

Até aqui a tela só convertia: a planilha era descartada depois de gerar o PDF. A cobrança precisa consultar
depois o que foi enviado (quando, qual arquivo, quais clientes e valores), sem depender de alguém guardar o
arquivo original. O formato das planilhas ainda não está definido (ADR 0001).

## Decisão

1. **Postgres 16** como banco, configurado pela variável `DATABASE_URL`. Sem ela, a tela funciona como antes e
   não guarda nada (útil para uso local e para os testes que não precisam de banco).
2. **Duas tabelas:**
   - `conversoes`: uma linha por planilha convertida (arquivo, título, tamanho, nº de abas e de linhas, data).
   - `linhas_planilha`: uma linha por linha de dados, com a aba, a posição e os valores em **`jsonb`**
     (`{"Cliente": ..., "Valor (R$)": 2446.49, "Vencimento": "2026-08-12T00:00:00"}`).
     Números continuam números; datas viram texto ISO 8601.
3. **`jsonb` em vez de colunas fixas**, porque as colunas das planilhas ainda variam. Quando o layout de
   cobrança for fixado, criaremos uma tabela tipada (`cobrancas` com cliente, documento, vencimento, valor,
   situação) alimentada a partir daqui, em novo ADR.
4. **SQL direto com `psycopg` 3**, sem ORM. São três consultas; um ORM e uma ferramenta de migração seriam mais
   código do que o problema. O esquema é idempotente (`CREATE ... IF NOT EXISTS`) e aplicado quando a tela inicia.
5. **Tudo ou nada:** a conversão e suas linhas são gravadas numa única transação. Se o banco falhar, a tela
   responde erro 503 em vez de entregar o PDF fingindo que guardou.
6. **Testes contra Postgres real** via `testcontainers` (sobe um container descartável). Nada de mock de banco.
7. **Ambiente local com `docker compose`** (Postgres + tela). Em produção no Azure:
   Azure Database for PostgreSQL – Flexible Server, com a URL guardada como *secret* do Container App.

## Alternativas consideradas

- **SQLite:** zero infraestrutura, mas no Azure Container Apps o disco do container é descartável e há várias
  réplicas; perderíamos dados.
- **Guardar só o arquivo original (Blob Storage):** simples, mas não permite consultar clientes e valores sem
  abrir planilha por planilha.
- **SQLAlchemy + Alembic:** justificável quando houver várias tabelas tipadas e mudanças de esquema frequentes.
  Revisitar junto com a tabela `cobrancas`.

## Consequências

- Consultas por cliente/valor já são possíveis: `SELECT * FROM linhas_planilha WHERE dados->>'Cliente' = '...'`.
  Para volume grande, criar índice GIN em `dados` ou índices de expressão nas chaves mais buscadas.
- Os nomes das chaves no `jsonb` são os cabeçalhos da planilha: se uma planilha usar "Valor" e outra
  "Valor (R$)", ficam diferentes. Isso será resolvido na tabela tipada.
- Dados de clientes (nomes, CPF/CNPJ) passam a ficar armazenados: o banco precisa de acesso restrito, backup, e
  a tela precisa de login antes de ir para a internet (ADR 0001).
- A mesma planilha enviada duas vezes gera dois registros. Deduplicar (ex.: por hash do arquivo) fica para quando
  houver necessidade real.
