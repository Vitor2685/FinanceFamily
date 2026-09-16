from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "chave-local-desenvolvimento"
)

DATABASE = "database.db"

# ---------------------------------------------------
# CONFIGURAÇÃO DO LOGIN
# ---------------------------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------------------------------------------
# CONEXÃO COM BANCO
# ---------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------
# CRIAÇÃO DAS TABELAS
# ---------------------------------------------------

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------
# USUÁRIO DO FLASK-LOGIN
# ---------------------------------------------------

class User(UserMixin):

    def __init__(self, id, nome, email, senha):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha


@login_manager.user_loader
def load_user(user_id):

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()

    if user:
        return User(
            user["id"],
            user["nome"],
            user["email"],
            user["senha"]
        )

    return None


# ---------------------------------------------------
# PÁGINA INICIAL
# ---------------------------------------------------

@app.route("/")
@login_required
def index():

    conn = get_db()

    gastos = conn.execute(
        """
        SELECT *
        FROM gastos
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (current_user.id,)
    ).fetchall()

    total = conn.execute(
        """
        SELECT COALESCE(SUM(valor), 0)
        FROM gastos
        WHERE user_id = ?
        """,
        (current_user.id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        gastos=gastos,
        total=total
    )


# ---------------------------------------------------
# CADASTRO
# ---------------------------------------------------

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        if not nome or not email or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for("cadastro"))

        if len(senha) < 6:
            flash("A senha precisa ter pelo menos 6 caracteres.")
            return redirect(url_for("cadastro"))

        senha_hash = generate_password_hash(senha)

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (nome, email, senha)
                VALUES (?, ?, ?)
                """,
                (nome, email, senha_hash)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            flash("Esse e-mail já está cadastrado.")
            return redirect(url_for("cadastro"))

        conn.close()

        flash("Cadastro realizado com sucesso!")

        return redirect(url_for("login"))

    return render_template("cadastro.html")


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["senha"], senha):

            usuario = User(
                user["id"],
                user["nome"],
                user["email"],
                user["senha"]
            )

            login_user(usuario)

            return redirect(url_for("index"))

        flash("E-mail ou senha incorretos.")

    return render_template("login.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# ---------------------------------------------------
# ADICIONAR GASTO
# ---------------------------------------------------

@app.route("/adicionar", methods=["POST"])
@login_required
def adicionar():

    descricao = request.form["descricao"]
    valor = request.form["valor"]
    categoria = request.form["categoria"]

    try:
        valor = float(valor.replace(",", "."))
    except ValueError:

        flash("Digite um valor válido.")

        return redirect(url_for("index"))

    conn = get_db()

    conn.execute(
        """
        INSERT INTO gastos
        (user_id, descricao, valor, categoria)
        VALUES (?, ?, ?, ?)
        """,
        (
            current_user.id,
            descricao,
            valor,
            categoria
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# ---------------------------------------------------
# EXCLUIR GASTO
# ---------------------------------------------------

@app.route("/excluir/<int:gasto_id>")
@login_required
def excluir(gasto_id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM gastos
        WHERE id = ?
        AND user_id = ?
        """,
        (
            gasto_id,
            current_user.id
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# ---------------------------------------------------
# INICIAR SISTEMA
# ---------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )