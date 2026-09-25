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

  Cenário: Por padrão a tela só abre neste computador
    Quando eu iniciar a tela sem opções
    Então ela aceita conexões apenas de "127.0.0.1"

  Cenário: Liberar a tela na rede local para acessar pelo celular
    Quando eu iniciar a tela com a opção "--rede"
    Então ela aceita conexões apenas de "0.0.0.0"
