from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
app.config['MYSQL_DB'] = 'brmw'

mysql = MySQL(app)

# Rota principal - Menu
@app.route('/')
def menu():
    return render_template('menu.html')

# --- FORNECEDORES ---
@app.route('/fornecedores')
def listar_fornecedores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Fornecedor")
    fornecedores = cur.fetchall()
    cur.close()
    return render_template('lista_fornecedores.html', fornecedores=fornecedores)

@app.route('/fornecedores/adicionar', methods=['GET', 'POST'])
def adicionar_fornecedor():
    if request.method == 'POST':
        nome_empresa = request.form['nome_empresa']
        cnpj = request.form['cnpj']
        email = request.form['email']
        senha = request.form['senha']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Fornecedor (nome_empresa, cnpj, email, senha) VALUES (%s, %s, %s, %s)",
                    (nome_empresa, cnpj, email, senha))
        mysql.connection.commit()
        cur.close()
        flash('Fornecedor adicionado com sucesso!')
        return redirect(url_for('listar_fornecedores'))
    return render_template('adicionar_fornecedor.html')

@app.route('/fornecedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_fornecedor(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nome_empresa = request.form['nome_empresa']
        cnpj = request.form['cnpj']
        email = request.form['email']
        senha = request.form['senha']
        
        cur.execute("""
            UPDATE Fornecedor 
            SET nome_empresa=%s, cnpj=%s, email=%s, senha=%s 
            WHERE id_fornecedor=%s
        """, (nome_empresa, cnpj, email, senha, id))
        mysql.connection.commit()
        cur.close()
        flash('Fornecedor atualizado com sucesso!')
        return redirect(url_for('listar_fornecedores'))
    else:
        cur.execute("SELECT * FROM Fornecedor WHERE id_fornecedor=%s", (id,))
        fornecedor = cur.fetchone()
        cur.close()
        return render_template('editar_fornecedor.html', fornecedor=fornecedor)

@app.route('/fornecedores/excluir/<int:id>', methods=['POST'])
def excluir_fornecedor(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Produto WHERE id_fornecedor = %s", (id,))
        cur.execute("DELETE FROM Fornecedor WHERE id_fornecedor = %s", (id,))
        mysql.connection.commit()
        flash("Fornecedor e produtos relacionados excluídos com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('listar_fornecedores'))

# --- PRODUTOS ---
@app.route('/produtos')
def listar_produtos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT p.id_produto, p.nome_produto, p.quantidade_produto, p.descricao, p.numero_produto, p.preco, f.nome_empresa
        FROM Produto p
        JOIN Fornecedor f ON p.id_fornecedor = f.id_fornecedor
    """)
    produtos = cur.fetchall()
    cur.close()
    return render_template('lista_produtos.html', produtos=produtos)

@app.route('/produtos/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form.get('nome_produto')
        descricao = request.form.get('descricao')
        quantidade = request.form.get('quantidade_produto')
        preco = request.form.get('preco')
        id_fornecedor = request.form.get('id_fornecedor')

        if not all([nome, descricao, quantidade, preco, id_fornecedor]):
            flash("Por favor, preencha todos os campos do formulário.")
            return redirect(url_for('adicionar_produto'))

        try:
            quantidade_int = int(quantidade)
            preco_float = float(preco)
        except ValueError:
            flash("Quantidade ou preço inválido. Use valores numéricos.")
            return redirect(url_for('adicionar_produto'))

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Produto (nome_produto, descricao, quantidade_produto, preco, id_fornecedor) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, descricao, quantidade_int, preco_float, id_fornecedor))
        mysql.connection.commit()
        cur.close()
        flash('Produto adicionado com sucesso!')
        return redirect(url_for('listar_produtos'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_fornecedor, nome_empresa FROM Fornecedor")
    fornecedores = cur.fetchall()
    cur.close()
    return render_template('adicionar_produto.html', fornecedores=fornecedores)

@app.route('/produtos/excluir/<int:id>', methods=['POST'])
def excluir_produto(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Produto WHERE id_produto = %s", (id,))
        mysql.connection.commit()
        flash("Produto excluído com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir produto: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('listar_produtos'))

# --- COMPRADORES ---
@app.route('/compradores')
def listar_compradores():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM Comprador")
    compradores = cur.fetchall()
    cur.close()
    return render_template('lista_compradores.html', compradores=compradores)

@app.route('/compradores/adicionar', methods=['GET', 'POST'])
def adicionar_comprador():
    if request.method == 'POST':
        nome_funcionario = request.form['nome_funcionario']
        cpf_comprador = request.form['cpf_comprador']
        email = request.form['email']
        endereco_comprador = request.form['endereco_comprador']
        cargo = request.form['cargo']
        setor = request.form['setor']
        senha = request.form['senha']

        if not all([nome_funcionario, cpf_comprador, email, senha]):
            flash('Preencha os campos obrigatórios: Nome, CPF, Email e Senha.')
            return redirect(url_for('adicionar_comprador'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO Comprador 
                (nome_funcionario, cpf_comprador, email, endereco_comprador, cargo, setor, senha)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nome_funcionario, cpf_comprador, email, endereco_comprador, cargo, setor, senha))
            mysql.connection.commit()
            flash('Comprador adicionado com sucesso!')
            return redirect(url_for('listar_compradores'))
        except Exception as e:
            flash(f'Erro ao adicionar comprador: {str(e)}')
            return redirect(url_for('adicionar_comprador'))
        finally:
            cur.close()

    return render_template('adicionar_comprador.html')

@app.route('/compradores/editar/<int:id>', methods=['GET', 'POST'])
def editar_comprador(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nome_funcionario = request.form['nome_funcionario']
        cpf_comprador = request.form['cpf_comprador']
        email = request.form['email']
        endereco_comprador = request.form['endereco_comprador']
        cargo = request.form['cargo']
        setor = request.form['setor']
        senha = request.form['senha']

        if not all([nome_funcionario, cpf_comprador, email, senha]):
            flash('Preencha os campos obrigatórios: Nome, CPF, Email e Senha.')
            return redirect(url_for('editar_comprador', id=id))

        try:
            cur.execute("""
                UPDATE Comprador SET 
                    nome_funcionario=%s, cpf_comprador=%s, email=%s, endereco_comprador=%s, 
                    cargo=%s, setor=%s, senha=%s
                WHERE id_comprador=%s
            """, (nome_funcionario, cpf_comprador, email, endereco_comprador, cargo, setor, senha, id))
            mysql.connection.commit()
            flash('Comprador atualizado com sucesso!')
            return redirect(url_for('listar_compradores'))
        except Exception as e:
            flash(f'Erro ao atualizar comprador: {str(e)}')
            return redirect(url_for('editar_comprador', id=id))
        finally:
            cur.close()
    else:
        cur.execute("SELECT * FROM Comprador WHERE id_comprador=%s", (id,))
        comprador = cur.fetchone()
        cur.close()
        if not comprador:
            flash('Comprador não encontrado.')
            return redirect(url_for('listar_compradores'))
        return render_template('editar_comprador.html', comprador=comprador)

@app.route('/compradores/excluir/<int:id>', methods=['POST'])
def excluir_comprador(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Comprador WHERE id_comprador=%s", (id,))
        mysql.connection.commit()
        flash('Comprador excluído com sucesso!')
    except Exception as e:
        flash(f'Erro ao excluir comprador: {str(e)}')
    finally:
        cur.close()
    return redirect(url_for('listar_compradores'))

# --- PAGAMENTOS ---
@app.route('/pagamentos')
def listar_pagamentos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT p.id_pagamento, c.nome_funcionario, pr.nome_produto, p.metodo_pag, p.endereco_pag, p.data_compra, p.hora_pag
        FROM Pagamento p
        JOIN Comprador c ON p.id_comprador = c.id_comprador
        JOIN Produto pr ON p.id_produto = pr.id_produto
        ORDER BY p.data_compra DESC, p.hora_pag DESC
    """)
    pagamentos = cur.fetchall()
    cur.close()
    return render_template('lista_pagamentos.html', pagamentos=pagamentos)

@app.route('/pagamentos/adicionar', methods=['GET', 'POST'])
def adicionar_pagamento():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        id_comprador = request.form.get('id_comprador')
        id_produto = request.form.get('id_produto')
        metodo_pag = request.form.get('metodo_pag')
        endereco_pag = request.form.get('endereco_pag')
        data_compra = request.form.get('data_compra')
        hora_pag = request.form.get('hora_pag')

        if not all([id_comprador, id_produto, metodo_pag, data_compra, hora_pag]):
            flash("Preencha todos os campos obrigatórios.")
            return redirect(url_for('adicionar_pagamento'))

        try:
            # Validação básica das datas pode ser adicionada aqui, opcional.
            datetime.strptime(data_compra, '%Y-%m-%d')
            datetime.strptime(hora_pag, '%H:%M')
        except ValueError:
            flash("Formato de data ou hora inválido.")
            return redirect(url_for('adicionar_pagamento'))

        try:
            cur.execute("""
                INSERT INTO Pagamento (id_comprador, id_produto, metodo_pag, endereco_pag, data_compra, hora_pag)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_comprador, id_produto, metodo_pag, endereco_pag, data_compra, hora_pag))
            mysql.connection.commit()
            flash('Pagamento registrado com sucesso!')
            return redirect(url_for('listar_pagamentos'))
        except Exception as e:
            flash(f"Erro ao registrar pagamento: {str(e)}")
            return redirect(url_for('adicionar_pagamento'))
        finally:
            cur.close()
    else:
        cur.execute("SELECT id_comprador, nome_funcionario FROM Comprador")
        compradores = cur.fetchall()
        cur.execute("SELECT id_produto, nome_produto FROM Produto")
        produtos = cur.fetchall()
        cur.close()
        return render_template('adicionar_pagamento.html', compradores=compradores, produtos=produtos)

@app.route('/pagamentos/excluir/<int:id>', methods=['POST'])
def excluir_pagamento(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Pagamento WHERE id_pagamento=%s", (id,))
        mysql.connection.commit()
        flash('Pagamento excluído com sucesso!')
    except Exception as e:
        flash(f'Erro ao excluir pagamento: {str(e)}')
    finally:
        cur.close()
    return redirect(url_for('listar_pagamentos'))

# --- COMPRAS ---
@app.route('/compras')
def listar_compras():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT co.id_compra, co.quantidade, co.data_compra, co.valor_total, p.nome_produto, f.nome_empresa
        FROM Compra co
        JOIN Produto p ON co.id_produto = p.id_produto
        JOIN Fornecedor f ON p.id_fornecedor = f.id_fornecedor
        ORDER BY co.data_compra DESC
    """)
    compras = cur.fetchall()
    cur.close()
    return render_template('lista_compras.html', compras=compras)

@app.route('/compras/adicionar', methods=['GET', 'POST'])
def adicionar_compra():
    if request.method == 'POST':
        id_produto = request.form.get('id_produto')
        quantidade = request.form.get('quantidade')
        valor_total = request.form.get('valor_total')
        data_compra = request.form.get('data_compra')

        if not all([id_produto, quantidade, valor_total, data_compra]):
            flash('Preencha todos os campos.')
            return redirect(url_for('adicionar_compra'))

        try:
            quantidade_int = int(quantidade)
            valor_float = float(valor_total)
            datetime.strptime(data_compra, '%Y-%m-%d')
        except ValueError:
            flash('Dados inválidos em quantidade, valor ou data.')
            return redirect(url_for('adicionar_compra'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO Compra (id_produto, quantidade, valor_total, data_compra)
                VALUES (%s, %s, %s, %s)
            """, (id_produto, quantidade_int, valor_float, data_compra))
            mysql.connection.commit()
            flash('Compra registrada com sucesso!')
            return redirect(url_for('listar_compras'))
        except Exception as e:
            flash(f'Erro ao registrar compra: {str(e)}')
            return redirect(url_for('adicionar_compra'))
        finally:
            cur.close()
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_produto, nome_produto FROM Produto")
        produtos = cur.fetchall()
        cur.close()
        return render_template('adicionar_compra.html', produtos=produtos)

@app.route('/compras/excluir/<int:id>', methods=['POST'])
def excluir_compra(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Compra WHERE id_compra=%s", (id,))
        mysql.connection.commit()
        flash('Compra excluída com sucesso!')
    except Exception as e:
        flash(f'Erro ao excluir compra: {str(e)}')
    finally:
        cur.close()
    return redirect(url_for('listar_compras'))

# --- MOVIMENTAÇÃO DE ESTOQUE ---
@app.route('/movimentacoes')
def listar_movimentacoes():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
    SELECT m.id_movimentacao_estoque, p.nome_produto, m.quantidade, m.data_movimentacao
    FROM Movimentacao_Estoque m
    JOIN Produto p ON m.id_produto = p.id_produto
    ORDER BY m.data_movimentacao DESC
""")

    movimentacoes = cur.fetchall()
    cur.close()
    return render_template('lista_movimentacoes.html', movimentacoes=movimentacoes)

@app.route('/movimentacoes/adicionar', methods=['GET', 'POST'])
def adicionar_movimentacao():
    if request.method == 'POST':
        id_produto = request.form.get('id_produto')
        quantidade = request.form.get('quantidade_movimentada')
        tipo = request.form.get('tipo_movimentacao')
        data = request.form.get('data_movimentacao')

        if not all([id_produto, quantidade, tipo, data]):
            flash('Preencha todos os campos.')
            return redirect(url_for('adicionar_movimentacao'))

        try:
            quantidade_int = int(quantidade)
            datetime.strptime(data, '%Y-%m-%d')
        except ValueError:
            flash('Quantidade ou data inválida.')
            return redirect(url_for('adicionar_movimentacao'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO Movimentacao_Estoque (id_produto, quantidade_movimentada, tipo_movimentacao, data_movimentacao)
                VALUES (%s, %s, %s, %s)
            """, (id_produto, quantidade_int, tipo, data))
            mysql.connection.commit()
            flash('Movimentação registrada com sucesso!')
            return redirect(url_for('listar_movimentacoes'))
        except Exception as e:
            flash(f'Erro ao registrar movimentação: {str(e)}')
            return redirect(url_for('adicionar_movimentacao'))
        finally:
            cur.close()
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_produto, nome_produto FROM Produto")
        produtos = cur.fetchall()
        cur.close()
        return render_template('adicionar_movimentacao.html', produtos=produtos)

@app.route('/movimentacoes/excluir/<int:id>', methods=['POST'])
def excluir_movimentacao(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Movimentacao_Estoque WHERE id_movimentacao=%s", (id,))
        mysql.connection.commit()
        flash('Movimentação excluída com sucesso!')
    except Exception as e:
        flash(f'Erro ao excluir movimentação: {str(e)}')
    finally:
        cur.close()
    return redirect(url_for('listar_movimentacoes'))

if __name__ == '__main__':
    app.run(debug=True)
