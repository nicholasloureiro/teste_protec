"""Tela web: envia a planilha e baixa o PDF."""

import argparse
import socket
import logging
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response

from planilha_pdf import FormatoNaoSuportado, banco, gerar_pdf, ler_planilha

log = logging.getLogger("planilha_pdf")


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    url = banco.url_configurada()
    if url:
        banco.criar_tabelas(url)
    else:
        log.warning("DATABASE_URL não definida: as conversões não serão guardadas.")
    yield


app = FastAPI(title="Planilha → PDF", lifespan=ciclo_de_vida)

PAGINA = (Path(__file__).parent / "tela.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def tela():
    return PAGINA


@app.post("/converter")
async def converter(arquivo: UploadFile, titulo: str = Form("")):
    nome = Path(arquivo.filename or "planilha").name
    with tempfile.TemporaryDirectory() as pasta:
        entrada = Path(pasta) / nome
        entrada.write_bytes(await arquivo.read())
        try:
            saida = gerar_pdf(entrada, titulo=titulo.strip() or None)
        except FormatoNaoSuportado as e:
            return JSONResponse({"erro": str(e)}, status_code=400)
        except Exception:
            return JSONResponse({"erro": "Não foi possível ler a planilha. Verifique se o arquivo não está corrompido."},
                                status_code=400)
        conteudo = saida.read_bytes()
        url = banco.url_configurada()
        if url:
            try:
                banco.salvar_conversao(url, nome, titulo.strip() or None, entrada.stat().st_size,
                                       ler_planilha(entrada))
            except Exception:
                log.exception("Falha ao guardar a conversão de %s", nome)
                return JSONResponse({"erro": "O PDF foi gerado, mas não foi possível guardar no banco. "
                                             "Tente de novo ou avise o suporte."}, status_code=503)
    return Response(conteudo, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{saida.name}"'})


@app.get("/historico")
def ver_historico():
    url = banco.url_configurada()
    if not url:
        return {"ativo": False, "conversoes": []}
    return {"ativo": True, "conversoes": banco.historico(url)}


def endereco(argv: list[str] | None = None) -> tuple[str, int]:
    """Lê as opções da linha de comando e devolve (host, porta)."""
    parser = argparse.ArgumentParser(description="Tela web do conversor de planilha para PDF.")
    parser.add_argument("--rede", action="store_true",
                        help="aceita conexões de outros aparelhos da rede local (ex.: celular)")
    parser.add_argument("--porta", type=int, default=8000)
    args = parser.parse_args(argv)
    return ("0.0.0.0" if args.rede else "127.0.0.1"), args.porta


def ip_local() -> str:
    """IP deste computador na rede local (o da interface que sai para a internet)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def main() -> None:
    import uvicorn

    host, porta = endereco()
    print(f"Neste computador: http://localhost:{porta}")
    if host == "0.0.0.0":
        print(f"No celular (mesma rede Wi-Fi): http://{ip_local()}:{porta}")
    uvicorn.run(app, host=host, port=porta)
