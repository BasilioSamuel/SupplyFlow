from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Troque para algo mais seguro em produção!

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
        try:
            cur.execute("INSERT INTO Fornecedor (nome_empresa, cnpj, email, senha) VALUES (%s, %s, %s, %s)",
                        (nome_empresa, cnpj, email, senha))
            mysql.connection.commit()
            flash('Fornecedor adicionado com sucesso!')
        except Exception as e:
            flash(f'Erro ao adicionar fornecedor: {str(e)}')
        finally:
            cur.close()

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

        try:
            cur.execute("""
                UPDATE Fornecedor 
                SET nome_empresa=%s, cnpj=%s, email=%s, senha=%s 
                WHERE id_fornecedor=%s
            """, (nome_empresa, cnpj, email, senha, id))
            mysql.connection.commit()
            flash('Fornecedor atualizado com sucesso!')
        except Exception as e:
            flash(f'Erro ao atualizar fornecedor: {str(e)}')
        finally:
            cur.close()
        return redirect(url_for('listar_fornecedores'))
    else:
        cur.execute("SELECT * FROM Fornecedor WHERE id_fornecedor=%s", (id,))
        fornecedor = cur.fetchone()
        cur.close()
        if not fornecedor:
            flash('Fornecedor não encontrado.')
            return redirect(url_for('listar_fornecedores'))
        return render_template('editar_fornecedor.html', fornecedor=fornecedor)

@app.route('/fornecedores/excluir/<int:id>', methods=['POST'])
def excluir_fornecedor(id):
    cur = mysql.connection.cursor()
    try:
        # Apaga produtos relacionados antes do fornecedor para manter integridade
        cur.execute("DELETE FROM Produto WHERE id_fornecedor = %s", (id,))
        cur.execute("DELETE FROM Fornecedor WHERE id_fornecedor = %s", (id,))
        mysql.connection.commit()
        flash("Fornecedor e produtos relacionados excluídos com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir fornecedor: {str(e)}")
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
        try:
            cur.execute("""
                INSERT INTO Produto (nome_produto, descricao, quantidade_produto, preco, id_fornecedor) 
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, descricao, quantidade_int, preco_float, id_fornecedor))
            mysql.connection.commit()
            flash('Produto adicionado com sucesso!')
        except Exception as e:
            flash(f'Erro ao adicionar produto: {str(e)}')
        finally:
            cur.close()

        return redirect(url_for('listar_produtos'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_fornecedor, nome_empresa FROM Fornecedor")
    fornecedores = cur.fetchall()
    cur.close()
    return render_template('adicionar_produto.html', fornecedores=fornecedores)

@app.route('/produtos/excluir/<int:id>', methods=['POST'])
def excluir_produto(id):
    cur = mysql.connection.cursor()
    try:
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
        endereco_comprador = request.form.get('endereco_comprador', '')
        cargo = request.form.get('cargo', '')
        setor = request.form.get('setor', '')
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
        except Exception as e:
            flash(f'Erro ao adicionar comprador: {str(e)}')
        finally:
            cur.close()
        return redirect(url_for('listar_compradores'))

    return render_template('adicionar_comprador.html')

@app.route('/compradores/editar/<int:id>', methods=['GET', 'POST'])
def editar_comprador(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        nome_funcionario = request.form['nome_funcionario']
        cpf_comprador = request.form['cpf_comprador']
        email = request.form['email']
        endereco_comprador = request.form.get('endereco_comprador', '')
        cargo = request.form.get('cargo', '')
        setor = request.form.get('setor', '')
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
        except Exception as e:
            flash(f'Erro ao atualizar comprador: {str(e)}')
        finally:
            cur.close()
        return redirect(url_for('listar_compradores'))
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
        flash("Comprador excluído com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir comprador: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('listar_compradores'))

# --- PAGAMENTOS ---
@app.route('/pagamentos')
def listar_pagamentos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT pg.id_pagamento, pg.valor_pagamento, pg.data_pagamento, pg.tipo_pagamento, pg.id_compra, c.nome_funcionario
        FROM Pagamento pg
        JOIN Compra c ON pg.id_compra = c.id_compra
    """)
    pagamentos = cur.fetchall()
    cur.close()
    return render_template('lista_pagamentos.html', pagamentos=pagamentos)

