# ADR 0001 — Conversor de planilha para PDF

- **Status:** aceito
- **Data:** 2026-09-25

## Contexto

A área de cobrança trabalha com planilhas (.xlsx/.csv) e precisa enviar ou arquivar esses dados como PDF,
sem depender do Excel instalado e sem saber usar terminal. O produto está no início: o formato das planilhas
ainda não está fixo e a equipe é pequena, então a solução precisa ser simples de manter e de rodar.

## Decisão

1. **Python 3.10+ gerenciado com `uv`**, empacotado como `planilha-pdf` com dois comandos:
   `planilha-pdf` (terminal) e `planilha-pdf-tela` (tela web).
2. **Leitura com `openpyxl` e `csv` da biblioteca padrão**, sem pandas. Precisamos só de linhas e células;
   pandas traria dependência pesada e conversões de tipo indesejadas (datas e CNPJs viram outra coisa).
   O separador do CSV (`;`, `,`, tab) é detectado com `csv.Sniffer`.
3. **PDF com `reportlab`** (Platypus: `SimpleDocTemplate` + `Table`). Gera PDF em Python puro, sem
   dependências de sistema, com quebra de página e cabeçalho repetido automáticos.
4. **Layout genérico:** A4 paisagem, uma seção por aba, datas `dd/mm/aaaa`, números `1.234,56`, rodapé com
   data de geração e página. Nada depende de nomes de colunas, porque o formato ainda não está definido.
5. **Tela com FastAPI + uma página HTML estática** (`tela.html`, JS puro). Um endpoint `POST /converter`
   recebe o arquivo e devolve o PDF; o arquivo é processado em diretório temporário e descartado.
   Sem framework de frontend nem etapa de build.
6. **Testes BDD em português** (`pytest-bdd`, Gherkin `# language: pt`), escritos antes do código, para que o
   negócio consiga ler os critérios de aceite.

## Alternativas consideradas

- **pandas + `DataFrame.to_html` + WeasyPrint:** HTML/CSS dá mais liberdade visual, mas WeasyPrint exige
  bibliotecas de sistema (Pango/Cairo), complicando a instalação e o deploy.
- **LibreOffice headless (`soffice --convert-to pdf`):** fidelidade total ao Excel, mas exige LibreOffice no
  servidor, é lento e o resultado depende da formatação de cada planilha.
- **Streamlit para a tela:** rápido de fazer, mas adiciona uma dependência grande e dá menos controle sobre o
  download e as mensagens de erro do que um endpoint FastAPI.
- **React/Next.js:** exagero para uma tela com um campo de upload.

## Consequências

- Instalação é só `uv sync`; roda igual em Linux, macOS e Windows.
- O PDF **não** reproduz a formatação do Excel (cores, larguras, células mescladas); ele reconstrói uma tabela
  padronizada. Isso é intencional para uniformizar os relatórios.
- Colunas têm largura igual; planilhas com muitas colunas ou textos longos ficam apertadas. Se virar problema,
  calcular largura proporcional ao conteúdo.
- Fórmulas são lidas pelo valor salvo (`data_only=True`); planilha nunca aberta no Excel pode vir com valores vazios.
- A tela roda localmente e **não tem autenticação**. Antes de publicar para a empresa (ex.: Railway), é preciso
  adicionar login e limite de tamanho de upload.
- Quando o formato das planilhas de cobrança for definido, recursos específicos (totais, destaque de vencidos,
  logo) entram em um novo ADR.
