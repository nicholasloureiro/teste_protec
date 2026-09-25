from pypdf import PdfReader
from pytest_bdd import parsers, scenarios, then, when

from planilha_pdf import FormatoNaoSuportado, gerar_pdf

scenarios("features/gerar_pdf.feature")


@when("eu gerar o PDF")
def gerar(contexto):
    contexto["saida"] = gerar_pdf(contexto["entrada"])


@when("eu tentar gerar o PDF")
def tentar_gerar(contexto):
    try:
        gerar_pdf(contexto["entrada"])
    except FormatoNaoSuportado as e:
        contexto["erro"] = str(e)


@then("o arquivo PDF é criado")
def pdf_criado(contexto):
    saida = contexto["saida"]
    assert saida.suffix == ".pdf"
    assert saida.read_bytes().startswith(b"%PDF")


@then(parsers.parse('o PDF contém o texto "{texto}"'))
def pdf_contem(contexto, texto):
    reader = PdfReader(contexto["saida"])
    conteudo = "\n".join(p.extract_text() for p in reader.pages)
    assert texto in conteudo


@then(parsers.parse('recebo o erro "{mensagem}"'))
def recebo_erro(contexto, mensagem):
    assert mensagem in contexto.get("erro", "")
