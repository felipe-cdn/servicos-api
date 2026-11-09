"""Regras dos serviços: o que pode ser cadastrado e como os dados são guardados.

Os serviços ficam guardados em memória (dentro de um dicionário do Python).
Isso deixa o projeto simples: o foco aqui é o pipeline, não o banco de dados.
"""

STATUS_VALIDOS = ["pendente", "em_andamento", "concluido"]


class ServicoInvalido(Exception):
    """Erro usado quando os dados enviados não servem (a API responde 400)."""


def validar_servico(dados):
    """Confere se o serviço tem nome, cliente e preço corretos."""
    if not isinstance(dados, dict):
        raise ServicoInvalido("Envie um JSON com nome, cliente e preco.")

    nome = dados.get("nome")
    cliente = dados.get("cliente")
    preco = dados.get("preco")

    # Nome e cliente: texto que não pode ser vazio
    if not isinstance(nome, str) or nome.strip() == "":
        raise ServicoInvalido("O campo 'nome' é obrigatório.")
    if not isinstance(cliente, str) or cliente.strip() == "":
        raise ServicoInvalido("O campo 'cliente' é obrigatório.")

    # Preço: número maior que zero (True e False não valem como número)
    preco_e_numero = isinstance(preco, (int, float)) and not isinstance(preco, bool)
    if not preco_e_numero or preco <= 0:
        raise ServicoInvalido("O campo 'preco' deve ser um número maior que zero.")

    return {"nome": nome.strip(), "cliente": cliente.strip(), "preco": float(preco)}


def validar_status(status):
    """Confere se o status é um dos aceitos."""
    if status not in STATUS_VALIDOS:
        raise ServicoInvalido("Status inválido. Use: " + ", ".join(STATUS_VALIDOS))


class ListaDeServicos:
    """Guarda os serviços e permite criar, buscar, mudar o status e remover."""

    def __init__(self):
        self.servicos = {}  # chave = id, valor = dados do serviço
        self.proximo_id = 1

    def criar(self, dados):
        dados = validar_servico(dados)
        servico = {"id": self.proximo_id, **dados, "status": "pendente"}
        self.servicos[servico["id"]] = servico
        self.proximo_id += 1
        return servico

    def listar(self, status=None):
        todos = list(self.servicos.values())
        if status is None:
            return todos
        validar_status(status)
        return [servico for servico in todos if servico["status"] == status]

    def buscar(self, servico_id):
        return self.servicos.get(servico_id)  # devolve None se não existir

    def atualizar_status(self, servico_id, status):
        validar_status(status)
        servico = self.buscar(servico_id)
        if servico is not None:
            servico["status"] = status
        return servico

    def remover(self, servico_id):
        """Remove o serviço. Devolve True se removeu e False se não existia."""
        return self.servicos.pop(servico_id, None) is not None
