---
name: deploy-azure
description: Publica a tela planilha→PDF no Azure Container Apps (build do Dockerfile, criação/atualização do app, login Microsoft Entra, verificação da URL). Use quando pedirem deploy, publicar, subir no Azure ou atualizar a versão em produção.
disable-model-invocation: true
argument-hint: "[nome-do-app] [resource-group] [região]"
---

# Deploy no Azure Container Apps

Publica `planilha-pdf-tela` como container no Azure Container Apps. Deploy gera custo e expõe a tela na
internet: **confirme com o usuário antes de criar recursos e antes de liberar acesso**.

Parâmetros (`$ARGUMENTS`, na ordem; use o padrão se faltar):

| Parâmetro      | Padrão         |
|----------------|----------------|
| nome do app    | `planilha-pdf` |
| resource group | `rg-cobranca`  |
| região         | `brazilsouth`  |

## 1. Pré-voo local (não pule)

```bash
uv run pytest -q                       # tudo verde
git status --short                     # vazio; se não, commit + push antes (o deploy deve ser de código versionado)
docker build -t planilha-pdf:local .
docker run -d --rm --name planilha-teste -p 8081:8000 planilha-pdf:local
curl -s -o /dev/null -w '%{http_code}\n' localhost:8081                        # 200
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' \
  -F arquivo=@exemplos/cobrancas_teste.xlsx localhost:8081/converter          # 200 application/pdf
docker stop planilha-teste
```

Se o container falhar aqui, vai falhar no Azure também. Corrija antes de seguir.

## 2. Azure CLI e conta

```bash
az version || echo "instalar: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
az account show --query "{assinatura:name, id:id, usuario:user.name}" -o table
```

- Sem login: peça ao usuário para rodar `! az login` (é interativo; não rode por ele).
- Mostre a assinatura ativa e **pergunte se é a certa** antes de continuar. Trocar: `az account set -s <id>`.
- Primeira vez na assinatura: `az extension add -n containerapp --upgrade` e
  `az provider register -n Microsoft.App --wait` e `az provider register -n Microsoft.OperationalInsights --wait`.

## 3. Criar ou atualizar

Descubra se o app já existe:

```bash
az containerapp show -n <app> -g <rg> --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null
```

- **Não existe (primeiro deploy):** avise o usuário do custo (Container Apps no plano de consumo tem cota grátis
  mensal que cobre uso interno leve; o Container Registry Basic custa ~US$ 5/mês) e **peça confirmação**. Depois:

  ```bash
  az group create -n <rg> -l <região>
  az containerapp up -n <app> -g <rg> -l <região> \
    --source . --ingress external --target-port 8000
  ```

- **Já existe (nova versão):** rode o mesmo `az containerapp up -n <app> -g <rg> --source .`. Ele reconstrói a
  imagem e cria uma nova revisão.

`containerapp up --source .` usa o `Dockerfile` da raiz, cria o registry e o ambiente se faltarem, e imprime a URL.

## 3b. Banco Postgres (primeiro deploy)

Sem `DATABASE_URL` a tela funciona mas não guarda nada (ADR 0002). Verifique se já existe:
`az postgres flexible-server show -g <rg> -n <app>-pg --query state -o tsv`.

Se não existe, avise o custo (Flexible Server Burstable B1ms + 32 GB fica na casa de US$ 15–20/mês; confira na
calculadora do Azure) e **peça confirmação**. Então:

```bash
SENHA=$(openssl rand -base64 24 | tr -d '/+=')
az postgres flexible-server create -g <rg> -n <app>-pg -l <região> \
  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 \
  --admin-user cobranca --admin-password "$SENHA" --database-name cobranca \
  --public-access 0.0.0.0          # só serviços do Azure; nada da internet
az containerapp secret set -n <app> -g <rg> \
  --secrets database-url="postgresql://cobranca:$SENHA@<app>-pg.postgres.database.azure.com:5432/cobranca?sslmode=require"
az containerapp update -n <app> -g <rg> --set-env-vars DATABASE_URL=secretref:database-url
```

- A senha fica **só** no secret do Container App. Não escreva no chat, README, commit ou arquivo.
- As tabelas são criadas sozinhas quando a tela inicia. Confira nos logs que não aparece
  "DATABASE_URL não definida".

## 4. Login obrigatório (primeiro deploy)

A tela não tem autenticação própria (ADR 0001). **Antes de passar a URL para alguém**, ative o login da
Microsoft no próprio Azure (Easy Auth, sem mudar código). Isso exige registrar um app no Entra ID, que é mais
simples pelo portal. Oriente o usuário:

1. Portal do Azure → Container App `<app>` → **Autenticação** → **Adicionar provedor de identidade**.
2. Provedor **Microsoft**, "Criar novo registro de aplicativo", tipos de conta: **somente este locatário**.
3. Solicitações não autenticadas: **HTTP 302 — redirecionar para o login**.

Até o usuário confirmar que fez isso, trate o app como exposto e diga isso claramente.

## 5. Verificar

```bash
URL=https://$(az containerapp show -n <app> -g <rg> --query properties.configuration.ingress.fqdn -o tsv)
curl -s -o /dev/null -w '%{http_code}\n' $URL/      # com login ativo: 302 (ou 401). 200 = SEM login!
az containerapp logs show -n <app> -g <rg> --tail 20
```

- `200` sem estar logado significa que o login **não** está ativo: avise o usuário.
- Logs com "DATABASE_URL não definida" = o banco não está ligado e nada está sendo guardado.
- Peça ao usuário para abrir a URL no navegador, entrar com a conta da empresa e converter
  `exemplos/cobrancas_teste.xlsx`. Não dá para testar o fluxo logado via curl.

## 6. Registrar

- Coloque a URL de produção no README (seção "Uso pela tela"), commit e push.
- Informe ao usuário: URL, revisão ativa
  (`az containerapp revision list -n <app> -g <rg> --query "[?properties.active].name" -o tsv`),
  e se o login está ativo.

## Problemas conhecidos

- **Imagem roda local mas não sobe no Azure:** confira `--target-port 8000` e que o CMD usa `--rede`
  (sem ele o uvicorn escuta só em 127.0.0.1 e o ingress não alcança).
- **Mudou dependência e o build quebrou:** o Dockerfile usa `uv sync --frozen`; rode `uv lock` e commite o `uv.lock`.
- **Erro 503 "não foi possível guardar no banco":** veja `az containerapp logs show`; em geral é senha/URL errada
  no secret ou `sslmode=require` faltando.
- **Desfazer/limpar tudo:** `az group delete -n <rg>` apaga app, registry, ambiente **e o banco com os dados**. É irreversível:
  só com pedido explícito do usuário.
- **Planilhas grandes:** não há limite de upload no código; o ingress do Azure aceita o request inteiro.
  Se virar problema, limitar em `web.py`.
