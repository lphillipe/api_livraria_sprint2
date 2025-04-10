# API Livraria Online (Backend)

API REST desenvolvida em Flask (Python) para gerenciar o catálogo e estoque de uma livraria online. Permite adicionar, visualizar, editar e remover livros, além de buscar detalhes automaticamente em uma API externa ao adicionar novos títulos.

## Tecnologias Utilizadas

* Python 3.x
* Flask (com Flask-OpenAPI3 para documentação Swagger/ReDoc)
* Flask-CORS
* SQLAlchemy (com SQLite como banco de dados padrão)
* Requests (para chamadas à API externa)
* Docker

## Pré-requisitos (Desenvolvimento Local)

* Python 3 (versão 3.9 ou superior recomendada)
* `pip` (gerenciador de pacotes Python)
* (Opcional) Git para clonar o repositório
* (Opcional) Docker e Docker Compose para execução em container

## Instalação (Desenvolvimento Local)

1.  **Clone o repositório** (se aplicável):
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_BACKEND>
    cd <NOME_DA_PASTA_BACKEND>  
    ```
2.  **Crie um ambiente virtual:**
    * No Windows:
        ```cmd
        python -m venv env
        .\env\Scripts\activate
        ```
    * No Linux/macOS:
        ```bash
        python3 -m venv env
        source env/bin/activate
        ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Execução (Desenvolvimento Local)

1.  Certifique-se de que o ambiente virtual esteja ativado.
2.  Execute o servidor Flask:
    ```bash
    flask run --host 0.0.0.0 --port 5000
    ```
    * A API estará acessível em `http://127.0.0.1:5000`.
    * A documentação interativa da API (Swagger UI / ReDoc) geralmente estará disponível em `http://127.0.0.1:5000/openapi`.

## API Externa Utilizada

* **Nome:** Google Books API
* **URL Base:** `https://www.googleapis.com/books/v1/`
* **Propósito:** Utilizada na rota `POST /livro_adiciona` para buscar automaticamente autor(es), descrição e URL da capa com base no título do livro fornecido pelo usuário. A API busca pelo primeiro resultado mais relevante.
* **Cadastro/Chave:** Não foi necessário cadastro ou chave de API para as buscas públicas de volumes realizadas neste projeto.
* **Licença:** O uso está sujeito aos [Termos de Serviço das APIs do Google](https://developers.google.com/terms/).
* **Rota Externa Utilizada:** `GET volumes` com parâmetro `q` (ex: `https://www.googleapis.com/books/v1/volumes?q=...&maxResults=1&orderBy=relevance&langRestrict=pt`).

## Execução (Docker)

1.  **Construa a imagem Docker:** (Execute no diretório `api_livraria_sprint2`, onde está o Dockerfile)
    ```bash
    docker build -t nome-da-sua-imagem-backend .
    ```
    (Ex: `docker build -t api-livraria .`)

2.  **Execute o container Docker:**
    ```bash
    docker run -p 5000:5000 --name nome-do-seu-container-backend nome-da-sua-imagem-backend
    ```
    (Ex: `docker run -p 5000:5000 --name meu-api-livraria api-livraria`)
    * A API estará acessível em `http://127.0.0.1:5000` no seu navegador/ferramentas de API.
