"""Testes das regras dos serviços (sem passar pela API)."""
import pytest

from app.servicos import ListaDeServicos, ServicoInvalido

DADOS = {"nome": "Instalação elétrica", "cliente": "Maria", "preco": 150}


@pytest.fixture
def lista():
    """Cria uma lista nova e vazia para cada teste."""
    return ListaDeServicos()


def test_criar_servico_comeca_pendente(lista):
    servico = lista.criar(DADOS)
    assert servico["id"] == 1
    assert servico["status"] == "pendente"


def test_criar_sem_nome_e_invalido(lista):
    with pytest.raises(ServicoInvalido):
        lista.criar({**DADOS, "nome": "  "})


def test_preco_precisa_ser_maior_que_zero(lista):
    with pytest.raises(ServicoInvalido):
        lista.criar({**DADOS, "preco": 0})


def test_atualizar_status(lista):
    servico = lista.criar(DADOS)
    atualizado = lista.atualizar_status(servico["id"], "concluido")
    assert atualizado["status"] == "concluido"


def test_status_invalido_e_recusado(lista):
    servico = lista.criar(DADOS)
    with pytest.raises(ServicoInvalido):
        lista.atualizar_status(servico["id"], "voando")