@app.route('/pagamentos/adicionar', methods=['GET', 'POST'])
def adicionar_pagamento():
    if request.method == 'POST':
        valor_pagamento = request.form.get('valor_pagamento')
        data_pagamento = request.form.get('data_pagamento')
        tipo_pagamento = request.form.get('tipo_pagamento')
        id_compra = request.form.get('id_compra')

        if not all([valor_pagamento, data_pagamento, tipo_pagamento, id_compra]):
            flash('Preencha todos os campos do pagamento.')
            return redirect(url_for('adicionar_pagamento'))

        try:
            valor_float = float(valor_pagamento)
            data_obj = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de valor ou data inválido.')
            return redirect(url_for('adicionar_pagamento'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO Pagamento (valor_pagamento, data_pagamento, tipo_pagamento, id_compra) 
                VALUES (%s, %s, %s, %s)
            """, (valor_float, data_obj, tipo_pagamento, id_compra))
            mysql.connection.commit()
            flash('Pagamento adicionado com sucesso!')
        except Exception as e:
            flash(f'Erro ao adicionar pagamento: {str(e)}')
        finally:
            cur.close()

        return redirect(url_for('listar_pagamentos'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_compra FROM Compra")
    compras = cur.fetchall()
    cur.close()
    return render_template('adicionar_pagamento.html', compras=compras)

@app.route('/pagamentos/excluir/<int:id>', methods=['POST'])
def excluir_pagamento(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Pagamento WHERE id_pagamento=%s", (id,))
        mysql.connection.commit()
        flash("Pagamento excluído com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir pagamento: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('listar_pagamentos'))

# --- COMPRAS ---
@app.route('/compras')
def listar_compras():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT c.id_compra, c.data_compra, c.valor_compra, c.id_fornecedor, c.id_comprador,
               f.nome_empresa, comp.nome_funcionario
        FROM Compra c
        JOIN Fornecedor f ON c.id_fornecedor = f.id_fornecedor
        JOIN Comprador comp ON c.id_comprador = comp.id_comprador
    """)
    compras = cur.fetchall()
    cur.close()
    return render_template('lista_compras.html', compras=compras)

@app.route('/compras/adicionar', methods=['GET', 'POST'])
def adicionar_compra():
    if request.method == 'POST':
        data_compra = request.form.get('data_compra')
        valor_compra = request.form.get('valor_compra')
        id_fornecedor = request.form.get('id_fornecedor')
        id_comprador = request.form.get('id_comprador')

        if not all([data_compra, valor_compra, id_fornecedor, id_comprador]):
            flash('Preencha todos os campos da compra.')
            return redirect(url_for('adicionar_compra'))

        try:
            data_obj = datetime.strptime(data_compra, '%Y-%m-%d').date()
            valor_float = float(valor_compra)
        except ValueError:
            flash('Formato de data ou valor inválido.')
            return redirect(url_for('adicionar_compra'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO Compra (data_compra, valor_compra, id_fornecedor, id_comprador)
                VALUES (%s, %s, %s, %s)
            """, (data_obj, valor_float, id_fornecedor, id_comprador))
            mysql.connection.commit()
            flash('Compra adicionada com sucesso!')
        except Exception as e:
            flash(f'Erro ao adicionar compra: {str(e)}')
        finally:
            cur.close()
        return redirect(url_for('listar_compras'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_fornecedor, nome_empresa FROM Fornecedor")
    fornecedores = cur.fetchall()
    cur.execute("SELECT id_comprador, nome_funcionario FROM Comprador")
    compradores = cur.fetchall()
    cur.close()
    return render_template('adicionar_compra.html', fornecedores=fornecedores, compradores=compradores)

@app.route('/compras/excluir/<int:id>', methods=['POST'])
def excluir_compra(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Compra WHERE id_compra=%s", (id,))
        mysql.connection.commit()
        flash("Compra excluída com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir compra: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('listar_compras'))

# --- MOVIMENTAÇÕES DE ESTOQUE ---
@app.route('/movimentacoes')
def listar_movimentacoes():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT m.id_movimentacao_estoque, m.id_produto, m.quantidade_movimentada, m.tipo_movimentacao, m.data_movimentacao,
               p.nome_produto
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
        quantidade = request.form.get('quantidade')
        tipo_movimentacao = request.form.get('tipo_movimentacao')
        data_movimentacao = request.form.get('data_movimentacao')

        if not all([id_produto, quantidade, tipo_movimentacao, data_movimentacao]):
            flash('Preencha todos os campos da movimentação.')
            return redirect(url_for('adicionar_movimentacao'))

        try:
            quantidade_int = int(quantidade)
            data_obj = datetime.strptime(data_movimentacao, '%Y-%m-%d').date()
        except ValueError:
            flash('Quantidade ou data inválida.')
            return redirect(url_for('adicionar_movimentacao'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO Movimentacao_Estoque (id_produto, quantidade_movimentada, tipo_movimentacao, data_movimentacao)
                VALUES (%s, %s, %s, %s)
            """, (id_produto, quantidade_int, tipo_movimentacao, data_obj))
            mysql.connection.commit()
            flash('Movimentação adicionada com sucesso!')
        except Exception as e:
            flash(f'Erro ao adicionar movimentação: {str(e)}')
        finally:
            cur.close()
        return redirect(url_for('listar_movimentacoes'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_produto, nome_produto FROM Produto")
    produtos = cur.fetchall()
    cur.close()
    return render_template('adicionar_movimentacao.html', produtos=produtos)

@app.route('/movimentacoes/excluir/<int:id>', methods=['POST'])
def excluir_movimentacao(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Movimentacao_Estoque WHERE id_movimentacao_estoque=%s", (id,))
        mysql.connection.commit()
        flash("Movimentação excluída com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir movimentação: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('listar_movimentacoes'))

if __name__ == '__main__':
    app.run(debug=True)
