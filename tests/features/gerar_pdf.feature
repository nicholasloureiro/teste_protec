# language: pt
Funcionalidade: Gerar PDF a partir de uma planilha
  Como responsável pela cobrança
  Quero transformar uma planilha em PDF
  Para enviar ou arquivar o relatório sem depender do Excel

  Cenário: Planilha Excel vira PDF com os dados
    Dado uma planilha Excel com os clientes "Maria Souza" e "João Lima"
    Quando eu gerar o PDF
    Então o arquivo PDF é criado
    E o PDF contém o texto "Maria Souza"
    E o PDF contém o texto "João Lima"

  Cenário: Cada aba da planilha vira uma seção do PDF
    Dado uma planilha Excel com as abas "Janeiro" e "Fevereiro"
    Quando eu gerar o PDF
    Então o PDF contém o texto "Janeiro"
    E o PDF contém o texto "Fevereiro"

  Cenário: Planilha CSV também é aceita
    Dado uma planilha CSV com o cliente "Ana Pereira"
    Quando eu gerar o PDF
    Então o PDF contém o texto "Ana Pereira"

  Cenário: Formato não suportado é recusado
    Dado um arquivo "dados.txt"
    Quando eu tentar gerar o PDF
    Então recebo o erro "Formato não suportado"
