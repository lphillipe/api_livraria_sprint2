from sqlalchemy import Column, String, Integer, DateTime, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base


class Livro(Base):
    __tablename__ = 'Livros'

    id = Column("pk_Livros", Integer, primary_key=True)
    nome = Column(String(140), unique=True)
    autor = Column(String(140))
    quantidade = Column(Integer)
    valor = Column(Float)
    # Novos campos (opcionais)
    descricao = Column(Text, nullable=True) # Usar Text para descrições longas
    capa_url = Column(String(255), nullable=True) # URL da capa

    data_insercao = Column(DateTime, default=datetime.now()) # Adicionado no original, manter

    # Atualiza o __init__ para aceitar os novos campos como opcionais
    def __init__(self, nome:str, autor: str, quantidade:int, valor:float,
                 descricao:Union[str, None]=None, capa_url:Union[str, None]=None):
        """
        Cria um Livro

        Arguments:
            nome: nome do livro.
            autor: autor do livro.
            quantidade: quantidade de livros.
            valor: o valor do livro.
            descricao: descrição do livro (opcional).
            capa_url: URL da imagem de capa (opcional).
        """
        self.nome = nome
        self.autor = autor
        self.quantidade = quantidade
        self.valor = valor
        self.descricao = descricao # Adicionado
        self.capa_url = capa_url   # Adicionado

