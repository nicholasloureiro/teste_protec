# language: pt
Funcionalidade: Tela para converter planilha em PDF
  Como responsável pela cobrança
  Quero enviar a planilha por uma tela no navegador
  Para baixar o PDF sem usar o terminal

  Cenário: Abrir a tela
    Quando eu abrir a tela
    Então vejo o campo para enviar a planilha

  Cenário: Enviar planilha e baixar o PDF
    Dado uma planilha Excel com os clientes "Maria Souza" e "João Lima"
    Quando eu enviar a planilha pela tela
    Então recebo um PDF para download chamado "clientes.pdf"
    E o PDF contém o texto "Maria Souza"

  Cenário: Enviar arquivo em formato errado
    Dado um arquivo "dados.txt"
    Quando eu enviar a planilha pela tela
    Então a tela mostra o erro "Formato não suportado"
