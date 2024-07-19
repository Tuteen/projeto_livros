from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel, QComboBox, QSpinBox, QMessageBox
from PySide6.QtGui import QIcon
import mysql.connector

class CriarLivro(QWidget):
    def __init__(self, controller, db_config, usuario_atual, nivel_acesso):
        super().__init__()
        self.controller = controller
        self.db_config = db_config
        self.usuario_atual = usuario_atual
        self.nivel_acesso = nivel_acesso
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Criar Livro')
        self.setWindowIcon(QIcon('logo.png'))  # Ajuste o caminho do ícone
        self.resize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QComboBox, QSpinBox {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 5px;
                background: #444;
                color: white;
            }
            QPushButton {
                border: 2px solid #555;
                border-radius: 10px;
                padding: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0081cb, stop:1 #00ccee);
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ccee, stop:1 #0081cb);
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.tipo_livro_combo = QComboBox()
        self.tipo_livro_combo.addItems(self.get_book_type_options())
        layout.addWidget(QLabel('Tipo de Livro:'))
        layout.addWidget(self.tipo_livro_combo)

        self.numero_livro_input = QLineEdit()
        layout.addWidget(QLabel('Número do Livro:'))
        layout.addWidget(self.numero_livro_input)

        self.quantidade_folhas_input = QSpinBox()
        self.quantidade_folhas_input.setRange(1, 1000)
        layout.addWidget(QLabel('Quantidade de Folhas:'))
        layout.addWidget(self.quantidade_folhas_input)

        self.termos_por_folha_input = QSpinBox()
        self.termos_por_folha_input.setRange(1, 4)
        self.termos_por_folha_input.setValue(1)
        layout.addWidget(QLabel('Termos por Folha:'))
        layout.addWidget(self.termos_por_folha_input)

        create_button = QPushButton('Criar Livro')
        create_button.clicked.connect(self.criar_livro)
        layout.addWidget(create_button)

        self.setLayout(layout)

    def get_book_type_options(self):
        if self.nivel_acesso == 'Admin':
            return ['NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                    'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)',
                    'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                    'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Tabelionato':
            return ['PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                    'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Registro Civil':
            return ['NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                    'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)']
        else:
            return []

    def criar_livro(self):
        tipo = self.tipo_livro_combo.currentText()
        numero = self.numero_livro_input.text()
        quantidade_folhas = self.quantidade_folhas_input.value()
        termos_por_folha = self.termos_por_folha_input.value()

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Livros (tipo, numero, usuario_criacao) VALUES (%s, %s, %s)', (tipo, numero, self.controller.usuario_atual))
        livro_id = cursor.lastrowid

        for folha_num in range(1, quantidade_folhas + 1):
            cursor.execute('INSERT INTO Folhas (id_livro, numero_folha, termos_por_folha, digitalizada) VALUES (%s, %s, %s, %s)', (livro_id, folha_num, termos_por_folha, False))
            folha_id = cursor.lastrowid
            for termo_num in range(1, termos_por_folha + 1):
                cursor.execute('INSERT INTO Termos (id_folha, numero_termo, digitalizado, usuario_modificacao, data_modificacao) VALUES (%s, %s, %s, %s, %s)', (folha_id, termo_num, False, None, None))

        conn.commit()
        conn.close()

        QMessageBox.information(self, 'Livro Criado', 'O livro foi criado com sucesso!')
        self.close()


