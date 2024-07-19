import sys
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QLineEdit, QMessageBox, QComboBox
)
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtCore import Qt
from dialog_digit import DialogoDigitalizacao

class TelaListarLivros(QWidget):
    def __init__(self, db_config, nome_completo, nivel_acesso):
        super().__init__()
        self.db_config = db_config
        self.usuario_atual = nome_completo
        self.nivel_acesso = nivel_acesso
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Listar Livros e Detalhes')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel, QPushButton, QLineEdit, QComboBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 10px;
                padding: 5px;
                background: #444;
                color: white;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0081cb, stop:1 #00ccee);
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00ccee, stop:1 #0081cb);
            }
        """)

        main_layout = QHBoxLayout(self)

        # Barra de pesquisa
        search_layout = QVBoxLayout()
        self.book_type_filter = QComboBox()
        self.book_type_filter.addItems(self.get_book_type_options())
        self.book_search_input = QLineEdit()
        self.book_search_input.setPlaceholderText('Buscar Número do Livro')
        self.folha_search_input = QLineEdit()
        self.folha_search_input.setPlaceholderText('Buscar Folha')
        self.termo_search_input = QLineEdit()
        self.termo_search_input.setPlaceholderText('Buscar Termo')

        search_button = QPushButton('Buscar')
        search_button.clicked.connect(self.carregar_livros)

        search_layout.addWidget(self.book_type_filter)
        search_layout.addWidget(self.book_search_input)
        search_layout.addWidget(self.folha_search_input)
        search_layout.addWidget(self.termo_search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Listas para livros, folhas e termos
        self.lista_livros = QListWidget()
        self.lista_livros.currentItemChanged.connect(self.mostrar_folhas)
        main_layout.addWidget(self.lista_livros)

        self.lista_folhas = QListWidget()
        self.lista_folhas.currentItemChanged.connect(self.mostrar_termos)
        main_layout.addWidget(self.lista_folhas)

        self.lista_termos = QListWidget()
        self.lista_termos.itemClicked.connect(self.marcar_como_digitalizado)
        main_layout.addWidget(self.lista_termos)

        self.carregar_livros()

    def get_book_type_options(self):
        if self.nivel_acesso == 'Admin':
            return ['Todos', 'NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                    'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)',
                    'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                    'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Tabelionato':
            return ['Todos', 'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                    'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Registro Civil':
            return ['Todos', 'NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                    'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)']
        else:
            return ['Todos']

    def carregar_livros(self):
        self.lista_livros.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        tipo_livro = '%' if self.book_type_filter.currentText() == 'Todos' else self.book_type_filter.currentText()
        numero_livro = '%' if not self.book_search_input.text().strip() else f'%{self.book_search_input.text().strip()}%'

        if self.nivel_acesso == 'Tabelionato':
            tipos_permitidos = ['PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                                'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']
        elif self.nivel_acesso == 'Registro Civil':
            tipos_permitidos = ['NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                                'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)']
        else:  # Admin
            tipos_permitidos = ['NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)',
                                'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)',
                                'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)',
                                'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)']

        query = f"""
        SELECT Livros.id, Livros.tipo, Livros.numero, 
            CASE 
                WHEN SUM(CASE WHEN Folhas.digitalizada = 0 THEN 1 ELSE 0 END) = 0 THEN 'Completamente Digitalizado'
                ELSE 'Parcialmente Digitalizado'
            END AS digitalizacao_status
        FROM Livros
        LEFT JOIN Folhas ON Livros.id = Folhas.id_livro
        WHERE Livros.tipo LIKE %s AND Livros.numero LIKE %s AND Livros.tipo IN ({','.join(['%s'] * len(tipos_permitidos))})
        GROUP BY Livros.id
        ORDER BY FIELD(Livros.tipo, 'NASCIMENTO (LIVRO A)', 'CASAMENTO CIVIL (LIVRO B)', 'CAS. REL. CIVIL (LIVRO BA)', 'ÓBITO (LIVRO C)', 'NATIMORTO (LIVRO CA)', 'PROCLAMAS (LIVRO D)', 'PROCURAÇÕES (LIVRO P)', 'SUBSTABELECIMENTOS (LIVRO S)', 'ESCRITURAS DE COMPRA E VENDA (LIVRO N)', 'ESCRITURAS DIVERSAS (LIVRO TD)', 'TESTAMENTO (LIVRO T)'), CAST(Livros.numero AS UNSIGNED)
        """
        cursor.execute(query, [tipo_livro, numero_livro] + tipos_permitidos)
        for livro in cursor.fetchall():
            item = QListWidgetItem(f"{livro[1]} - {livro[2]} ({livro[3]})")
            item.setData(1000, livro[0])
            if livro[3] == 'Completamente Digitalizado':
                item.setBackground(QColor("#006400"))
            self.lista_livros.addItem(item)
        conn.close()

    def mostrar_folhas(self, current, previous):
        if not current:
            return
        livro_id = current.data(1000)
        self.lista_folhas.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        query = """
        SELECT Folhas.id, Folhas.numero_folha,
            CASE 
                WHEN SUM(CASE WHEN Termos.digitalizado = 0 THEN 1 ELSE 0 END) = 0 THEN 'Completamente Digitalizado'
                ELSE 'Digitalizar'
            END AS digitalizacao_status
        FROM Folhas
        LEFT JOIN Termos ON Folhas.id = Termos.id_folha
        WHERE Folhas.id_livro = %s AND Folhas.numero_folha LIKE %s
        GROUP BY Folhas.id
        """
        cursor.execute(query, (livro_id, '%' + self.folha_search_input.text() + '%',))
        for folha in cursor.fetchall():
            item = QListWidgetItem(f"Folha {folha[1]} ({folha[2]})")
            item.setData(1000, folha[0])
            if folha[2] == 'Completamente Digitalizado':
                item.setBackground(QColor("#006400"))
            self.lista_folhas.addItem(item)
        conn.close()

    def mostrar_termos(self, current, previous):
        if not current:
            return
        folha_id = current.data(1000)
        self.lista_termos.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        query = """
        SELECT Termos.id, Termos.numero_termo, Termos.digitalizado, Termos.usuario_modificacao
        FROM Termos
        WHERE Termos.id_folha = %s AND Termos.numero_termo LIKE %s
        """
        cursor.execute(query, (folha_id, '%' + self.termo_search_input.text() + '%',))
        for termo in cursor.fetchall():
            status = "Digitalizado" if termo[2] else "Não Digitalizado"
            item = QListWidgetItem(f"Termo {termo[1]} - {status} (Modificado por: {termo[3] if termo[3] else 'N/A'})")
            item.setData(1000, termo[0])
            self.lista_termos.addItem(item)
        conn.close()

    def marcar_como_digitalizado(self, item):
        termo_id = item.data(1000)
        # Armazenando os índices selecionados antes da atualização
        current_book_index = self.lista_livros.currentRow()
        current_folha_index = self.lista_folhas.currentRow()
        current_termo_index = self.lista_termos.currentRow()

        dialogo = DialogoDigitalizacao(self, termo_id, self.usuario_atual)
        dialogo.exec_()

        # Recarregando todos os dados
        self.carregar_livros()

        # Restaurando a seleção anterior
        if current_book_index != -1:
            self.lista_livros.setCurrentRow(current_book_index)
            self.mostrar_folhas(self.lista_livros.currentItem(), None)
            if current_folha_index != -1:
                self.lista_folhas.setCurrentRow(current_folha_index)
                self.mostrar_termos(self.lista_folhas.currentItem(), None)
                if current_termo_index != -1:
                    self.lista_termos.setCurrentRow(current_termo_index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'sua_senha',
        'database': 'meu_banco'
    }
    window = TelaListarLivros(db_config, "usuario1", "Admin")
    window.show()
    sys.exit(app.exec())
