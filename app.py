from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'segredo123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

@app.route("/")
def index():
    return render_template("index.html", usuario=session.get("usuario"))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        novo = Usuario(nome=nome, email=email, senha=senha, tipo="cliente")
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario"] = {"id": usuario.id, "nome": usuario.nome, "tipo": usuario.tipo}
            return redirect(url_for("index"))
        return render_template("login.html", erro="Email ou senha inválidos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("index"))

@app.route("/admin")
def admin_painel():
    if not session.get("usuario") or session["usuario"]["tipo"] != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/admin/produtos")
def admin_produtos():
    if not session.get("usuario") or session["usuario"]["tipo"] != "admin":
        return redirect(url_for("login"))
    produtos = Produto.query.all()
    return render_template("produtos.html", produtos=produtos)

@app.route("/admin/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    if not session.get("usuario") or session["usuario"]["tipo"] != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        nome = request.form["nome"]
        preco = float(request.form["preco"])
        db.session.add(Produto(nome=nome, preco=preco))
        db.session.commit()
        return redirect(url_for("admin_produtos"))
    return render_template("form_produto.html", acao="Adicionar")

@app.route("/admin/produtos/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    if not session.get("usuario") or session["usuario"]["tipo"] != "admin":
        return redirect(url_for("login"))
    produto = Produto.query.get_or_404(id)
    if request.method == "POST":
        produto.nome = request.form["nome"]
        produto.preco = float(request.form["preco"])
        db.session.commit()
        return redirect(url_for("admin_produtos"))
    return render_template("form_produto.html", acao="Editar", produto=produto)

@app.route("/admin/produtos/deletar/<int:id>")
def deletar_produto(id):
    if not session.get("usuario") or session["usuario"]["tipo"] != "admin":
        return redirect(url_for("login"))
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for("admin_produtos"))

@app.route("/cardapio")
def cardapio():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    produtos = Produto.query.all()
    return render_template("cardapio.html", produtos=produtos)

@app.route("/adicionar/<int:id>")
def adicionar_carrinho(id):
    if "carrinho" not in session:
        session["carrinho"] = {}
    carrinho = session["carrinho"]
    carrinho[str(id)] = carrinho.get(str(id), 0) + 1
    session["carrinho"] = carrinho
    return redirect(url_for("cardapio"))

@app.route("/carrinho")
def ver_carrinho():
    if "carrinho" not in session or not session["carrinho"]:
        return render_template("carrinho.html", itens=[], total=0)
    carrinho = session["carrinho"]
    itens = []
    total = 0
    for id, qtd in carrinho.items():
        produto = Produto.query.get(int(id))
        subtotal = produto.preco * qtd
        itens.append({"produto": produto, "quantidade": qtd, "subtotal": subtotal})
        total += subtotal
    return render_template("carrinho.html", itens=itens, total=total)

@app.route("/remover/<int:id>")
def remover_item(id):
    carrinho = session.get("carrinho", {})
    carrinho.pop(str(id), None)
    session["carrinho"] = carrinho
    return redirect(url_for("ver_carrinho"))

@app.route("/finalizar")
def finalizar_pedido():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    carrinho = session.get("carrinho", {})
    if not carrinho:
        return redirect(url_for("ver_carrinho"))
    total = 0
    for id, qtd in carrinho.items():
        produto = Produto.query.get(int(id))
        total += produto.preco * qtd
    pedido = Pedido(usuario_id=session["usuario"]["id"], total=total)
    db.session.add(pedido)
    db.session.commit()
    for id, qtd in carrinho.items():
        item = ItemPedido(pedido_id=pedido.id, produto_id=int(id), quantidade=qtd)
        db.session.add(item)
    db.session.commit()
    session["carrinho"] = {}
    return "Pedido finalizado com sucesso!"

@app.route("/init")
def init():
    db.create_all()
    if Usuario.query.filter_by(email="admin@admin.com").first() is None:
        admin = Usuario(nome="Admin", email="admin@admin.com", senha=generate_password_hash("admin123"), tipo="admin")
        db.session.add(admin)
        db.session.commit()
    return "Banco de dados criado com sucesso e admin inserido!"

if __name__ == '__main__':
    app.run(debug=True)
