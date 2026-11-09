"""Testes das rotas da API (simulam quem chama a API)."""
import pytest

from app.main import create_app

DADOS = {"nome": "Pintura", "cliente": "João", "preco": 300}


@pytest.fixture
def client():
    """Cria uma API nova para cada teste e devolve um 'cliente' para chamá-la."""
    return create_app().test_client()


def test_health_responde_ok(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.get_json() == {"status": "ok"}


def test_criar_servico_retorna_201(client):
    resposta = client.post("/servicos", json=DADOS)
    assert resposta.status_code == 201
    assert resposta.get_json()["nome"] == "Pintura"


def test_criar_servico_invalido_retorna_400(client):
    resposta = client.post("/servicos", json={"nome": "Sem preço"})
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_listar_e_filtrar_por_status(client):
    client.post("/servicos", json=DADOS)
    limpeza = client.post("/servicos", json={**DADOS, "nome": "Limpeza"}).get_json()
    client.patch(f"/servicos/{limpeza['id']}/status", json={"status": "concluido"})

    todos = client.get("/servicos").get_json()
    concluidos = client.get("/servicos?status=concluido").get_json()

    assert len(todos) == 2
    assert [servico["nome"] for servico in concluidos] == ["Limpeza"]


def test_buscar_servico_inexistente_retorna_404(client):
    assert client.get("/servicos/999").status_code == 404


def test_remover_servico(client):
    criado = client.post("/servicos", json=DADOS).get_json()
    assert client.delete(f"/servicos/{criado['id']}").status_code == 204
    assert client.get(f"/servicos/{criado['id']}").status_code == 404


def test_raiz_mostra_nome_e_versao(client):
    dados = client.get("/").get_json()
    assert "app" in dados
    assert "versao" in dados
    