# API de Prestação de Serviços

Projeto Final de **Integração DevOps** (Turma A, Taguatinga II).

**Integrantes:** Felipe Camargo Do Nascimento e Pedro Henrique Soares Puccinelli

## Descrição

Uma API REST bem simples para cadastrar e acompanhar **serviços prestados** (por exemplo, "Pintura" para o cliente "João"). O objetivo do projeto não é a aplicação, e sim demonstrar o ciclo DevOps: Git, testes automatizados, integração contínua (GitHub Actions), imagem Docker, entrega e boas práticas de segurança e monitoramento.

**O que é uma API?** É um "garçom" entre quem pede e quem guarda os dados. Outro programa (ou uma pessoa) faz um pedido por um endereço, como `GET /servicos` ("me mostre os serviços"), e a API devolve a resposta em formato JSON. **REST** é o jeito mais comum de organizar esses pedidos: cada endereço é uma coisa (`/servicos`) e o tipo de pedido diz a ação (GET busca, POST cria, PATCH altera, DELETE remove).

Principais funcionalidades:

- Cadastrar um serviço (nome, cliente e preço).
- Listar serviços e filtrar por status.
- Consultar, atualizar o status (`pendente`, `em_andamento`, `concluido`) e remover um serviço.
- Endpoint de saúde (`/health`) e logs de cada requisição.

## Tecnologias e ferramentas

| Para quê | Ferramenta |
|---|---|
| Linguagem e API | Python 3.12 e Flask |
| Servidor de produção | Gunicorn |
| Testes | pytest |
| Estilo de código | flake8 |
| Versionamento | Git e GitHub |
| Integração contínua | GitHub Actions |
| Artefato | Imagem Docker publicada no GitHub Container Registry (GHCR) |
| Execução do ambiente | Docker e Docker Compose |
| Segurança | pip-audit, GitHub Secrets (`GITHUB_TOKEN`), contêiner sem root |

## Como executar e testar a API

### Sem Docker (para desenvolver)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m flask --app app.main run --port 8000
```

### Endpoints

| Método | Rota | O que faz |
|---|---|---|
| GET | `/health` | Verifica se a API está de pé |
| GET | `/` | Nome, ambiente e versão |
| GET | `/servicos` | Lista (aceita `?status=concluido`) |
| POST | `/servicos` | Cria um serviço |
| GET | `/servicos/<id>` | Busca um serviço |
| PATCH | `/servicos/<id>/status` | Muda o status |
| DELETE | `/servicos/<id>` | Remove |

Exemplos (com a API em `http://localhost:8000`):

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/servicos -H "Content-Type: application/json" \
     -d '{"nome":"Pintura","cliente":"João","preco":300}'
curl http://localhost:8000/servicos
curl -X PATCH http://localhost:8000/servicos/1/status -H "Content-Type: application/json" \
     -d '{"status":"concluido"}'
```

No Windows (PowerShell), use `curl.exe` no lugar de `curl`, ou abra `http://localhost:8000/servicos` no navegador.

### Rodar os testes

```bash
pytest
```

São **11 testes automatizados**: regras de negócio (`tests/test_servicos.py`) e endpoints (`tests/test_api.py`).

## Estratégia de versionamento (GitHub Flow)

- A branch `main` é sempre estável: só recebe código por **Pull Request**.
- Cada funcionalidade ou correção nasce em uma branch curta: `feature/nome-da-mudanca` ou `fix/nome-do-erro`.
- Os commits têm mensagens descritivas (ex.: `Adiciona filtro de serviços por status`).
- O Pull Request só é aprovado (merge) depois que o **CI passa** e o **outro integrante revisa**.
- As versões são marcadas com tags (`v1.0.0`), e cada tag gera uma imagem Docker com o mesmo número.

## Pipeline de CI/CD (GitHub Actions)

Arquivo: `.github/workflows/ci.yml`. Roda em **push na main**, em **Pull Request** e em **tags `v*`**.

| Job | O que faz |
|---|---|
| **Testes** | Baixa o código (checkout), prepara o Python, instala as dependências, valida (flake8 e compilação), roda os testes e guarda o relatório (`resultados-testes.xml`) como artefato. |
| **Segurança** | Roda o `pip-audit` para achar vulnerabilidades conhecidas nas dependências. |
| **Imagem Docker** | Só roda se Testes e Segurança passarem. Constrói a imagem e, na `main` ou em tags, publica no GHCR. |

Se um teste falha, o job **Testes** fica vermelho e o pipeline para: a imagem não é publicada.

## Testes automatizados

- 11 casos de teste com **pytest**, executados no job **Testes** do pipeline.
- Cobrem: criação, validações (nome vazio, preço inválido), mudança e filtro de status, 404, remoção e o endpoint `/health`.
- Um teste que falha **derruba o pipeline** (o `pytest` devolve erro e o job fica vermelho).

