import sqlite3
from pathlib import Path

DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE = DATABASE_DIR / "gastos.db"


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            renda REAL DEFAULT 0
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL
        )
    """)

    quantidade = conexao.execute(
        "SELECT COUNT(*) FROM configuracoes"
    ).fetchone()[0]

    if quantidade == 0:
        conexao.execute(
            "INSERT INTO configuracoes (renda) VALUES (?)",
            (0,)
        )

    conexao.commit()
    conexao.close()


def obter_renda():
    conexao = conectar()

    resultado = conexao.execute(
        "SELECT renda FROM configuracoes WHERE id = 1"
    ).fetchone()

    conexao.close()

    return resultado["renda"] if resultado else 0


def atualizar_renda(renda):
    conexao = conectar()

    conexao.execute(
        "UPDATE configuracoes SET renda = ? WHERE id = 1",
        (renda,)
    )

    conexao.commit()
    conexao.close()


def adicionar_gasto(descricao, categoria, valor, data):
    conexao = conectar()

    conexao.execute("""
        INSERT INTO gastos
        (descricao, categoria, valor, data)
        VALUES (?, ?, ?, ?)
    """, (descricao, categoria, valor, data))

    conexao.commit()
    conexao.close()


def obter_gastos():
    conexao = conectar()

    gastos = conexao.execute("""
        SELECT *
        FROM gastos
        ORDER BY data DESC, id DESC
    """).fetchall()

    conexao.close()

    return gastos


def excluir_gasto(gasto_id):
    conexao = conectar()

    conexao.execute(
        "DELETE FROM gastos WHERE id = ?",
        (gasto_id,)
    )

    conexao.commit()
    conexao.close()


def obter_total_gastos():
    conexao = conectar()

    resultado = conexao.execute(
        "SELECT COALESCE(SUM(valor), 0) AS total FROM gastos"
    ).fetchone()

    conexao.close()

    return resultado["total"]