from pydantic import BaseModel, Field 
from typing import Optional, List
from model.livro import Livro

class LivroBuscaSchema(BaseModel):
    """ Define como um novo livro a ser inserido deve ser representado
    """
    nome: str = "Dom Casmurro"
    #autor: str = "Machado de Assis"
    quantidade: Optional[int] = 1
    valor: float = 37.00

class LivroUpdateBodySchema(BaseModel):
    """ Define os dados esperados no corpo JSON para atualizar um livro. """
    autor: str = "Machado de Assis " 
    quantidade: int = 10                     
    valor: float = 40.00                     

class ListagemLivrosSchema(BaseModel):
    """ Define como uma listagem de livros será retornada.
    """
    livros:List['LivroViewSchema']

class LivroViewSchema(BaseModel):
    """ Define como um livro será retornado.
    """
    id: int
    nome: str
    autor: Optional[int]
    quantidade: Optional[int]
    valor: float
    descricao: Optional[str] = None
    capa_url: Optional[str] = None

class LivroDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nome: str


def apresenta_livro(livro: Livro):
    """ Retorna uma representação do livro seguindo o schema definido em
        LivroViewSchema.
    """
    return {
        "id": livro.id,
        "nome": livro.nome,
        "autor": livro.autor,
        "quantidade": livro.quantidade,
        "valor": livro.valor,
        "descricao": livro.descricao,
        "capa_url": livro.capa_url
    }


def apresenta_livros(livros: List[Livro]) -> dict:
    """ Função para formatar UMA LISTA de livros para a resposta """
    result = []
    for livro in livros:
        result.append(apresenta_livro(livro))
    return {"livros": result}