## Artefato: construção e localização

- O artefato é uma **imagem Docker**, criada pelo `Dockerfile` no job **Imagem Docker**.
- Fica em `ghcr.io/<usuario>/servicos-api` (aba **Packages** do repositório).
- Rastreabilidade: cada imagem recebe a tag `sha-<commit>` (qual commit gerou), `latest` (última da main) e `1.0.0` (quando há tag `v1.0.0`).

## Estratégia de implantação e atualização

Separamos as etapas assim:

1. **Construção:** o Docker gera a imagem.
2. **Teste:** o pytest e o pip-audit validam o código.
3. **Entrega:** o pipeline publica a imagem no GHCR (fica pronta para uso).
4. **Implantação:** alguém roda a imagem em um ambiente, com Docker Compose.

### Implantar (ambiente local com Docker Compose)

```bash
cp .env.example .env        # ajuste GITHUB_USER e IMAGE_TAG
docker compose pull
docker compose up -d
curl http://localhost:8000/health
```

### Atualizar a versão

Mude `IMAGE_TAG` no arquivo `.env` para a nova versão (ex.: `1.1.0`) e rode:

```bash
docker compose pull && docker compose up -d
```

### Voltar para a versão anterior (rollback)

Como toda versão fica guardada no GHCR, basta apontar para a tag antiga (ex.: `IMAGE_TAG=1.0.0` ou `sha-abc1234`) e repetir os mesmos dois comandos. Não é preciso reconstruir nada.

## Infraestrutura e configuração

**Requisitos:** Docker 24 ou superior (com Docker Compose), cerca de 256 MB de memória e a porta 8000 livre.

**Configuração fora do código** (variáveis de ambiente, arquivo `.env`):

| Variável | Para que serve | Padrão |
|---|---|---|
| `GITHUB_USER` | Dono da imagem no GHCR | (obrigatória) |
| `IMAGE_TAG` | Versão da imagem | `latest` |
| `APP_NAME` | Nome mostrado na API | `API de Serviços` |
| `APP_ENV` | Ambiente (`producao`, `teste`...) | `producao` |
| `LOG_LEVEL` | Nível dos logs | `INFO` |

O `docker-compose.yml` sobe sempre o mesmo ambiente, de forma reproduzível.

## Segurança (DevSecOps)

- **Sem segredos no repositório:** o `.env` está no `.gitignore`; só o `.env.example` (sem valores secretos) é versionado.
- **GitHub Secrets:** o pipeline entra no GHCR com o `GITHUB_TOKEN`, gerado automaticamente a cada execução. Nenhuma senha fica no código.
- **Verificação automatizada:** o `pip-audit` procura vulnerabilidades conhecidas nas dependências a cada execução. Se achar uma, o job falha antes da imagem ser publicada.
- **Contêiner mais seguro:** a imagem usa `python:slim` (menor superfície de ataque) e roda com **usuário comum**, não root. As permissões do pipeline são mínimas (`contents: read`).

## Monitoramento e observabilidade

- **`GET /health`:** responde `{"status":"ok"}`. O contêiner também tem um `HEALTHCHECK`, e o `docker ps` mostra `healthy` ou `unhealthy`.
- **Logs:** cada requisição e cada erro geram uma linha de log (`docker compose logs -f api`).
- **Como identificar uma falha depois do deploy:** `docker ps` mostra `unhealthy` ou o contêiner parado; `curl /health` não responde; os logs mostram o erro.

## Evidências (GitHub Actions)

Os links abaixo mostram o histórico real do pipeline do projeto.

| Evidência | Link |
|---|---|
| Execução **com falha** (teste quebrado de propósito) | [Execução #8](https://github.com/felipe-cdn/servicos-api/actions/runs/42689241453) |
| Execução **com sucesso** (após a correção) | [Execução #9](https://github.com/felipe-cdn/servicos-api/actions/runs/42689923261) |
| Todas as execuções | [GitHub Actions](https://github.com/felipe-cdn/servicos-api/actions) |
| Pull Requests | [Pull Requests](https://github.com/felipe-cdn/servicos-api/pulls?q=is%3Apr) |
| Release v1.0.0 | [Release v1.0.0](https://github.com/felipe-cdn/servicos-api/releases/tag/v1.0.0) |
| Imagem publicada (GHCR) | [ghcr.io/felipe-cdn/servicos-api](https://github.com/felipe-cdn/servicos-api/pkgs/container/servicos-api) |

### O que aconteceu na falha

Em um Pull Request, um teste foi alterado de propósito (`is False` virou `is True`). O pipeline ficou vermelho no job **Testes**, o log mostrou `assert False is True` e o job **Imagem Docker** foi pulado, então nenhuma imagem quebrada foi publicada. O teste foi corrigido no mesmo PR e a execução seguinte (#9) passou nos três jobs.

Versão atual: 1.0.1
