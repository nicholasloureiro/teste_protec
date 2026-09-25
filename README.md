# teste_protec

Sistema de cobrança da empresa.

## Objetivo

Centralizar e automatizar o processo de cobrança: registro de débitos, acompanhamento de vencimentos e controle de pagamentos recebidos.

## Planilha → PDF

Converte uma planilha de cobrança (`.xlsx`, `.xlsm` ou `.csv`) em um relatório PDF:
cada aba vira uma seção com tabela, datas no formato `dd/mm/aaaa`, valores como `1.234,56`,
cabeçalho repetido a cada página e rodapé com data de geração e número da página.

### Instalação

Requer [uv](https://docs.astral.sh/uv/) e Python 3.10+.

```bash
uv sync
```

### Uso pela tela

```bash
uv run planilha-pdf-tela
```

Abra http://localhost:8000, escolha ou arraste a planilha, informe um título (opcional) e clique em **Gerar PDF**.

Para testar, use a planilha de exemplo `exemplos/cobrancas_teste.xlsx` (dados fictícios, abas Agosto e Setembro de 2026).
Para gerá-la de novo: `uv run python exemplos/gerar_planilha_teste.py`.

### Uso pelo terminal

```bash
uv run planilha-pdf cobrancas.xlsx                                   # gera cobrancas.pdf
uv run planilha-pdf cobrancas.csv -o relatorio.pdf -t "Cobrança Outubro"
```

Pelo Python:

```python
from planilha_pdf import gerar_pdf
gerar_pdf("cobrancas.xlsx", "relatorio.pdf", titulo="Cobrança Outubro")
```

CSV com separador `;`, `,` ou tab é detectado automaticamente.

### Testes

Os critérios de aceite estão em português em `tests/features/gerar_pdf.feature`.

```bash
uv run pytest
```

## Estrutura

Decisões de arquitetura em [`docs/adr/`](docs/adr/). Para agentes (Claude Code), o passo a passo de uso e
evolução está no skill [`.claude/skills/planilha-pdf`](.claude/skills/planilha-pdf/SKILL.md).

```
.
├── .claude/skills/planilha-pdf/       # skill do Claude Code para este projeto
├── docs/adr/                          # registros de decisão de arquitetura
├── src/planilha_pdf/
│   ├── __init__.py                    # leitura da planilha, geração do PDF e CLI
│   ├── web.py                         # tela web (FastAPI)
│   └── tela.html                      # página da tela
├── exemplos/
│   ├── cobrancas_teste.xlsx           # planilha fictícia para testes
│   └── gerar_planilha_teste.py        # gera a planilha de teste
└── tests/
    ├── features/                      # cenários de aceite (Gherkin pt-BR)
    ├── conftest.py                    # passos compartilhados
    ├── test_gerar_pdf.py
    └── test_tela.py
```

## Como contribuir

1. Crie uma branch a partir de `main`.
2. Faça commits pequenos e descritivos.
3. Abra um Pull Request para revisão antes do merge.
