import psycopg
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import parsers, scenarios, then, when
from testcontainers.community.postgres import PostgresContainer

from planilha_pdf import banco
from planilha_pdf.web import app

scenarios("features/banco.feature")


@pytest.fixture(scope="session")
def url_banco():
    with PostgresContainer("postgres:16-alpine", driver=None) as pg:
        url = pg.get_connection_url()
        banco.criar_tabelas(url)
        yield url


@pytest.fixture
def banco_ligado(url_banco, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", url_banco)
    with psycopg.connect(url_banco) as conn:
        conn.execute("TRUNCATE conversoes RESTART IDENTITY CASCADE")
    return url_banco


@when("eu enviar a planilha pela tela com o banco ligado")
def enviar_com_banco(contexto, banco_ligado):
    entrada = contexto["entrada"]
    with TestClient(app) as cliente:
        contexto["resposta"] = cliente.post(
            "/converter", files={"arquivo": (entrada.name, entrada.read_bytes())}, data={"titulo": ""}
        )


@when("eu consultar o histórico")
def consultar_historico(contexto, banco_ligado):
    with TestClient(app) as cliente:
        contexto["historico"] = cliente.get("/historico").json()


@then(parsers.parse('a conversão de "{arquivo}" fica registrada com {linhas:d} linhas'))
def conversao_registrada(banco_ligado, arquivo, linhas):
    with psycopg.connect(banco_ligado) as conn:
        registro = conn.execute("SELECT arquivo, linhas FROM conversoes").fetchall()
    assert registro == [(arquivo, linhas)]


@then(parsers.parse('a linha do cliente "{cliente}" fica guardada com o vencimento "{vencimento}" e o valor {valor:g}'))
def linha_guardada(banco_ligado, cliente, vencimento, valor):
    with psycopg.connect(banco_ligado) as conn:
        dados = conn.execute(
            "SELECT dados FROM linhas_planilha WHERE dados->>'Cliente' = %s", (cliente,)
        ).fetchone()[0]
    assert dados["Vencimento"].startswith(vencimento)
    assert dados["Valor"] == valor


@then(parsers.parse('vejo "{arquivo}" no histórico'))
def vejo_no_historico(contexto, arquivo):
    assert contexto["historico"]["ativo"] is True
    assert arquivo in [c["arquivo"] for c in contexto["historico"]["conversoes"]]


@then("nenhuma conversão fica registrada")
def nada_registrado(banco_ligado):
    with psycopg.connect(banco_ligado) as conn:
        assert conn.execute("SELECT count(*) FROM conversoes").fetchone()[0] == 0
