# language: pt
Funcionalidade: Guardar as conversões no Postgres
  Como responsável pela cobrança
  Quero que cada planilha convertida fique guardada no banco
  Para consultar depois o que foi enviado, mesmo sem o arquivo original

  Cenário: A conversão e as linhas da planilha ficam guardadas
    Dado uma planilha Excel com os clientes "Maria Souza" e "João Lima"
    Quando eu enviar a planilha pela tela com o banco ligado
    Então a conversão de "clientes.xlsx" fica registrada com 2 linhas
    E a linha do cliente "Maria Souza" fica guardada com o vencimento "2026-10-05" e o valor 150.0

  Cenário: O histórico mostra as conversões feitas
    Dado uma planilha Excel com os clientes "Maria Souza" e "João Lima"
    Quando eu enviar a planilha pela tela com o banco ligado
    E eu consultar o histórico
    Então vejo "clientes.xlsx" no histórico

  Cenário: Arquivo recusado não é guardado
    Dado um arquivo "dados.txt"
    Quando eu enviar a planilha pela tela com o banco ligado
    Então nenhuma conversão fica registrada
