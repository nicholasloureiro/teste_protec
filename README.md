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

### Uso

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

```
.
├── src/planilha_pdf/__init__.py       # leitura da planilha, geração do PDF e CLI
└── tests/
    ├── features/gerar_pdf.feature     # cenários de aceite (Gherkin pt-BR)
    └── test_gerar_pdf.py              # implementação dos passos
```

## Como contribuir

1. Crie uma branch a partir de `main`.
2. Faça commits pequenos e descritivos.
3. Abra um Pull Request para revisão antes do merge.
