"""Tela web: envia a planilha e baixa o PDF."""

import tempfile
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response

from planilha_pdf import FormatoNaoSuportado, gerar_pdf

app = FastAPI(title="Planilha → PDF")

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
    return Response(conteudo, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{saida.name}"'})


def main() -> None:
    import uvicorn

    print("Abra http://localhost:8000 no navegador")
    uvicorn.run(app, host="127.0.0.1", port=8000)
