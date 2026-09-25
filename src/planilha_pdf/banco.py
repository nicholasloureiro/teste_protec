"""Guarda as conversões e as linhas das planilhas no Postgres."""

import os
from datetime import date, datetime, time

import psycopg
from psycopg.types.json import Jsonb

ESQUEMA = """
CREATE TABLE IF NOT EXISTS conversoes (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    criado_em     timestamptz NOT NULL DEFAULT now(),
    arquivo       text NOT NULL,
    titulo        text,
    tamanho_bytes integer NOT NULL,
    abas          integer NOT NULL,
    linhas        integer NOT NULL
);
CREATE INDEX IF NOT EXISTS conversoes_criado_em_idx ON conversoes (criado_em DESC);

CREATE TABLE IF NOT EXISTS linhas_planilha (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversao_id bigint NOT NULL REFERENCES conversoes (id) ON DELETE CASCADE,
    aba          text NOT NULL,
    numero       integer NOT NULL,
    dados        jsonb NOT NULL
);
CREATE INDEX IF NOT EXISTS linhas_planilha_conversao_idx ON linhas_planilha (conversao_id);
"""


def url_configurada() -> str | None:
    """URL do Postgres (variável DATABASE_URL). Sem ela, nada é guardado."""
    return os.environ.get("DATABASE_URL") or None


def criar_tabelas(url: str) -> None:
    with psycopg.connect(url) as conn:
        conn.execute(ESQUEMA)


def _valor_json(valor):
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    return valor


def _registros(linhas: list[list]) -> list[dict]:
    """Primeira linha é o cabeçalho; cada linha seguinte vira {coluna: valor}."""
    if not linhas:
        return []
    cabecalho = []
    for i, nome in enumerate(linhas[0], start=1):
        nome = str(nome).strip() if nome not in (None, "") else f"coluna_{i}"
        while nome in cabecalho:
            nome += f"_{i}"
        cabecalho.append(nome)
    return [
        {col: _valor_json(v) for col, v in zip(cabecalho, linha) if v not in (None, "")}
        for linha in linhas[1:]
    ]


def salvar_conversao(url: str, arquivo: str, titulo: str | None, tamanho_bytes: int,
                     abas: dict[str, list[list]]) -> int:
    """Grava a conversão e as linhas de todas as abas numa transação. Retorna o id."""
    por_aba = {nome: _registros(linhas) for nome, linhas in abas.items()}
    total = sum(len(r) for r in por_aba.values())
    with psycopg.connect(url) as conn:
        conversao_id = conn.execute(
            "INSERT INTO conversoes (arquivo, titulo, tamanho_bytes, abas, linhas)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (arquivo, titulo, tamanho_bytes, len(por_aba), total),
        ).fetchone()[0]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO linhas_planilha (conversao_id, aba, numero, dados) VALUES (%s, %s, %s, %s)",
                [(conversao_id, aba, n, Jsonb(r))
                 for aba, registros in por_aba.items() for n, r in enumerate(registros, start=1)],
            )
    return conversao_id


def historico(url: str, limite: int = 20) -> list[dict]:
    with psycopg.connect(url) as conn:
        cur = conn.execute(
            "SELECT id, criado_em, arquivo, titulo, abas, linhas FROM conversoes"
            " ORDER BY criado_em DESC LIMIT %s",
            (limite,),
        )
        colunas = [c.name for c in cur.description]
        return [dict(zip(colunas, linha)) for linha in cur.fetchall()]
