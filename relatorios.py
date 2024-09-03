import sys
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDateEdit, QComboBox, QListWidget, QListWidgetItem
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QDate
import exportar_planilha

class ModuloRelatorios(QWidget):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Módulo de Relatórios')
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                padding: 5px;
                background: none;
                border: none;
            }               
            QPushButton, QDateEdit, QComboBox {
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

        main_layout = QVBoxLayout(self)

        # Filtros de data e colaborador
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.colaborador_filter = QComboBox()
        self.colaborador_filter.addItem("Todos")
        self.load_colaboradores()
        
        filter_layout.addWidget(QLabel('Data Início:'))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel('Data Fim:'))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(QLabel('Colaborador:'))
        filter_layout.addWidget(self.colaborador_filter)
        main_layout.addLayout(filter_layout)

        # Botões para gerar relatórios
        button_layout = QHBoxLayout()
        self.btn_relatorio_livros = QPushButton('Relatório de Livros')
        self.btn_relatorio_livros.clicked.connect(self.gerar_relatorio_livros)
        self.btn_relatorio_folhas = QPushButton('Relatório de Folhas Digitalizadas')
        self.btn_relatorio_folhas.clicked.connect(self.gerar_relatorio_folhas)
        self.btn_relatorio_termos = QPushButton('Relatório de Termos Digitalizados')
        self.btn_relatorio_termos.clicked.connect(self.gerar_relatorio_termos)
        self.btn_relatorio_livros_concluidos = QPushButton('Relatório de Livros Concluídos')
        self.btn_relatorio_livros_concluidos.clicked.connect(self.gerar_relatorio_livros_concluidos)
        
        button_layout.addWidget(self.btn_relatorio_livros)
        button_layout.addWidget(self.btn_relatorio_folhas)
        button_layout.addWidget(self.btn_relatorio_termos)
        button_layout.addWidget(self.btn_relatorio_livros_concluidos)
        main_layout.addLayout(button_layout)

        # Botão de exportar planilha separado
        export_layout = QHBoxLayout()
        self.btn_exportar_planilha = QPushButton('Exportar Planilha')
        self.btn_exportar_planilha.clicked.connect(self.abrir_tela_exportar)
        export_layout.addWidget(self.btn_exportar_planilha)
        main_layout.addLayout(export_layout)

        # Lista para exibir os relatórios
        self.lista_relatorios = QListWidget()
        main_layout.addWidget(self.lista_relatorios)

        self.setLayout(main_layout)

    def load_colaboradores(self):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT usuario_modificacao FROM Termos WHERE usuario_modificacao IS NOT NULL")
        colaboradores = cursor.fetchall()
        colaboradores = sorted([colaborador[0] for colaborador in colaboradores])  # Ordenar colaboradores
        for colaborador in colaboradores:
            self.colaborador_filter.addItem(colaborador)
        conn.close()

    def gerar_relatorio_livros(self):
        self.lista_relatorios.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        SELECT t.usuario_modificacao, l.id, l.numero
        FROM Livros l
        JOIN Folhas f ON l.id = f.id_livro
        JOIN Termos t ON f.id = t.id_folha
        WHERE t.data_modificacao BETWEEN %s AND %s
        """
        params = [self.start_date.date().toString("yyyy-MM-dd"), self.end_date.date().toString("yyyy-MM-dd")]

        if self.colaborador_filter.currentText() != "Todos":
            query += " AND t.usuario_modificacao = %s"
            params.append(self.colaborador_filter.currentText())

        query += " GROUP BY l.id, t.usuario_modificacao"
        cursor.execute(query, params)
        
        results = cursor.fetchall()
        if results:
            usuario_livros = {}
            for row in results:
                usuario, livro_id, livro_numero = row
                if usuario not in usuario_livros:
                    usuario_livros[usuario] = []
                usuario_livros[usuario].append(f"Livro ID: {livro_id}, Número: {livro_numero}")

            for usuario, livros in usuario_livros.items():
                self.lista_relatorios.addItem(f"Colaborador: {usuario}, Livros Modificados: {len(livros)}")
                for livro in livros:
                    self.lista_relatorios.addItem(f"    {livro}")
        else:
            self.lista_relatorios.addItem("Nenhum registro encontrado.")

        conn.close()

    def gerar_relatorio_folhas(self):
        self.lista_relatorios.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        SELECT t.usuario_modificacao, f.id, f.numero_folha
        FROM Folhas f
        JOIN Termos t ON f.id = t.id_folha
        WHERE t.data_modificacao BETWEEN %s AND %s AND t.digitalizado = 1
        """
        params = [self.start_date.date().toString("yyyy-MM-dd"), self.end_date.date().toString("yyyy-MM-dd")]

        if self.colaborador_filter.currentText() != "Todos":
            query += " AND t.usuario_modificacao = %s"
            params.append(self.colaborador_filter.currentText())

        query += " GROUP BY f.id, t.usuario_modificacao"
        cursor.execute(query, params)
        
        results = cursor.fetchall()
        if results:
            usuario_folhas = {}
            for row in results:
                usuario, folha_id, numero_folha = row
                if usuario not in usuario_folhas:
                    usuario_folhas[usuario] = []
                usuario_folhas[usuario].append(f"Folha ID: {folha_id}, Número: {numero_folha}")

            for usuario, folhas in usuario_folhas.items():
                self.lista_relatorios.addItem(f"Colaborador: {usuario}, Folhas Digitalizadas: {len(folhas)}")
                for folha in folhas:
                    self.lista_relatorios.addItem(f"    {folha}")
        else:
            self.lista_relatorios.addItem("Nenhum registro encontrado.")

        conn.close()

    def gerar_relatorio_termos(self):
        self.lista_relatorios.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        SELECT usuario_modificacao, id, numero_termo, digitalizado
        FROM Termos
        WHERE data_modificacao BETWEEN %s AND %s AND digitalizado = 1
        """
        params = [self.start_date.date().toString("yyyy-MM-dd"), self.end_date.date().toString("yyyy-MM-dd")]

        if self.colaborador_filter.currentText() != "Todos":
            query += " AND usuario_modificacao = %s"
            params.append(self.colaborador_filter.currentText())

        query += " ORDER BY usuario_modificacao, data_modificacao"
        cursor.execute(query, params)
        
        results = cursor.fetchall()
        if results:
            usuario_termos = {}
            for row in results:
                usuario, termo_id, numero_termo, digitalizado = row
                if usuario not in usuario_termos:
                    usuario_termos[usuario] = []
                usuario_termos[usuario].append(f"Termo ID: {termo_id}, Número: {numero_termo}, Digitalizado: {digitalizado}")

            for usuario, termos in usuario_termos.items():
                self.lista_relatorios.addItem(f"Colaborador: {usuario}, Termos Digitalizados: {len(termos)}")
                for termo in termos:
                    self.lista_relatorios.addItem(f"    {termo}")
        else:
            self.lista_relatorios.addItem("Nenhum registro encontrado.")

        conn.close()

    def gerar_relatorio_livros_concluidos(self):
        self.lista_relatorios.clear()
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        query = """
        SELECT t.usuario_modificacao, l.id, l.numero
        FROM Livros l
        JOIN Folhas f ON l.id = f.id_livro
        JOIN Termos t ON f.id = t.id_folha
        WHERE t.data_modificacao BETWEEN %s AND %s
        GROUP BY l.id, t.usuario_modificacao
        HAVING COUNT(DISTINCT f.id) = SUM(f.digitalizada)
        """
        params = [self.start_date.date().toString("yyyy-MM-dd"), self.end_date.date().toString("yyyy-MM-dd")]

        if self.colaborador_filter.currentText() != "Todos":
            query += " AND t.usuario_modificacao = %s"
            params.append(self.colaborador_filter.currentText())

        cursor.execute(query, params)
        
        results = cursor.fetchall()
        if results:
            usuario_livros_concluidos = {}
            for row in results:
                usuario, livro_id, livro_numero = row
                if usuario not in usuario_livros_concluidos:
                    usuario_livros_concluidos[usuario] = []
                usuario_livros_concluidos[usuario].append(f"Livro ID: {livro_id}, Número: {livro_numero}")

            for usuario, livros in usuario_livros_concluidos.items():
                self.lista_relatorios.addItem(f"Colaborador: {usuario}, Livros Concluídos: {len(livros)}")
                for livro in livros:
                    self.lista_relatorios.addItem(f"    {livro}")
        else:
            self.lista_relatorios.addItem("Nenhum registro encontrado.")

        conn.close()

    def abrir_tela_exportar(self):
        self.tela_exportar = exportar_planilha.TelaExportarPlanilha(self.db_config)
        self.tela_exportar.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'sua_senha',
        'database': 'meu_banco'
    }
    window = ModuloRelatorios(db_config)
    window.show()
    sys.exit(app.exec())
