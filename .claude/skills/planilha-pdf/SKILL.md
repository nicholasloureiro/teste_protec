---
name: planilha-pdf
description: Converter planilhas de cobrança (.xlsx/.xlsm/.csv) em relatório PDF neste repositório, subir a tela web, gerar a planilha de teste ou evoluir o conversor (novas colunas, totais, logo, destaque de vencidos). Use quando o pedido envolver planilha → PDF, a tela de upload, ou alterações em src/planilha_pdf.
---

# Planilha → PDF (sistema de cobrança)

Decisões de arquitetura em `docs/adr/` (0001 conversor, 0002 Postgres). Leia antes de trocar biblioteca ou estrutura.

## Usar

```bash
uv sync
docker compose up -d --build                  # Postgres (porta 5440) + tela em http://localhost:8000, guardando no banco
docker compose exec postgres psql -U cobranca -d cobranca    # ver os dados guardados
uv run planilha-pdf-tela                      # tela sem banco (sem DATABASE_URL não guarda nada)
uv run planilha-pdf-tela --rede               # libera na rede local (celular): http://<ip-da-máquina>:8000
uv run planilha-pdf arquivo.xlsx -o saida.pdf -t "Título"   # terminal
uv run python exemplos/gerar_planilha_teste.py              # recria exemplos/cobrancas_teste.xlsx
```

## Evoluir (fluxo obrigatório)

1. **Teste primeiro.** Escreva o cenário em Gherkin pt-BR (`# language: pt`) em `tests/features/*.feature`
   e os passos em `tests/test_*.py`. Rode `uv run pytest -q` e confirme que falha pelo motivo certo.
2. Implemente em `src/planilha_pdf/` até passar.
3. **Olhe o PDF**, não só os testes: gere a partir de `exemplos/cobrancas_teste.xlsx` e renderize
   (`pdftoppm -png -r 60 -f 1 -l 1 saida.pdf pag`) para conferir visualmente. `pypdf` extrai texto
   invisível — teste passando não prova que está legível.
4. Se mexeu na tela, suba com `docker compose up -d --build` e teste com
   `curl -F arquivo=@exemplos/cobrancas_teste.xlsx localhost:8000/converter -o t.pdf`.
5. Atualize o README, commit e `git push` para `origin main`
   (https://github.com/nicholasloureiro/teste_protec).

## Onde fica cada coisa

- `src/planilha_pdf/__init__.py` — `ler_planilha` (abas → linhas), `formatar` (datas dd/mm/aaaa, números 1.234,56), `gerar_pdf`, CLI.
- `src/planilha_pdf/web.py` — FastAPI: `GET /` (tela) e `POST /converter` (multipart `arquivo`, `titulo`) → PDF ou `400 {"erro": ...}`.
- `src/planilha_pdf/tela.html` — página única, HTML/CSS/JS puro, sem build.
- `src/planilha_pdf/banco.py` — esquema (`conversoes`, `linhas_planilha` com `jsonb`), `salvar_conversao`, `historico`. SQL direto com psycopg 3.
- `web.py` também expõe `GET /historico` → `{"ativo": bool, "conversoes": [...]}`.
- `tests/conftest.py` — fixture `contexto` e passos `Dado` compartilhados.
- `tests/test_banco.py` — sobe Postgres real com testcontainers (precisa do Docker); não use mock de banco.

## Armadilhas já encontradas

- **Cor do texto em células:** as células são `Paragraph`; o estilo do Paragraph ignora `TEXTCOLOR` do `TableStyle`.
  Para mudar cor/fonte de uma linha, use um estilo clonado (como `cabecalho` em `_tabela`).
- **Passos do pytest-bdd compartilhados** devem ficar em `tests/conftest.py`. Importar funções de passo de outro
  módulo de teste não as registra.
- **Fonte:** Helvetica (padrão do reportlab) cobre acentos do português, mas não emoji nem caracteres fora do Latin-1.
  Se aparecerem quadrados no PDF, registre uma TTF (ex.: DejaVuSans).
- **Planilhas com fórmulas:** lemos com `data_only=True`, que usa o valor salvo pelo Excel. Arquivo gerado por
  script e nunca aberto no Excel pode trazer fórmulas com valor vazio.
- **Celular não abre a tela:** sem `--rede` o servidor escuta só em 127.0.0.1. Com `--rede`, confira se o celular
  está no mesmo Wi-Fi (não nos dados móveis) e se o firewall (`ufw`) não bloqueia a porta 8000.
- **Mudança de esquema:** o esquema é `CREATE ... IF NOT EXISTS`, então alterar uma tabela existente não tem
  efeito sozinho. Escreva um `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` no `ESQUEMA` (sem ferramenta de migração, ADR 0002).
- **`pkill -f planilha-pdf-tela`** mata o próprio shell que rodou o comando (a linha contém o padrão). Pare a tela
  pelo PID (`ss -ltnp | grep 8000`) ou com `docker compose down`.
- Dados de teste são **fictícios**; nunca versione planilha real de clientes (`*.pdf` já está no `.gitignore`).
