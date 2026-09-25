import io

from fastapi.testclient import TestClient
from pypdf import PdfReader
from pytest_bdd import parsers, scenarios, then, when

from planilha_pdf.web import app, endereco

scenarios("features/tela.feature")

cliente = TestClient(app)


@when("eu abrir a tela")
def abrir_tela(contexto):
    contexto["resposta"] = cliente.get("/")


@then("vejo o campo para enviar a planilha")
def campo_upload(contexto):
    assert contexto["resposta"].status_code == 200
    assert 'type="file"' in contexto["resposta"].text


@when("eu enviar a planilha pela tela")
def enviar(contexto):
    entrada = contexto["entrada"]
    contexto["resposta"] = cliente.post(
        "/converter", files={"arquivo": (entrada.name, entrada.read_bytes())}, data={"titulo": ""}
    )


@then(parsers.parse('recebo um PDF para download chamado "{nome}"'))
def recebo_pdf(contexto, nome):
    r = contexto["resposta"]
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert nome in r.headers["content-disposition"]


@then(parsers.parse('o PDF contém o texto "{texto}"'))
def pdf_contem(contexto, texto):
    reader = PdfReader(io.BytesIO(contexto["resposta"].content))
    assert texto in "\n".join(p.extract_text() for p in reader.pages)


@then(parsers.parse('a tela mostra o erro "{mensagem}"'))
def mostra_erro(contexto, mensagem):
    r = contexto["resposta"]
    assert r.status_code == 400
    assert mensagem in r.json()["erro"]


@when("eu iniciar a tela sem opções")
def iniciar_sem_opcoes(contexto):
    contexto["host"], _ = endereco([])


@when(parsers.parse('eu iniciar a tela com a opção "{opcao}"'))
def iniciar_com_opcao(contexto, opcao):
    contexto["host"], _ = endereco([opcao])


@then(parsers.parse('ela aceita conexões apenas de "{host}"'))
def aceita_de(contexto, host):
    assert contexto["host"] == host
