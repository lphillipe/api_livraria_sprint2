import requests
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request, jsonify, send_from_directory
from urllib.parse import unquote
import os

from sqlalchemy.exc import IntegrityError

from model import Session, Livro
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Livraria API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc, RapiDoc, RapiPDF, Scalar, ou Elements")
livro_tag = Tag(name="Livro", description="Adição, visualização, remoção, e atualização de livros à base")



@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/livro_adiciona', tags=[livro_tag],
          responses={"200": LivroViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_livro(form: LivroBuscaSchema): 
    """Adiciona um novo Livro na base de dados.
    Se descrição e capa_url forem fornecidos no 'form', eles são usados.
    Caso contrário, tenta buscar na API do Google Books.

    Retorna uma representação do livro adicionado.
    """
    logger.debug(f"Recebida requisição para adicionar livro: Título='{form.nome}', Qtd={form.quantidade}, Valor={form.valor}")

    fetched_author = "Autor não encontrado"
    fetched_description = None
    fetched_cover_url = None

    # Faz a Busca na API Externa do Google.
    try:
        logger.info(f"Buscando dados externos para '{form.nome}'...")
        search_term = form.nome # Busca apenas pelo título
        encoded_search_term = requests.utils.quote(search_term)
        # Busca 1 resultado mais relevante em português
        google_books_url = f"https://www.googleapis.com/books/v1/volumes?q={encoded_search_term}&maxResults=1&orderBy=relevance&langRestrict=pt"

        response = requests.get(google_books_url, timeout=10)
        response.raise_for_status() # Verifica erros HTTP
        data = response.json()

        # Pega o PRIMEIRO resultado, se existir
        if data.get("totalItems", 0) > 0 and 'items' in data:
            volume_info = data['items'][0].get('volumeInfo', {})
            logger.info(f"Primeiro resultado encontrado para '{form.nome}'. Extraindo dados.")

            # Extrai autores (pega o primeiro da lista, se houver)
            authors_list = volume_info.get('authors')
            if authors_list and isinstance(authors_list, list):
                fetched_author = authors_list[0] # Pega só o primeiro autor
            elif authors_list: # Se for string única (raro)
                 fetched_author = authors_list
            # Mantém "Autor não encontrado" se a lista for vazia ou não existir

            fetched_description = volume_info.get('description')
            fetched_cover_url = volume_info.get('imageLinks', {}).get('thumbnail')
            logger.info(f"Dados extraídos: Autor='{fetched_author}', Desc? {'Sim' if fetched_description else 'Não'}, Capa? {'Sim' if fetched_cover_url else 'Não'}")
        else:
             logger.info(f"Nenhum resultado encontrado na API externa para '{form.nome}'. Usando dados padrão.")

    except requests.exceptions.Timeout:
         logger.warning(f"Timeout ao buscar dados na API externa para '{form.nome}'.")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erro de rede/HTTP ao buscar dados externos para '{form.nome}': {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar dados externos para '{form.nome}': {e}", exc_info=True)
    

    # Cria o objeto Livro com dados do form + dados buscados/padrão
    livro = Livro(
        nome=form.nome,
        autor=fetched_author, # Autor encontrado ou padrão
        quantidade=form.quantidade,
        valor=form.valor,
        descricao=fetched_description, # Descrição encontrada ou None
        capa_url=fetched_cover_url     # Capa encontrada ou None
    )
    logger.debug(f"Objeto Livro final para salvar: {livro.nome}, Autor: {livro.autor}, Qtd: {livro.quantidade}")

    session = Session()
    try:
        session.add(livro)
        session.commit()
        logger.debug(f"Livro '{livro.nome}' salvo no banco com ID: {livro.id}")
        # Retorna a representação completa do livro usando apresenta_livro
        return apresenta_livro(livro), 200

    except IntegrityError as e:
        session.rollback()
        error_msg = "Livro de mesmo nome já salvo na base :/"
        logger.warning(f"Erro de integridade ao adicionar livro '{livro.nome}': {e}")
        return {"mesage": error_msg}, 409
    except Exception as e:
        session.rollback()
        error_msg = "Não foi possível salvar novo item no servidor."
        logger.error(f"Erro inesperado ao salvar livro '{livro.nome}': {e}", exc_info=True)
        return {"mesage": error_msg}, 400
    finally:
        if session: session.close()
        logger.debug("Sessão do banco fechada.")

@app.get('/livros_list', tags=[livro_tag],
         responses={"200": ListagemLivrosSchema, "404": ErrorSchema})
def get_livros():
    """Lista todos os Livros cadastrados.

    Retorna uma representação da listagem de livros.
    """
    logger.debug(f"Coletando livros ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    livros = session.query(Livro).all()

    if not livros:
        # se não há livros cadastrados
        return {"livros": []}, 200
    else:
        logger.debug(f"%d livros econtrados" % len(livros))
        # retorna a representação de produto
        print(livros)
        return apresenta_livros(livros), 200


@app.get('/livro_busca', tags=[livro_tag],
         responses={"200": LivroViewSchema, "404": ErrorSchema})
def get_livro(query: LivroBuscaSchema):
    """Faz a busca por um livro a partir do nome do livro.

    Retorna uma representação dos livros associados.
    """
    livro_nome = query.nome
    logger.debug(f"Coletando dados sobre produto #{livro_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    livro = session.query(Livro).filter(Livro.nome == livro_nome).first()

    if not livro:
        # se o livro não foi encontrado
        error_msg = "Livro não encontrado na base :/"
        logger.warning(f"Erro ao buscar livro '{livro_nome}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Livro econtrado: '{livro.nome}'")
        # retorna a representação do livro
        return apresenta_livro(livro), 200


@app.delete('/livro_del', tags=[livro_tag],
            responses={"200": LivroDelSchema, "404": ErrorSchema})
def del_livro(query: LivroBuscaSchema):
    """Deleta um livro a partir do seu nome.

    Retorna uma mensagem de confirmação da remoção.
    """
    livro_nome = unquote(unquote(query.nome))
    print(livro_nome)
    logger.debug(f"Deletando dados sobre o livro #{livro_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Livro).filter(Livro.nome == livro_nome).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Livro deletado #{livro_nome}")
        return {"mesage": "Livro removido", "Livro": livro_nome}
    else:
        # se o produto não foi encontrado
        error_msg = "Livro não encontrado na base :/"
        logger.warning(f"Erro ao deletar um livro #'{livro_nome}', {error_msg}")
        return {"mesage": error_msg}, 404

@app.put('/livro_update', tags=[livro_tag],
         responses={"200": LivroViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def update_livro(query: LivroBuscaSchema):
    """Atualiza os dados de um Livro existente na base de dados, identificado pelo nome.

    O nome do livro a ser atualizado é passado via query parameter.
    O corpo da requisição (JSON) deve conter os novos dados: 'autor', 'quantidade' e 'valor'.

    Retorna uma representação atualizada do livro.
    """
    # Pega o nome do livro a ser atualizado pela query string
    livro_nome_original = unquote(unquote(query.nome))
    logger.debug(f"Recebida requisição para atualizar dados do livro: '{livro_nome_original}'")

    # Pega os dados enviados no corpo da requisição (espera-se JSON)
    data = request.get_json()

    # Validação básica dos dados recebidos
    if not data or not all(k in data for k in ('autor', 'quantidade', 'valor')):
         error_msg = "Dados incompletos para atualização. Forneça 'autor', 'quantidade' e 'valor' no corpo JSON."
         logger.warning(f"Erro ao atualizar livro '{livro_nome_original}': {error_msg}")
         return {"mesage": error_msg}, 400

    session = Session() # Abre a sessão ANTES do try/finally
    try:
        # Busca o livro existente pelo nome original
        livro = session.query(Livro).filter(Livro.nome == livro_nome_original).first()

        if not livro:
            # Se o livro não foi encontrado
            error_msg = "Livro não encontrado na base :/"
            logger.warning(f"Erro ao atualizar: Livro '{livro_nome_original}' não encontrado.")
            session.close() # Fecha a sessão antes de retornar
            return {"mesage": error_msg}, 404
        else:
            # Atualiza os campos do objeto livro encontrado
            logger.debug(f"Livro encontrado: '{livro.nome}'. Atualizando com dados: {data}")
            livro.autor = data['autor']
            livro.quantidade = int(data['quantidade']) # Converte para int
            livro.valor = float(data['valor']) # Converte para float

            # Efetiva a atualização no banco de dados
            session.commit()
            logger.debug(f"Livro '{livro_nome_original}' atualizado com sucesso para: {livro.autor}, {livro.quantidade}, {livro.valor}")
            # Retorna a representação atualizada do livro
            return apresenta_livro(livro), 200

    except ValueError:
         # Erro na conversão de quantidade ou valor para número
         error_msg = "Quantidade e/ou Valor inválidos. Devem ser numéricos."
         logger.warning(f"Erro ao atualizar livro '{livro_nome_original}': {error_msg} - Dados recebidos: {data}")
         session.rollback() # Desfaz quaisquer alterações na sessão
         return {"mesage": error_msg}, 400
    except Exception as e:
        # Caso ocorra qualquer outro erro inesperado
        error_msg = "Não foi possível atualizar o livro no servidor."
        logger.error(f"Erro inesperado ao atualizar livro '{livro_nome_original}': {e}", exc_info=True)
        session.rollback() # Desfaz quaisquer alterações na sessão
        return {"mesage": error_msg}, 400
    finally:
        # Garante que a sessão seja fechada em qualquer caso (sucesso ou erro)
        if session:
            session.close()
            logger.debug("Sessão do banco de dados fechada.")


