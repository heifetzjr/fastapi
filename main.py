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

app = FastAPI()

livros: dict[int, dict[str, str]] = {}


@app.get("/livros")
def get_livros() -> dict:
    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    return {"livros": livros}


@app.post("/adicionar-livro")
def post_livro(titulo: str, autor: str) -> dict:
    if not titulo or not autor:
        raise HTTPException(status_code=400, detail="Título e autor são obrigatórios")
    if any(livro["titulo"] == titulo for livro in livros.values()):
        raise HTTPException(status_code=400, detail="Livro já existe")

    id_livro = max(livros.keys()) + 1 if livros else 1
    livros[id_livro] = {"titulo": titulo, "autor": autor}
    return {"id": id_livro, "titulo": titulo, "autor": autor}


@app.put("/atualizar-livro/{id_livro}")
def put_livro(id_livro: int, titulo: str, autor: str) -> dict:
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    if not titulo or not autor:
        raise HTTPException(status_code=400, detail="Título e autor são obrigatórios")

    livros[id_livro] = {"titulo": titulo, "autor": autor}
    return {"id": id_livro, "titulo": titulo, "autor": autor}


@app.delete("/deletar-livro/{id_livro}")
def delete_livro(id_livro: int) -> dict:
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    del livros[id_livro]
    return {"message": "Livro deletado com sucesso"}

# 1: {"titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien"},
# 2: {"titulo": "Harry Potter e a Pedra Filosofal", "autor": "J.K. Rowling"},
# 3: {"titulo": "O Código Da Vinci", "autor": "Dan Brown"},
# 4: {"titulo": "A Guerra dos Tronos", "autor": "George R.R. Martin"},
# 5: {"titulo": "O Hobbit", "autor": "J.R.R. Tolkien"},
# 6: {"titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry"},
# 7: {"titulo": "O Alquimista", "autor": "Paulo Coelho"},
# 8: {"titulo": "O Morro dos Ventos Uivantes", "autor": "Emily Brontë"},
# 9: {"titulo": "O Retrato de Dorian Gray", "autor": "Oscar Wilde"},
# 10: {"titulo": "O Grande Gatsby", "autor": "F. Scott Fitzgerald"},
# 11: {"titulo": "O Senhor dos Anéis: A Sociedade do Anel", "autor": "J.R.R. Tolkien"},
# 12: {"titulo": "O Senhor dos Anéis: As Duas Torres", "autor": "J.R.R. Tolkien"},
# 13: {"titulo": "O Senhor dos Anéis: O Retorno do Rei", "autor": "J.R.R. Tolkien"},
# 14: {"titulo": "Harry Potter e a Câmara Secreta", "autor": "J.K. Rowling"},
# 15: {"titulo": "Harry Potter e o Prisioneiro de Azkaban", "autor": "J.K. Rowling"},
# 16: {"titulo": "Harry Potter e o Cálice de Fogo", "autor": "J.K. Rowling"},
# 17: {"titulo": "Harry Potter e a Ordem da Fênix", " autor": "J.K. Rowling"},
# 18: {"titulo": "Harry Potter e o Enigma do Príncipe", "autor": "J.K. Rowling"},
# 19: {"titulo": "Harry Potter e as Relíquias da Morte", "autor": "J.K. Rowling"},
# 20: {"titulo": "O Código Da Vinci: O Símbolo Perdido", "autor": "Dan Brown"},