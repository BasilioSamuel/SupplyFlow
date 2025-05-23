-- Criar banco e usar
DROP DATABASE IF EXISTS brmw;
CREATE DATABASE brmw;
USE brmw;

-- Tabela: Fornecedor
CREATE TABLE Fornecedor (
    id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
    nome_empresa VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    email VARCHAR(100),
    senha VARCHAR(100)
);

-- Tabela: Produto
CREATE TABLE Produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome_produto VARCHAR(100) NOT NULL,
    quantidade_produto INT,
    descricao TEXT,
    numero_produto VARCHAR(50),
    id_fornecedor INT NOT NULL,
    FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela: Comprador
CREATE TABLE Comprador (
    id_comprador INT AUTO_INCREMENT PRIMARY KEY,
    nome_funcionario VARCHAR(100),
    cpf_comprador VARCHAR(14) UNIQUE,
    email VARCHAR(100),
    endereco_comprador VARCHAR(200),
    cargo VARCHAR(50),
    setor VARCHAR(50),
    senha VARCHAR(100)
);

-- Tabela: Pagamento
CREATE TABLE Pagamento (
    id_pagamento INT AUTO_INCREMENT PRIMARY KEY,
    id_comprador INT NOT NULL,
    id_produto INT NOT NULL,
    metodo_pag VARCHAR(50),
    endereco_pag VARCHAR(200),
    data_compra DATE,
    hora_pag TIME,
    FOREIGN KEY (id_comprador) REFERENCES Comprador(id_comprador)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabela: Compra
CREATE TABLE Compra (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_comprador INT NOT NULL,
    id_pagamento INT NOT NULL UNIQUE,
    FOREIGN KEY (id_comprador) REFERENCES Comprador(id_comprador)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_pagamento) REFERENCES Pagamento(id_pagamento)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabela: Movimentacao_Estoque
CREATE TABLE Movimentacao_Estoque (
    id_movimentacao_estoque INT AUTO_INCREMENT PRIMARY KEY,
    id_produto INT NOT NULL,
    quantidade INT,
    data_movimentacao DATE,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Inserir dados exemplo

INSERT INTO Fornecedor (nome_empresa, cnpj, email, senha) VALUES
('Fornecedor A', '12.345.678/0001-90', 'contato@forna.com', 'senha123'),
('Fornecedor B', '98.765.432/0001-10', 'contato@fornb.com', 'senha456');

INSERT INTO Produto (nome_produto, quantidade_produto, descricao, numero_produto, id_fornecedor) VALUES
('Mouse Gamer', 150, 'Mouse com iluminação RGB', 'MG001', 1),
('Teclado Mecânico', 80, 'Teclado com switches azuis', 'TM002', 2);

INSERT INTO Comprador (nome_funcionario, cpf_comprador, email, endereco_comprador, cargo, setor, senha) VALUES
('João Silva', '123.456.789-00', 'joao@empresa.com', 'Rua A, 123', 'Analista', 'TI', 'senha1'),
('Maria Souza', '987.654.321-00', 'maria@empresa.com', 'Rua B, 456', 'Compradora', 'Compras', 'senha2');

INSERT INTO Pagamento (id_comprador, id_produto, metodo_pag, endereco_pag, data_compra, hora_pag) VALUES
(1, 1, 'Cartão de Crédito', 'Rua A, 123', '2025-05-01', '14:00:00'),
(2, 2, 'Boleto Bancário', 'Rua B, 456', '2025-05-02', '09:30:00');

INSERT INTO Compra (id_comprador, id_pagamento) VALUES
(1, 1),
(2, 2);

INSERT INTO Movimentacao_Estoque (id_produto, quantidade, data_movimentacao) VALUES
(1, -10, '2025-05-01'),
(2, -5, '2025-05-02');

-- Consultas de exemplo (tire o -- para executar)

-- Ver produtos com fornecedores
-- SELECT p.nome_produto, p.quantidade_produto, f.nome_empresa
-- FROM Produto p
-- JOIN Fornecedor f ON p.id_fornecedor = f.id_fornecedor;

-- Ver compradores e compras
-- SELECT c.nome_funcionario, co.id_compra, pg.metodo_pag, pg.data_compra
-- FROM Comprador c
-- JOIN Compra co ON c.id_comprador = co.id_comprador
-- JOIN Pagamento pg ON co.id_pagamento = pg.id_pagamento;

-- Ver movimentações de estoque
-- SELECT me.data_movimentacao, me.quantidade, p.nome_produto
-- FROM Movimentacao_Estoque me
-- JOIN Produto p ON me.id_produto = p.id_produto;
