"""
Resumão prático para APIs REST
Você mais vai usar:

200 – sucesso genérico (GET, PUT, PATCH, POST simples)
201 – criado com sucesso (POST de criação)
204 – deu certo, sem corpo (DELETE, às vezes PUT/PATCH)
400 – requisição inválida (erros de formato/parâmetros)
401 – precisa de login/token
403 – usuário logado, mas sem permissão
404 – não encontrado
409 – conflito (ex: duplicado)
422 – dados inválidos (validação)
500 – erro inesperado do servidor
"""
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI(
    title="API de Livros",
    description="Uma API simples para gerenciar uma coleção de livros",
    version="1.0.0",
    contact={
        "name": "Antonio Bernardo Dos Santos Junior",
        "email": "bernardojunior.ccb@gmail.com",
    }
)

# segurança
MEU_USUARIO = "admin"
MEU_SENHA = "admin"

security = HTTPBasic()

livros: dict[int, dict[str, str | int]] = {
    1: {"titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien", "ano": 1954},
    2: {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling", "ano": 1997},
    3: {"titulo": "O Código Da Vinci", "autor": "Dan Brown", "ano": 2003},
    4: {"titulo": "A Guerra dos Tronos", "autor": "George R.R. Martin", "ano": 1996},
    5: {"titulo": "O Hobbit", "autor": "J.R.R. Tolkien", "ano": 1937},
    6: {"titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry", "ano": 1943},
    7: {"titulo": "O Alquimista", "autor": "Paulo Coelho", "ano": 1988},
    8: {"titulo": "O Morro dos Ventos Uivantes", "autor": "Emily Brontë", "ano": 1847},
    9: {"titulo": "O Retrato de Dorian Gray", "autor": "Oscar Wilde", "ano": 1890},
    10: {"titulo": "O Grande Gatsby", "autor": "F. Scott Fitzgerald", "ano": 1925},
    11: {"titulo": "O Senhor dos Anéis: A Sociedade do Anel", "autor": "J.R.R. Tolkien", "ano": 1954},
    12: {"titulo": "O Senhor dos Anéis: As Duas Torres", "autor": "J.R.R. Tolkien", "ano": 1954},
    13: {"titulo": "O Senhor dos Anéis: O Retorno do Rei", "autor": "J.R.R. Tolkien", "ano": 1955},
    14: {"titulo": "Harry Potter e a Câmara Secreta", "autor": "J.K. Rowling", "ano": 1998},
    15: {"titulo": "Harry Potter e o Prisioneiro de Azkaban", "autor": "J.K. Rowling", "ano": 1999},
    17: {"titulo": "Harry Potter e a Ordem da Fênix", "autor": "J.K. Rowling", "ano": 2003},
    18: {"titulo": "Harry Potter e o Enigma do Príncipe", "autor": "J.K. Rowling", "ano": 2005},
    19: {"titulo": "Harry Potter e as Relíquias da Morte", "autor": "J.K. Rowling", "ano": 2007},
    20: {"titulo": "O Código Da Vinci: O Símbolo Perdido", "autor": "Dan Brown", "ano": 2003},
}


class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int


def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    is_valid = secrets.compare_digest(credentials.username, MEU_USUARIO) and secrets.compare_digest(credentials.password, MEU_SENHA)
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"}
        )
    return True


@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)) -> dict:
    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros de paginação inválidos")

    start = (page - 1) * limit  # 0
    end = start + limit  # 4
    # livros_paginados = list(livros.items())[start:end]
    # livros_paginados = [
    #     {"id": id_livro, "titulo": dados["titulo"], "autor": dados["autor"], "ano": dados["ano"]}
    #     for id_livro, dados in list(livros.items())[start:end]
    # ]  # Mesma coisa que a linha abaixo, mas mais verbosa e menos flexível.
    livros_ordenados = sorted(livros.items(), key=lambda x: x[1]["titulo"])  # Ordena os livros por título antes de paginar
    livros_paginados = [{**{"id": id_livro}, **dados} for id_livro, dados in livros_ordenados[start:end]]
    return {
        "page": page,
        "limit": limit,
        "total": len(livros_paginados),
        "livros": livros_paginados
    }


@app.post("/adicionar-livro")
def post_livro(livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)) -> dict:
    if not livro:
        raise HTTPException(status_code=400, detail="Título e autor são obrigatórios")
    if any(liv["titulo"] == livro.titulo for liv in livros.values()):
        raise HTTPException(status_code=400, detail="Livro já existe")

    id_livro = max(livros.keys()) + 1 if livros else 1
    livros[id_livro] = livro.model_dump()
    return {"id": id_livro, "livro": livro}


@app.put("/atualizar-livro/{id_livro}")
def put_livro(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)) -> dict:
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    if not livro:
        raise HTTPException(status_code=400, detail="Título e autor são obrigatórios")

    livros[id_livro] = livro.model_dump()
    return {"id": id_livro, "livro": livro}


@app.delete("/deletar-livro/{id_livro}")
def delete_livro(id_livro: int, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)) -> dict:
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    del livros[id_livro]
    return {"message": "Livro deletado com sucesso"}

# 1: {"titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien", "ano": 1954},
# 2: {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling", "ano": 1997},
# 3: {"titulo": "O Código Da Vinci", "autor": "Dan Brown", "ano": 2003},
# 4: {"titulo": "A Guerra dos Tronos", "autor": "George R.R. Martin", "ano": 1996},
# 5: {"titulo": "O Hobbit", "autor": "J.R.R. Tolkien", "ano": 1937},
# 6: {"titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry", "ano": 1943},
# 7: {"titulo": "O Alquimista", "autor": "Paulo Coelho", "ano": 1988},
# 8: {"titulo": "O Morro dos Ventos Uivantes", "autor": "Emily Brontë", "ano": 1847},
# 9: {"titulo": "O Retrato de Dorian Gray", "autor": "Oscar Wilde", "ano": 1890},
# 10: {"titulo": "O Grande Gatsby", "autor": "F. Scott Fitzgerald", "ano": 1925},
# 11: {"titulo": "O Senhor dos Anéis: A Sociedade do Anel", "autor": "J.R.R. Tolkien", "ano": 1954},
# 12: {"titulo": "O Senhor dos Anéis: As Duas Torres", "autor": "J.R.R. Tolkien", "ano": 1954},
# 13: {"titulo": "O Senhor dos Anéis: O Retorno do Rei", "autor": "J.R.R. Tolkien", "ano": 1955},
# 14: {"titulo": "Harry Potter e a Câmara Secreta", "autor": "J.K. Rowling", "ano": 1998},
# 15: {"titulo": "Harry Potter e o Prisioneiro de Azkaban", "autor": "J.K. Rowling", "ano": 1999},
# 17: {"titulo": "Harry Potter e a Ordem da Fênix", " autor": "J.K. Rowling", "ano": 2003},
# 18: {"titulo": "Harry Potter e o Enigma do Príncipe", "autor": "J.K. Rowling", "ano": 2005},
# 19: {"titulo": "Harry Potter e as Relíquias da Morte", "autor": "J.K. Rowling", "ano": 2007},
# 20: {"titulo": "O Código Da Vinci: O Símbolo Perdido", "autor": "Dan Brown", "ano": 2003},