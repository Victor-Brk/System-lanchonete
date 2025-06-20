# 🍔 System.lanchonete

Esse é um sistema pra lanchonete, feito em Python com Flask. Dá pra cliente ver o cardápio, colocar no carrinho, finalizar pedido. Tem login normal e painel de admin pra cadastrar produto.

# O que ele faz ?

- Cadastro e login (cliente e admin)  
- Admin pode criar, editar e excluir produto  
- Cliente vê o cardápio, adiciona no carrinho e faz pedido  
- Tudo salvo no banco SQLite  
- Visual simples, mas moderninho com CSS.

# Como rodar na sua máquina ?

1 clone o projeto
2 Instale o Flask e as libs no cmd: pip install flask flask_sqlalchemy werkzeug
3 Depois rode o sistema: python app.py

4 Crie o banco e o admin:
Abra no navegador e cole http://localhost:5000/init
Ele cria o banco e um admin padrão...

5 Entre no navegador:
http://localhost:5000

# login:
Admin: admin@admin.com / admin123

Obs: Cliente pode se cadastrar normal

# Como o sistema funciona
Backend em Python com Flask e SQLite

Frontend em HTML com templates do Flask

Sessão salva login e carrinho

Admin gerencia produtos (cria, edita, apaga)

Cliente vê cardápio, adiciona no carrinho e faz pedido.

# Licença...
pode usar e modificar sem stress.
