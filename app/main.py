"""A API: cada função abaixo responde a um endereço (rota) da internet."""
import logging
import os

from flask import Flask, jsonify, request

from app.servicos import ListaDeServicos, ServicoInvalido

logger = logging.getLogger("servicos-api")


def create_app():
    """Monta a API. As configurações vêm de variáveis de ambiente (fora do código)."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    app = Flask(__name__)
    lista = ListaDeServicos()

    nome_do_app = os.getenv("APP_NAME", "API de Serviços")
    ambiente = os.getenv("APP_ENV", "desenvolvimento")
    versao = os.getenv("APP_VERSION", "dev")

    # ----- Logs e erros -----

    @app.after_request
    def registrar_log(resposta):
        # Escreve uma linha de log a cada requisição. Ex.: GET /health -> 200
        logger.info("%s %s -> %s", request.method, request.path, resposta.status_code)
        return resposta

    @app.errorhandler(ServicoInvalido)
    def dados_invalidos(erro):
        return jsonify({"erro": str(erro)}), 400

    @app.errorhandler(404)
    def rota_nao_encontrada(_erro):
        return jsonify({"erro": "Endereço não encontrado."}), 404

    # ----- Rotas -----

    @app.get("/")
    def inicio():
        return jsonify({"app": nome_do_app, "ambiente": ambiente, "versao": versao})

    @app.get("/health")
    def health():
        # Usado para saber se a API está funcionando
        return jsonify({"status": "ok"})

    @app.get("/servicos")
    def listar_servicos():
        # Aceita filtro opcional: /servicos?status=concluido
        return jsonify(lista.listar(request.args.get("status")))

    @app.post("/servicos")
    def criar_servico():
        servico = lista.criar(request.get_json(silent=True))
        logger.info("Serviço criado: id=%s", servico["id"])
        return jsonify(servico), 201

    @app.get("/servicos/<int:servico_id>")
    def buscar_servico(servico_id):
        servico = lista.buscar(servico_id)
        if servico is None:
            return jsonify({"erro": "Serviço não encontrado."}), 404
        return jsonify(servico)

    @app.patch("/servicos/<int:servico_id>/status")
    def mudar_status(servico_id):
        dados = request.get_json(silent=True) or {}
        servico = lista.atualizar_status(servico_id, dados.get("status"))
        if servico is None:
            return jsonify({"erro": "Serviço não encontrado."}), 404
        return jsonify(servico)

    @app.delete("/servicos/<int:servico_id>")
    def remover_servico(servico_id):
        if not lista.remover(servico_id):
            return jsonify({"erro": "Serviço não encontrado."}), 404
        return "", 204

    return app


app = create_app()
