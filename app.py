# API de Lista de Tarefas
# Desenvolvido por Kamilla Medrado para a Sprint Desenvolvimento Full Stack Básico - PUC-RIO
# MVP entregue em 06/07/2025

from flask import Flask, request
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from urllib.parse import unquote

from model import Session, Base, engine, Tarefa
from util.respostas import resposta_sucesso, resposta_erro
from schemas.tarefa import TarefaSchema
from schemas.tarefa_busca import TarefaBuscaSchema
from schemas.tarefa_view import apresenta_tarefa, apresenta_tarefas
from logger.logger import logger

app = Flask(__name__)
CORS(app)

# Criar as tabelas no banco
Base.metadata.create_all(bind=engine)


@app.route("/")
def home():
    return resposta_sucesso("API de tarefas no ar!", 200)


@app.post("/tarefa")
def add_tarefa():
    """ Adiciona uma nova tarefa """
    logger.debug("Recebendo nova tarefa para cadastro...")
    dados = request.get_json()
    tarefa = Tarefa(
        titulo=dados.get("titulo"),
        descricao=dados.get("descricao"),
        concluida=False
    )
    try:
        session = Session()
        session.add(tarefa)
        session.commit()
        logger.debug(f"Tarefa adicionada: {tarefa.titulo}")
        return resposta_sucesso(apresenta_tarefa(tarefa), 200)
    except IntegrityError:
        return resposta_erro(409, "Já existe uma tarefa com esse título.")
    except Exception as e:
        return resposta_erro(400, f"Erro ao adicionar tarefa: {str(e)}")
    

@app.get("/tarefas")
def get_tarefas():
    """ Lista todas as tarefas """
    logger.debug("Listando todas as tarefas...")
    session = Session()
    tarefas = session.query(Tarefa).all()
    if not tarefas:
        return resposta_sucesso([], 200)
    return resposta_sucesso(apresenta_tarefas(tarefas), 200)


@app.get("/tarefa")
def get_tarefa():
    """ Busca uma tarefa pelo título """
    dados = request.args
    titulo = dados.get("titulo")
    if not titulo:
        return resposta_erro(400, "Título da tarefa não informado.")
    
    session = Session()
    tarefa = session.query(Tarefa).filter(Tarefa.titulo == titulo).first()
    if not tarefa:
        return resposta_erro(404, "Tarefa não encontrada.")
    return resposta_sucesso(apresenta_tarefa(tarefa), 200)


@app.delete("/tarefa")
def del_tarefa():
    """ Remove uma tarefa pelo título """
    dados = request.args
    titulo = unquote(unquote(dados.get("titulo", "")))

    session = Session()
    count = session.query(Tarefa).filter(Tarefa.titulo == titulo).delete()
    session.commit()

    if count:
        return resposta_sucesso(f"Tarefa '{titulo}' removida com sucesso!", 200)
    else:
        return resposta_erro(404, "Tarefa não encontrada.")
    

if __name__ == "__main__":
    print("Iniciando aplicação Flask...")
    app.run(debug=True)